from config.dataset_schema import (
    FIXED_DATASET_COLUMNS,
    POLICY_MAPPABLE_COLUMNS,
)


ALLOWED_CATEGORIES = {"PII", "SPII", "CPII"}
ALLOWED_OUTCOMES = {"PASS", "FLAG", "BLOCK"}


def validate_rules(result: dict) -> None:
    """
    Validate the rules produced by the LLM.

    Raises ValueError if the extracted rules violate the
    project's structural or dataset constraints.
    """

    # ---------------------------------------------------------
    # 1. Top-level structure
    # ---------------------------------------------------------

    if not isinstance(result, dict):
        raise ValueError("Extraction result must be a dictionary.")

    if "rules" not in result:
        raise ValueError("Extraction result does not contain 'rules'.")

    rules = result["rules"]

    if not isinstance(rules, list):
        raise ValueError("'rules' must be a list.")

    if not rules:
        raise ValueError("No rules were extracted.")

    # ---------------------------------------------------------
    # 2. Track rule IDs for duplicate detection
    # ---------------------------------------------------------

    seen_rule_ids = set()

    # ---------------------------------------------------------
    # 3. Validate every rule
    # ---------------------------------------------------------

    for index, rule in enumerate(rules, start=1):

        if not isinstance(rule, dict):
            raise ValueError(
                f"Rule #{index} must be an object."
            )

        rule_id = rule.get("rule_id")
        category = rule.get("category")
        outcome = rule.get("outcome")

        # -----------------------------------------------------
        # Rule ID
        # -----------------------------------------------------

        if rule_id is not None:

            if not isinstance(rule_id, str):
                raise ValueError(
                    f"Rule #{index}: rule_id must be a string or null."
                )

            if rule_id in seen_rule_ids:
                raise ValueError(
                    f"Duplicate rule_id detected: {rule_id}"
                )

            seen_rule_ids.add(rule_id)

        # -----------------------------------------------------
        # Category
        # -----------------------------------------------------

        if category not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Rule {rule_id or index}: invalid category "
                f"'{category}'. "
                f"Allowed: {sorted(ALLOWED_CATEGORIES)}"
            )

        # -----------------------------------------------------
        # Outcome
        # -----------------------------------------------------

        if outcome not in ALLOWED_OUTCOMES:
            raise ValueError(
                f"Rule {rule_id or index}: invalid outcome "
                f"'{outcome}'. "
                f"Allowed: {sorted(ALLOWED_OUTCOMES)}"
            )

        # -----------------------------------------------------
        # Required fields
        # -----------------------------------------------------

        required_fields = [
            "description",
            "policy_terms",
            "columns",
            "condition",
            "explanation",
            "remediation",
        ]

        for field in required_fields:
            if field not in rule:
                raise ValueError(
                    f"Rule {rule_id or index}: missing '{field}'."
                )

        # -----------------------------------------------------
        # policy_terms
        # -----------------------------------------------------

        if not isinstance(rule["policy_terms"], list):
            raise ValueError(
                f"Rule {rule_id or index}: policy_terms must be a list."
            )

        for term in rule["policy_terms"]:
            if not isinstance(term, str):
                raise ValueError(
                    f"Rule {rule_id or index}: "
                    "every policy_term must be a string."
                )

        # -----------------------------------------------------
        # Top-level columns
        # -----------------------------------------------------

        columns = rule["columns"]

        if not isinstance(columns, list):
            raise ValueError(
                f"Rule {rule_id or index}: columns must be a list."
            )

        for column in columns:

            if column not in POLICY_MAPPABLE_COLUMNS:
                raise ValueError(
                    f"Rule {rule_id or index}: invalid dataset column "
                    f"'{column}' in top-level columns."
                )

            if column == "record_id":
                raise ValueError(
                    f"Rule {rule_id or index}: record_id cannot "
                    "be used as a policy column."
                )

        # -----------------------------------------------------
        # Condition
        # -----------------------------------------------------

        _validate_condition(
            rule["condition"],
            rule_id or f"rule-{index}",
        )

        # -----------------------------------------------------
        # Verify every condition column is represented in the
        # rule-level columns list.
        # -----------------------------------------------------

        condition_columns = set()

        _collect_condition_columns(
            rule["condition"],
            condition_columns,
        )

        for column in condition_columns:

            if column not in columns:
                raise ValueError(
                    f"Rule {rule_id or index}: condition column "
                    f"'{column}' is missing from top-level columns."
                )

        # -----------------------------------------------------
        # Verify every top-level column actually appears in the
        # condition tree.
        # -----------------------------------------------------

        if set(columns) != condition_columns:
            missing_from_condition = set(columns) - condition_columns

            extra_in_condition = condition_columns - set(columns)

            if missing_from_condition:
                raise ValueError(
                    f"Rule {rule_id or index}: top-level columns "
                    f"not present in condition: "
                    f"{sorted(missing_from_condition)}"
                )

            if extra_in_condition:
                raise ValueError(
                    f"Rule {rule_id or index}: condition contains "
                    f"columns not listed at rule level: "
                    f"{sorted(extra_in_condition)}"
                )


def _validate_condition(condition: dict, rule_id: str) -> None:
    """
    Recursively validate a condition tree.
    """

    if not isinstance(condition, dict):
        raise ValueError(
            f"Rule {rule_id}: condition must be an object."
        )

    operator = condition.get("operator")
    fields = condition.get("fields")

    # ---------------------------------------------------------
    # Operator
    # ---------------------------------------------------------

    if operator not in {"AND", "OR"}:
        raise ValueError(
            f"Rule {rule_id}: invalid condition operator "
            f"'{operator}'."
        )

    # ---------------------------------------------------------
    # Fields
    # ---------------------------------------------------------

    if not isinstance(fields, list):
        raise ValueError(
            f"Rule {rule_id}: condition fields must be a list."
        )

    for field in fields:

        if not isinstance(field, dict):
            raise ValueError(
                f"Rule {rule_id}: every condition field "
                "must be an object."
            )

        if "column" not in field:
            raise ValueError(
                f"Rule {rule_id}: condition field missing 'column'."
            )

        if "policy_term" not in field:
            raise ValueError(
                f"Rule {rule_id}: condition field missing "
                "'policy_term'."
            )

        if "required" not in field:
            raise ValueError(
                f"Rule {rule_id}: condition field missing "
                "'required'."
            )

        if "condition" not in field:
            raise ValueError(
                f"Rule {rule_id}: condition field missing "
                "nested 'condition'."
            )

        column = field["column"]
        policy_term = field["policy_term"]
        required = field["required"]
        nested_condition = field["condition"]

        # -----------------------------------------------------
        # Column validation
        # -----------------------------------------------------

        if column is not None:

            if column not in POLICY_MAPPABLE_COLUMNS:
                raise ValueError(
                    f"Rule {rule_id}: invalid condition column "
                    f"'{column}'."
                )

            if column == "record_id":
                raise ValueError(
                    f"Rule {rule_id}: record_id cannot be used "
                    "inside conditions."
                )

        # -----------------------------------------------------
        # policy_term validation
        # -----------------------------------------------------

        if policy_term is not None:

            if not isinstance(policy_term, str):
                raise ValueError(
                    f"Rule {rule_id}: policy_term must be "
                    "a string or null."
                )

            if not policy_term.strip():
                raise ValueError(
                    f"Rule {rule_id}: policy_term cannot be empty."
                )

        # -----------------------------------------------------
        # Required validation
        # -----------------------------------------------------

        if not isinstance(required, bool):
            raise ValueError(
                f"Rule {rule_id}: required must be boolean."
            )

        # -----------------------------------------------------
        # Nested condition validation
        # -----------------------------------------------------

        _validate_condition(
            nested_condition,
            rule_id,
        )

        # -----------------------------------------------------
        # A leaf condition
        # ---------------------------------------------------------

        is_leaf = (
            len(nested_condition.get("fields", [])) == 0
        )

        if is_leaf:

            # A leaf must represent an actual policy concept.
            if column is None and policy_term is None:
                raise ValueError(
                    f"Rule {rule_id}: leaf condition has both "
                    "'column' and 'policy_term' set to null."
                )

        else:

            # A nested logical group should not itself pretend
            # to represent a dataset field.
            if column is not None:
                raise ValueError(
                    f"Rule {rule_id}: nested condition group "
                    "cannot have a dataset column."
                )

            if policy_term is not None:
                raise ValueError(
                    f"Rule {rule_id}: nested condition group "
                    "cannot have a policy_term."
                )


def _collect_condition_columns(
    condition: dict,
    columns: set,
) -> None:
    """
    Recursively collect all mapped dataset columns from
    a condition tree.
    """

    for field in condition.get("fields", []):

        column = field.get("column")

        if column is not None:
            columns.add(column)

        nested_condition = field.get("condition")

        if nested_condition:
            _collect_condition_columns(
                nested_condition,
                columns,
            )