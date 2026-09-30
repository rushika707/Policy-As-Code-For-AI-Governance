import json
import math
import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "policy_runs.db"


def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def clean_value(value):
    if isinstance(value, float) and math.isnan(value):
        return None

    return value


def clean_record(record):
    if isinstance(record, dict):
        return {
            key: clean_record(value)
            for key, value in record.items()
        }

    if isinstance(record, list):
        return [
            clean_record(value)
            for value in record
        ]

    return clean_value(record)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_number INTEGER NOT NULL,
            run_date TEXT NOT NULL,
            policy_name TEXT,
            dataset_name TEXT NOT NULL,
            total_records INTEGER NOT NULL,
            pass_count INTEGER NOT NULL,
            flag_count INTEGER NOT NULL,
            block_count INTEGER NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS run_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            record_id TEXT NOT NULL,
            record_data TEXT NOT NULL,
            outcome TEXT NOT NULL,
            triggered_rules TEXT,
            reason TEXT,
            remediation TEXT,
            FOREIGN KEY(run_id)
                REFERENCES runs(id)
                ON DELETE CASCADE
        )
        """
    )

    connection.commit()
    connection.close()


def save_run(
    records,
    dataset_name,
    policy_name=None,
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COALESCE(MAX(run_number), 0) + 1
        FROM runs
        """
    )

    run_number = cursor.fetchone()[0]

    total_records = len(records)

    pass_count = sum(
        1 for record in records
        if record.get("outcome") == "PASS"
    )

    flag_count = sum(
        1 for record in records
        if record.get("outcome") == "FLAG"
    )

    block_count = sum(
        1 for record in records
        if record.get("outcome") == "BLOCK"
    )

    run_date = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO runs (
            run_number,
            run_date,
            policy_name,
            dataset_name,
            total_records,
            pass_count,
            flag_count,
            block_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_number,
            run_date,
            policy_name,
            dataset_name,
            total_records,
            pass_count,
            flag_count,
            block_count,
        ),
    )

    run_id = cursor.lastrowid

    for record in records:
        record_data = {
            "record_id": record.get("record_id"),
            **record.get("input", {}),
        }

        triggered_rules = record.get(
            "triggered_rules",
            [],
        )

        reason_list = [
            rule.get("explanation", "")
            for rule in triggered_rules
            if rule.get("explanation")
        ]

        remediation_list = [
            rule.get("remediation", "")
            for rule in triggered_rules
            if rule.get("remediation")
        ]

        cursor.execute(
            """
            INSERT INTO run_records (
                run_id,
                record_id,
                record_data,
                outcome,
                triggered_rules,
                reason,
                remediation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                str(record.get("record_id")),
                json.dumps(
                    clean_record(record_data),
                    ensure_ascii=False,
                ),
                record.get("outcome"),
                json.dumps(
                    clean_record(triggered_rules),
                    ensure_ascii=False,
                ),
                json.dumps(
                    reason_list,
                    ensure_ascii=False,
                ),
                json.dumps(
                    remediation_list,
                    ensure_ascii=False,
                ),
            ),
        )

    connection.commit()
    connection.close()

    return run_id


def get_runs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM runs
        ORDER BY run_number DESC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_run(run_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM runs
        WHERE id = ?
        """,
        (run_id,),
    )

    run_row = cursor.fetchone()

    if run_row is None:
        connection.close()
        return None

    run = dict(run_row)

    cursor.execute(
        """
        SELECT *
        FROM run_records
        WHERE run_id = ?
        ORDER BY id
        """,
        (run_id,),
    )

    record_rows = cursor.fetchall()
    connection.close()

    records = []

    for row in record_rows:
        record = dict(row)

        input_data = json.loads(
            record["record_data"]
        )

        triggered_rules = json.loads(
            record["triggered_rules"] or "[]"
        )

        reasons = json.loads(
            record["reason"] or "[]"
        )

        remediations = json.loads(
            record["remediation"] or "[]"
        )

        records.append(
            {
                "record_id": record["record_id"],
                "outcome": record["outcome"],
                "triggered_rule_ids": [
                    rule.get("rule_id")
                    for rule in triggered_rules
                    if rule.get("rule_id")
                ],
                "triggered_categories": [
                    rule.get("category")
                    for rule in triggered_rules
                    if rule.get("category")
                ],
                "triggered_rules": triggered_rules,
                "input": input_data,
                "reason": reasons,
                "remediation": remediations,
            }
        )

    run["records"] = records

    return run


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {DB_PATH}")