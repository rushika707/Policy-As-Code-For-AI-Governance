import json
from pathlib import Path

from backend.extraction.extractor import extract_rules


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

POLICY_TEXT_FILE = (
    BASE_DIR
    / "extracted_text"
    / "AI Training Data PII Policies.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "extracted_text"
    / "rules.json"
)


print("=" * 60)
print("POLICY RULE EXTRACTION TEST")
print("=" * 60)


# ============================================================
# LOAD EXTRACTED POLICY TEXT
# ============================================================

print("\nReading extracted policy text...")

with open(
    POLICY_TEXT_FILE,
    "r",
    encoding="utf-8",
) as file:
    extracted_data = json.load(file)


# ============================================================
# HANDLE EXTRACTED TEXT STRUCTURE
# ============================================================

if isinstance(extracted_data, dict):

    # Expected structure:
    #
    # {
    #     "filename": "...",
    #     "pages": [
    #         {
    #             "page_number": 1,
    #             "text": "..."
    #         }
    #     ]
    # }

    if "pages" in extracted_data:

        pages = extracted_data["pages"]

    else:

        raise ValueError(
            "Extracted JSON is an object, but it does not "
            "contain a 'pages' field."
        )

elif isinstance(extracted_data, list):

    # Also support:
    #
    # [
    #     {
    #         "page_number": 1,
    #         "text": "..."
    #     }
    # ]

    pages = extracted_data

else:

    raise ValueError(
        "Unexpected extracted policy JSON structure."
    )


# ============================================================
# VALIDATE PAGES
# ============================================================

if not isinstance(pages, list):
    raise ValueError(
        "'pages' must be a list."
    )

if not pages:
    raise ValueError(
        "No pages found in extracted policy text."
    )


# ============================================================
# COMBINE PAGE TEXT
# ============================================================

page_texts = []

for page in pages:

    if not isinstance(page, dict):
        raise ValueError(
            "Each page must be a JSON object."
        )

    if "text" not in page:
        raise ValueError(
            "A page is missing the 'text' field."
        )

    page_texts.append(
        page["text"]
    )


policy_text = "\n\n".join(page_texts)


print(
    f"Policy pages loaded: {len(pages)}"
)

print(
    f"Policy text length: "
    f"{len(policy_text)} characters"
)


# ============================================================
# EXTRACT RULES
# ============================================================

print("\nExtracting rules...\n")

result = extract_rules(policy_text)


# ============================================================
# SAVE RULES
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        result,
        file,
        indent=2,
        ensure_ascii=False,
    )


# ============================================================
# SUMMARY
# ============================================================

rules = result.get("rules", [])


print("\n" + "=" * 60)
print("EXTRACTION COMPLETE")
print("=" * 60)

print(
    f"Total rules extracted: {len(rules)}"
)


# ============================================================
# CATEGORY SUMMARY
# ============================================================

category_counts = {
    "PII": 0,
    "SPII": 0,
    "CPII": 0,
}

outcome_counts = {
    "PASS": 0,
    "FLAG": 0,
    "BLOCK": 0,
}


for rule in rules:

    category = rule["category"]
    outcome = rule["outcome"]

    if category in category_counts:
        category_counts[category] += 1

    if outcome in outcome_counts:
        outcome_counts[outcome] += 1


print("\nRules by category:")

for category, count in category_counts.items():

    print(
        f"  {category}: {count}"
    )


print("\nRules by outcome:")

for outcome, count in outcome_counts.items():

    print(
        f"  {outcome}: {count}"
    )


# ============================================================
# RULE IDS
# ============================================================

print("\nExtracted rule IDs:")

for rule in rules:

    print(
        f"  {rule['rule_id']} "
        f"→ {rule['category']} "
        f"→ {rule['outcome']}"
    )


# ============================================================
# ALL RULES CHECK
# ============================================================

print("\n" + "=" * 60)
print("ALL EXTRACTED RULES")
print("=" * 60)

for rule in rules:

    print(
        f"\n{rule['rule_id']}"
        f" | {rule['category']}"
        f" | {rule['outcome']}"
    )

    print(
        f"Description: {rule['description']}"
    )

    print(
        f"Policy terms: {rule['policy_terms']}"
    )

    print(
        f"Dataset columns: {rule['columns']}"
    )

    print(
        "Condition:"
    )

    print(
        json.dumps(
            rule["condition"],
            indent=2,
            ensure_ascii=False,
        )
    )


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 60)
print("RULES SAVED TO:")
print(OUTPUT_FILE)
print("=" * 60)