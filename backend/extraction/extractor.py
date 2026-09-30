import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from config.rule_schema import RULE_SCHEMA
from config.dataset_schema import POLICY_MAPPABLE_COLUMNS
from backend.extraction.prompt import (
    SYSTEM_PROMPT,
    build_user_prompt,
)
from backend.extraction.validator import validate_rules


load_dotenv()


MODEL_NAME = "gpt-5.6-luna"


def extract_rules(policy_text: str) -> dict:
    """
    Extract PII, SPII and CPII rules from policy text
    using OpenAI, then validate the extracted result.
    """

    # ========================================================
    # API KEY
    # ========================================================

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set."
        )

    client = OpenAI(
        api_key=api_key
    )

    # ========================================================
    # BUILD PROMPT
    # ========================================================

    user_prompt = build_user_prompt(
        policy_text=policy_text,
        dataset_columns=POLICY_MAPPABLE_COLUMNS,
    )

    # ========================================================
    # EXTRACTION LOG
    # ========================================================

    print("=" * 60)
    print("OPENAI POLICY RULE EXTRACTION")
    print("=" * 60)

    print(
        f"Model: {MODEL_NAME}"
    )

    print(
        f"Policy characters: {len(policy_text)}"
    )

    print(
        f"Dataset columns: {len(POLICY_MAPPABLE_COLUMNS)}"
    )

    print(
        "Sending extraction request..."
    )

    # ========================================================
    # OPENAI REQUEST
    # ========================================================

    response = client.responses.create(
        model=MODEL_NAME,
        instructions=SYSTEM_PROMPT,
        input=user_prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "policy_rules",
                "schema": RULE_SCHEMA,
                "strict": True,
            }
        },
    )

    # ========================================================
    # PARSE RESPONSE
    # ========================================================

    print(
        "OpenAI response received."
    )

    result = json.loads(
        response.output_text
    )

    print(
        f"Rules extracted: "
        f"{len(result.get('rules', []))}"
    )

    # ========================================================
    # VALIDATE
    # ========================================================

    print(
        "Validating extracted rules..."
    )

    validate_rules(result)

    print(
        "Rule validation: PASSED"
    )

    print("=" * 60)

    return result