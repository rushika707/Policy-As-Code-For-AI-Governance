package policy

import rego.v1

# ========================================
# EXTRACTED POLICY RULES
# ========================================

# PII-PII-01: Legal names are direct identifiers and require review of the record.
rule_PII_PII_01 if {
    object.get(input, "customer_name", "") != ""
}

# PII-PII-02: Private email addresses require review of the record.
rule_PII_PII_02 if {
    object.get(input, "email", "") != ""
}

# PII-PII-03: Contact numbers require review of the record.
rule_PII_PII_03 if {
    object.get(input, "phone", "") != ""
}

# PII-PII-04: Home location information requires review of the record.
rule_PII_PII_04 if {
    object.get(input, "address", "") != ""
}

# PII-PII-05: Taxpayer identification information is blocked until removed or approved.
rule_PII_PII_05 if {
    false
}

# PII-PII-06: Travel document numbers are blocked until removed or approved.
rule_PII_PII_06 if {
    object.get(input, "passport_number", "") != ""
}

# PII-PII-07: Driver credential numbers are blocked until removed or approved.
rule_PII_PII_07 if {
    false
}

# PII-PII-08: Payment account identifiers, including bank accounts or card numbers, are blocked until removed or approved.
rule_PII_PII_08 if {
    object.get(input, "bank_account", "") != ""
}

rule_PII_PII_08 if {
    object.get(input, "credit_card_number", "") != ""
}

# PII-PII-09: Linkable digital identifiers require review of the record.
rule_PII_PII_09 if {
    object.get(input, "ip_address", "") != ""
}

# SPII-SPII-01: Health status information is blocked.
rule_SPII_SPII_01 if {
    object.get(input, "medical_condition", "") != ""
}

# SPII-SPII-02: Ethnic background information is restricted.
rule_SPII_SPII_02 if {
    object.get(input, "ethnicity", "") != ""
}

# SPII-SPII-03: Faith or religion information is blocked.
rule_SPII_SPII_03 if {
    object.get(input, "religion", "") != ""
}

# SPII-SPII-04: Political preference information is blocked.
rule_SPII_SPII_04 if {
    object.get(input, "political_view", "") != ""
}

# SPII-SPII-05: Labour organisation membership information is restricted.
rule_SPII_SPII_05 if {
    false
}

# SPII-SPII-06: Biometric or DNA data is blocked.
rule_SPII_SPII_06 if {
    false
}

# CPII-CPII-01: A legal name combined with a date of birth requires review.
rule_CPII_CPII_01 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "dob", "") != ""
}

# CPII-CPII-02: A legal name combined with full home location requires review.
rule_CPII_CPII_02 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "address", "") != ""
}

# CPII-CPII-03: A legal name combined with a contact number requires review.
rule_CPII_CPII_03 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "phone", "") != ""
}

# CPII-CPII-04: A legal name combined with a private email requires review.
rule_CPII_CPII_04 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "email", "") != ""
}

# CPII-CPII-05: A date of birth combined with postal code and gender requires review.
rule_CPII_CPII_05 if {
    false
}

# CPII-CPII-06: A worker ID combined with business unit and position requires review where identifiable.
rule_CPII_CPII_06 if {
    object.get(input, "employee_id", "") != ""
    object.get(input, "department", "") != ""
    object.get(input, "job_role", "") != ""
}

# CPII-CPII-07: An account reference combined with purchase history allowing re-identification requires review.
rule_CPII_CPII_07 if {
    false
}

# CPII-CPII-08: Free-form text containing personal identifiers requires review; the fixed feedback column is not used as an executable PII condition.
rule_CPII_CPII_08 if {
    false
}

# ========================================
# TRIGGERED RULES
# ========================================

triggered_rules contains {
    "rule_id": "PII-PII-01",
    "category": "PII",
    "description": "Legal names are direct identifiers and require review of the record.",
    "outcome": "FLAG",
    "explanation": "The policy identifies legal names and their name variants as direct identifiers.",
    "remediation": "Flag the record for review."
} if rule_PII_PII_01

triggered_rules contains {
    "rule_id": "PII-PII-02",
    "category": "PII",
    "description": "Private email addresses require review of the record.",
    "outcome": "FLAG",
    "explanation": "The policy identifies private, regular, and alternate email addresses as direct identifiers.",
    "remediation": "Flag the record for review."
} if rule_PII_PII_02

triggered_rules contains {
    "rule_id": "PII-PII-03",
    "category": "PII",
    "description": "Contact numbers require review of the record.",
    "outcome": "FLAG",
    "explanation": "The policy identifies contact numbers, mobile numbers, and telephone numbers as direct identifiers.",
    "remediation": "Flag the record for review."
} if rule_PII_PII_03

triggered_rules contains {
    "rule_id": "PII-PII-04",
    "category": "PII",
    "description": "Home location information requires review of the record.",
    "outcome": "FLAG",
    "explanation": "The policy identifies home location information, including addresses and related location details, as a direct identifier.",
    "remediation": "Flag the record for review."
} if rule_PII_PII_04

triggered_rules contains {
    "rule_id": "PII-PII-05",
    "category": "PII",
    "description": "Taxpayer identification information is blocked until removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing taxpayer identification information to be blocked until the information is removed or approved.",
    "remediation": "Remove the taxpayer identification information or obtain approval before allowing the record."
} if rule_PII_PII_05

triggered_rules contains {
    "rule_id": "PII-PII-06",
    "category": "PII",
    "description": "Travel document numbers are blocked until removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy identifies passport and travel document numbers as direct identifiers subject to blocking.",
    "remediation": "Remove the travel document number or obtain approval before allowing the record."
} if rule_PII_PII_06

triggered_rules contains {
    "rule_id": "PII-PII-07",
    "category": "PII",
    "description": "Driver credential numbers are blocked until removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy identifies driver and driving-licence credential numbers as direct identifiers.",
    "remediation": "Remove the driver credential number or obtain approval before allowing the record."
} if rule_PII_PII_07

triggered_rules contains {
    "rule_id": "PII-PII-08",
    "category": "PII",
    "description": "Payment account identifiers, including bank accounts or card numbers, are blocked until removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy identifies bank account and card identifiers as payment account identifiers requiring blocking.",
    "remediation": "Remove the payment account identifier or obtain approval before allowing the record."
} if rule_PII_PII_08

triggered_rules contains {
    "rule_id": "PII-PII-09",
    "category": "PII",
    "description": "Linkable digital identifiers require review of the record.",
    "outcome": "FLAG",
    "explanation": "The policy identifies linkable digital identifiers, including IP addresses and related identifiers, as direct identifiers requiring review.",
    "remediation": "Flag the record for review."
} if rule_PII_PII_09

triggered_rules contains {
    "rule_id": "SPII-SPII-01",
    "category": "SPII",
    "description": "Health status information is blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy identifies health status and related medical information as sensitive personal data.",
    "remediation": "Block the record."
} if rule_SPII_SPII_01

triggered_rules contains {
    "rule_id": "SPII-SPII-02",
    "category": "SPII",
    "description": "Ethnic background information is restricted.",
    "outcome": "BLOCK",
    "explanation": "The policy identifies ethnic background and related information as sensitive personal data requiring restriction.",
    "remediation": "Restrict the record."
} if rule_SPII_SPII_02

triggered_rules contains {
    "rule_id": "SPII-SPII-03",
    "category": "SPII",
    "description": "Faith or religion information is blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy identifies religious beliefs, faith, and denomination as sensitive personal data.",
    "remediation": "Block the record."
} if rule_SPII_SPII_03

triggered_rules contains {
    "rule_id": "SPII-SPII-04",
    "category": "SPII",
    "description": "Political preference information is blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy identifies political preference and related political information as sensitive personal data.",
    "remediation": "Block the record."
} if rule_SPII_SPII_04

triggered_rules contains {
    "rule_id": "SPII-SPII-05",
    "category": "SPII",
    "description": "Labour organisation membership information is restricted.",
    "outcome": "BLOCK",
    "explanation": "The policy identifies labour organisation and union membership information as sensitive personal data requiring restriction.",
    "remediation": "Restrict the record."
} if rule_SPII_SPII_05

triggered_rules contains {
    "rule_id": "SPII-SPII-06",
    "category": "SPII",
    "description": "Biometric or DNA data is blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy identifies biometric templates, fingerprints, retina scans, and DNA data as sensitive personal data.",
    "remediation": "Block the record."
} if rule_SPII_SPII_06

triggered_rules contains {
    "rule_id": "CPII-CPII-01",
    "category": "CPII",
    "description": "A legal name combined with a date of birth requires review.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of legal name and date of birth as an indirect identifier.",
    "remediation": "Flag the record for review."
} if rule_CPII_CPII_01

triggered_rules contains {
    "rule_id": "CPII-CPII-02",
    "category": "CPII",
    "description": "A legal name combined with full home location requires review.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of legal name and full home location as an indirect identifier.",
    "remediation": "Flag the record for review."
} if rule_CPII_CPII_02

triggered_rules contains {
    "rule_id": "CPII-CPII-03",
    "category": "CPII",
    "description": "A legal name combined with a contact number requires review.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of legal name and contact number as an indirect identifier.",
    "remediation": "Flag the record for review."
} if rule_CPII_CPII_03

triggered_rules contains {
    "rule_id": "CPII-CPII-04",
    "category": "CPII",
    "description": "A legal name combined with a private email requires review.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of legal name and private email as an indirect identifier.",
    "remediation": "Flag the record for review."
} if rule_CPII_CPII_04

triggered_rules contains {
    "rule_id": "CPII-CPII-05",
    "category": "CPII",
    "description": "A date of birth combined with postal code and gender requires review.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of date of birth, postal code, and gender as an indirect identifier; postal code has no matching dataset column.",
    "remediation": "Flag the record for review."
} if rule_CPII_CPII_05

triggered_rules contains {
    "rule_id": "CPII-CPII-06",
    "category": "CPII",
    "description": "A worker ID combined with business unit and position requires review where identifiable.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of worker ID, business unit, and position as an indirect identifier when identifiable.",
    "remediation": "Flag the record for review."
} if rule_CPII_CPII_06

triggered_rules contains {
    "rule_id": "CPII-CPII-07",
    "category": "CPII",
    "description": "An account reference combined with purchase history allowing re-identification requires review.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of account reference and purchase history as an indirect identifier when it allows re-identification.",
    "remediation": "Flag the record for review."
} if rule_CPII_CPII_07

triggered_rules contains {
    "rule_id": "CPII-CPII-08",
    "category": "CPII",
    "description": "Free-form text containing personal identifiers requires review; the fixed feedback column is not used as an executable PII condition.",
    "outcome": "FLAG",
    "explanation": "The policy requires review when free-form text contains personal identifiers, but the fixed feedback column cannot be treated as a source or presence condition for PII evaluation.",
    "remediation": "Flag the record for review."
} if rule_CPII_CPII_08

# ========================================
# OUTCOME DETECTION
# ========================================

has_block if {
    some rule in triggered_rules
    rule.outcome == "BLOCK"
}

has_flag if {
    some rule in triggered_rules
    rule.outcome == "FLAG"
}

# ========================================
# FINAL DECISION
# ========================================

decision := "BLOCK" if has_block

decision := "FLAG" if {
    not has_block
    has_flag
}

decision := "PASS" if {
    not has_block
    not has_flag
}

# ========================================
# FINAL RESULT
# ========================================

result := {
    "outcome": decision,
    "triggered_rules": [rule |
        some rule in triggered_rules
    ]
}
