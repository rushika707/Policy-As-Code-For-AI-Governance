RULE_SCHEMA = {
    "type": "object",
    "properties": {
        "rules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "rule_id": {
                        "type": ["string", "null"]
                    },

                    "category": {
                        "type": "string",
                        "enum": ["PII", "SPII", "CPII"]
                    },

                    "description": {
                        "type": "string"
                    },

                    "policy_terms": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },

                    "columns": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },

                    "condition": {
                        "$ref": "#/$defs/condition"
                    },

                    "outcome": {
                        "type": "string",
                        "enum": ["PASS", "FLAG", "BLOCK"]
                    },

                    "explanation": {
                        "type": "string"
                    },

                    "remediation": {
                        "type": "string"
                    },

                },

                "required": [
                    "rule_id",
                    "category",
                    "description",
                    "policy_terms",
                    "columns",
                    "condition",
                    "outcome",
                    "explanation",
                    "remediation"
                ],

                "additionalProperties": False
            }
        }
    },

    "required": ["rules"],

    "additionalProperties": False,

    "$defs": {
        "condition": {
            "type": "object",

            "properties": {
                "operator": {
                    "type": "string",
                    "enum": ["AND", "OR"]
                },

                "fields": {
                    "type": "array",
                    "items": {
                        "$ref": "#/$defs/condition_field"
                    }
                }
            },

            "required": [
                "operator",
                "fields"
            ],

            "additionalProperties": False
        },

        "condition_field": {
            "type": "object",

            "properties": {
                "column": {
                    "type": ["string", "null"]
                },

                "policy_term": {
                    "type": ["string", "null"]
                },

                "required": {
                    "type": "boolean"
                },

                "condition": {
                    "$ref": "#/$defs/condition"
                }
            },

            "required": [
                "column",
                "policy_term",
                "required",
                "condition"
            ],

            "additionalProperties": False
        }
    }
}