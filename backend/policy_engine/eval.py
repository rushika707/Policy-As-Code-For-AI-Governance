import json
import subprocess
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATASET_PATH = (
    BASE_DIR
    / "synthetic_data"
    / "synthetic_dataset.xlsx"
)

OPA_PATH = (
    BASE_DIR
    / "opa"
    / "opa.exe"
)

REGO_PATH = (
    BASE_DIR
    / "policies"
    / "rego"
    / "policy.rego"
)

RESULTS_DIR = (
    BASE_DIR
    / "evaluation_results"
)

RESULTS_PATH = (
    RESULTS_DIR
    / "results.json"
)


EXPECTED_COLUMNS = [
    "record_id",
    "customer_name",
    "email",
    "phone",
    "address",
    "dob",
    "gender",
    "passport_number",
    "ni_number",
    "credit_card_number",
    "bank_account",
    "medical_condition",
    "ethnicity",
    "religion",
    "political_view",
    "employee_id",
    "department",
    "job_role",
    "customer_id",
    "ip_address",
    "feedback",
]


def validate_paths():
    """
    Make sure all required files exist.
    """

    required_paths = {
        "Dataset": DATASET_PATH,
        "OPA": OPA_PATH,
        "Rego policy": REGO_PATH,
    }

    for name, path in required_paths.items():

        if not path.exists():
            raise FileNotFoundError(
                f"{name} not found: {path}"
            )


def load_dataset():
    """
    Load the synthetic Excel dataset.
    """

    print()
    print("Loading synthetic dataset...")
    print(f"Dataset: {DATASET_PATH}")

    dataframe = pd.read_excel(
        DATASET_PATH
    )

    print(
        f"Rows    : {len(dataframe)}"
    )

    print(
        f"Columns : {len(dataframe.columns)}"
    )

    return dataframe


def validate_dataset_columns(dataframe):
    """
    Verify that the dataset contains exactly the
    expected project columns.
    """

    actual_columns = list(
        dataframe.columns
    )

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in actual_columns
    ]

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in EXPECTED_COLUMNS
    ]

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    if unexpected_columns:
        raise ValueError(
            "Dataset contains unexpected columns: "
            + ", ".join(unexpected_columns)
        )

    print(
        "Dataset column validation: PASSED"
    )


def clean_value(value):
    """
    Convert pandas/Excel values into JSON-safe values.

    Empty Excel cells become empty strings.
    Numeric values that represent whole numbers are converted
    without the unnecessary .0 suffix.
    """

    if pd.isna(value):
        return ""

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    return str(value)


def row_to_input(row):
    """
    Convert one pandas row into the JSON object that
    will be passed to OPA.
    """

    record = {}

    for column in EXPECTED_COLUMNS:

        record[column] = clean_value(
            row[column]
        )

    return record


def evaluate_record(record):
    """
    Evaluate one record using OPA.
    """

    input_json = json.dumps(
        record,
        ensure_ascii=False,
    )

    command = [
        str(OPA_PATH),
        "eval",
        "-d",
        str(REGO_PATH),
        "--stdin-input",
        "--format",
        "json",
        "data.policy.result",
    ]

    process = subprocess.run(
        command,
        input=input_json,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )

    if process.returncode != 0:

        raise RuntimeError(
            "OPA evaluation failed:\n"
            + process.stderr
        )

    output = json.loads(
        process.stdout
    )

    try:
        result = (
            output["result"][0]
            ["expressions"][0]
            ["value"]
        )
    except (
        KeyError,
        IndexError,
        TypeError,
    ) as error:

        raise RuntimeError(
            "Unexpected OPA response:\n"
            + json.dumps(
                output,
                indent=2,
            )
        ) from error

    return result


def build_record_result(record, evaluation):
    """
    Combine the original record information with
    the OPA evaluation result.
    """

    triggered_rules = evaluation.get(
        "triggered_rules",
        [],
    )

    rule_ids = [
        rule["rule_id"]
        for rule in triggered_rules
    ]

    categories = [
        rule["category"]
        for rule in triggered_rules
    ]

    return {
        "record_id": record["record_id"],
        "outcome": evaluation["outcome"],
        "triggered_rule_ids": rule_ids,
        "triggered_categories": categories,
        "triggered_rules": triggered_rules,
        "input": record,
    }


def evaluate_dataset(dataframe):
    """
    Evaluate every dataset record through OPA.
    """

    results = []

    total_records = len(dataframe)

    print()
    print("=" * 60)
    print("STARTING DATASET EVALUATION")
    print("=" * 60)

    for index, (_, row) in enumerate(
        dataframe.iterrows(),
        start=1,
    ):

        record = row_to_input(row)

        evaluation = evaluate_record(
            record
        )

        result = build_record_result(
            record,
            evaluation,
        )

        results.append(result)

        print(
            f"[{index}/{total_records}] "
            f"Record {record['record_id']} "
            f"→ {evaluation['outcome']}"
        )

    return results


def calculate_summary(results):
    """
    Calculate basic PASS / FLAG / BLOCK statistics.
    """

    total = len(results)

    pass_count = sum(
        1
        for result in results
        if result["outcome"] == "PASS"
    )

    flag_count = sum(
        1
        for result in results
        if result["outcome"] == "FLAG"
    )

    block_count = sum(
        1
        for result in results
        if result["outcome"] == "BLOCK"
    )

    pass_rate = (
        (pass_count / total) * 100
        if total
        else 0
    )

    return {
        "total_records": total,
        "pass": pass_count,
        "flag": flag_count,
        "block": block_count,
        "pass_rate": round(
            pass_rate,
            2,
        ),
    }


def save_results(results, summary):
    """
    Save the complete evaluation results.
    """

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "summary": summary,
        "records": results,
    }

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        f"Results saved to: {RESULTS_PATH}"
    )


def main():

    print("=" * 60)
    print("POLICY-AS-CODE DATASET EVALUATOR")
    print("=" * 60)

    # ---------------------------------------------------------
    # Validate project files
    # ---------------------------------------------------------

    print()
    print("Validating required files...")

    validate_paths()

    print(
        "Required file validation: PASSED"
    )

    # ---------------------------------------------------------
    # Load dataset
    # ---------------------------------------------------------

    dataframe = load_dataset()

    # ---------------------------------------------------------
    # Validate columns
    # ---------------------------------------------------------

    print()
    print("Validating dataset columns...")

    validate_dataset_columns(
        dataframe
    )

    # ---------------------------------------------------------
    # Evaluate records
    # ---------------------------------------------------------

    results = evaluate_dataset(
        dataframe
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    summary = calculate_summary(
        results
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    save_results(
        results,
        summary,
    )

    # ---------------------------------------------------------
    # Print summary
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)

    print(
        f"Total records : {summary['total_records']}"
    )

    print(
        f"PASS          : {summary['pass']}"
    )

    print(
        f"FLAG          : {summary['flag']}"
    )

    print(
        f"BLOCK         : {summary['block']}"
    )

    print(
        f"Pass rate     : {summary['pass_rate']}%"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()