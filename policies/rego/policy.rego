package policy

import rego.v1

# ========================================
# EXTRACTED POLICY RULES
# ========================================

# PII-PII-01: Full name is a direct identifier and must be flagged.
rule_PII_PII_01 if {
    object.get(input, "customer_name", "") != ""
}

# PII-PII-02: A personal email address must be flagged.
rule_PII_PII_02 if {
    object.get(input, "email", "") != ""
}

# PII-PII-03: A phone or mobile number must be flagged.
rule_PII_PII_03 if {
    object.get(input, "phone", "") != ""
}

# PII-PII-04: A postal or home address must be flagged.
rule_PII_PII_04 if {
    object.get(input, "address", "") != ""
}

# PII-PII-05: A National Insurance number must be blocked until removed or approved.
rule_PII_PII_05 if {
    object.get(input, "ni_number", "") != ""
}

# PII-PII-06: A passport number must be blocked until removed or approved.
rule_PII_PII_06 if {
    object.get(input, "passport_number", "") != ""
}

# PII-PII-07: A driving licence number must be blocked until removed or approved.
rule_PII_PII_07 if {
    false
}

# PII-PII-08: A bank account or payment card number must be blocked until removed or approved.
rule_PII_PII_08 if {
    object.get(input, "bank_account", "") != ""
}

rule_PII_PII_08 if {
    object.get(input, "credit_card_number", "") != ""
}

# PII-PII-09: An online identifier that is linkable to a person must be flagged.
rule_PII_PII_09 if {
    object.get(input, "ip_address", "") != ""
}

# SPII-SPII-01: Health or medical information must be blocked.
rule_SPII_SPII_01 if {
    object.get(input, "medical_condition", "") != ""
}

# SPII-SPII-02: Ethnicity or racial origin must be blocked.
rule_SPII_SPII_02 if {
    object.get(input, "ethnicity", "") != ""
}

# SPII-SPII-03: Religion or belief must be blocked.
rule_SPII_SPII_03 if {
    object.get(input, "religion", "") != ""
}

# SPII-SPII-04: Political opinion must be blocked.
rule_SPII_SPII_04 if {
    object.get(input, "political_view", "") != ""
}

# SPII-SPII-05: Trade union membership must be blocked.
rule_SPII_SPII_05 if {
    false
}

# SPII-SPII-06: Biometric or genetic data must be blocked.
rule_SPII_SPII_06 if {
    false
}

# CPII-CPII-01: Full name combined with date of birth must be flagged.
rule_CPII_CPII_01 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "dob", "") != ""
}

# CPII-CPII-02: Full name combined with a postal address or postcode must be flagged.
rule_CPII_CPII_02 if {
    false
}

# CPII-CPII-03: Full name combined with a phone number must be flagged.
rule_CPII_CPII_03 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "phone", "") != ""
}

# CPII-CPII-04: Full name combined with a personal email address must be flagged.
rule_CPII_CPII_04 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "email", "") != ""
}

# CPII-CPII-05: Date of birth combined with postcode and gender must be flagged.
rule_CPII_CPII_05 if {
    false
}

# CPII-CPII-06: Employee ID, department, and role must be flagged when linkable to a person.
rule_CPII_CPII_06 if {
    object.get(input, "employee_id", "") != ""
    object.get(input, "department", "") != ""
    object.get(input, "job_role", "") != ""
}

# CPII-CPII-07: Customer ID combined with account event details must be flagged when the customer can be re-identified.
rule_CPII_CPII_07 if {
    false
}

# CPII-CPII-08: Free-text comments containing personal identifiers must be flagged.
rule_CPII_CPII_08 if {
    false
}

# ========================================
# TRIGGERED RULES
# ========================================

triggered_rules contains {
    "rule_id": "PII-PII-01",
    "category": "PII",
    "description": "Full name is a direct identifier and must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy identifies full name as a direct identifier requiring the record to be flagged.",
    "remediation": "Flag the record."
} if rule_PII_PII_01

triggered_rules contains {
    "rule_id": "PII-PII-02",
    "category": "PII",
    "description": "A personal email address must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy identifies personal email addresses as direct identifiers requiring the record to be flagged.",
    "remediation": "Flag the record."
} if rule_PII_PII_02

triggered_rules contains {
    "rule_id": "PII-PII-03",
    "category": "PII",
    "description": "A phone or mobile number must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy identifies phone and mobile numbers as direct identifiers requiring the record to be flagged.",
    "remediation": "Flag the record."
} if rule_PII_PII_03

triggered_rules contains {
    "rule_id": "PII-PII-04",
    "category": "PII",
    "description": "A postal or home address must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy identifies postal and home addresses as direct identifiers requiring the record to be flagged.",
    "remediation": "Flag the record."
} if rule_PII_PII_04

triggered_rules contains {
    "rule_id": "PII-PII-05",
    "category": "PII",
    "description": "A National Insurance number must be blocked until removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing a National Insurance number to be blocked until removal or approval.",
    "remediation": "Remove the National Insurance number or obtain approval before allowing the record."
} if rule_PII_PII_05

triggered_rules contains {
    "rule_id": "PII-PII-06",
    "category": "PII",
    "description": "A passport number must be blocked until removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing a passport number to be blocked until removal or approval.",
    "remediation": "Remove the passport number or obtain approval before allowing the record."
} if rule_PII_PII_06

triggered_rules contains {
    "rule_id": "PII-PII-07",
    "category": "PII",
    "description": "A driving licence number must be blocked until removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing a driving licence number to be blocked until removal or approval, but no matching dataset column is available.",
    "remediation": "Remove the driving licence number or obtain approval before allowing the record."
} if rule_PII_PII_07

triggered_rules contains {
    "rule_id": "PII-PII-08",
    "category": "PII",
    "description": "A bank account or payment card number must be blocked until removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing a bank account or payment card number to be blocked until removal or approval.",
    "remediation": "Remove the bank account or payment card number, or obtain approval before allowing the record."
} if rule_PII_PII_08

triggered_rules contains {
    "rule_id": "PII-PII-09",
    "category": "PII",
    "description": "An online identifier that is linkable to a person must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy identifies IP addresses and other online identifiers as PII when they are linkable to a person.",
    "remediation": "Flag the record."
} if rule_PII_PII_09

triggered_rules contains {
    "rule_id": "SPII-SPII-01",
    "category": "SPII",
    "description": "Health or medical information must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing health or medical information to be blocked.",
    "remediation": "Block the record."
} if rule_SPII_SPII_01

triggered_rules contains {
    "rule_id": "SPII-SPII-02",
    "category": "SPII",
    "description": "Ethnicity or racial origin must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing ethnicity or racial-origin information to be blocked.",
    "remediation": "Block the record."
} if rule_SPII_SPII_02

triggered_rules contains {
    "rule_id": "SPII-SPII-03",
    "category": "SPII",
    "description": "Religion or belief must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing religion or belief information to be blocked.",
    "remediation": "Block the record."
} if rule_SPII_SPII_03

triggered_rules contains {
    "rule_id": "SPII-SPII-04",
    "category": "SPII",
    "description": "Political opinion must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing political opinion to be blocked.",
    "remediation": "Block the record."
} if rule_SPII_SPII_04

triggered_rules contains {
    "rule_id": "SPII-SPII-05",
    "category": "SPII",
    "description": "Trade union membership must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing trade union membership information to be blocked, but no matching dataset column is available.",
    "remediation": "Block the record."
} if rule_SPII_SPII_05

triggered_rules contains {
    "rule_id": "SPII-SPII-06",
    "category": "SPII",
    "description": "Biometric or genetic data must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing biometric or genetic data to be blocked, but no matching dataset column is available.",
    "remediation": "Block the record."
} if rule_SPII_SPII_06

triggered_rules contains {
    "rule_id": "CPII-CPII-01",
    "category": "CPII",
    "description": "Full name combined with date of birth must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of full name and date of birth as an indirect identifier combination.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_01

triggered_rules contains {
    "rule_id": "CPII-CPII-02",
    "category": "CPII",
    "description": "Full name combined with a postal address or postcode must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy defines full name combined with either postal address or postcode as an indirect identifier combination.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_02

triggered_rules contains {
    "rule_id": "CPII-CPII-03",
    "category": "CPII",
    "description": "Full name combined with a phone number must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of full name and phone number as an indirect identifier combination.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_03

triggered_rules contains {
    "rule_id": "CPII-CPII-04",
    "category": "CPII",
    "description": "Full name combined with a personal email address must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of full name and personal email address as an indirect identifier combination.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_04

triggered_rules contains {
    "rule_id": "CPII-CPII-05",
    "category": "CPII",
    "description": "Date of birth combined with postcode and gender must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of date of birth, postcode, and gender as an indirect identifier combination.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_05

triggered_rules contains {
    "rule_id": "CPII-CPII-06",
    "category": "CPII",
    "description": "Employee ID, department, and role must be flagged when linkable to a person.",
    "outcome": "FLAG",
    "explanation": "The policy defines employee ID, department, and role as a combination requiring flagging when linkable to a person.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_06

triggered_rules contains {
    "rule_id": "CPII-CPII-07",
    "category": "CPII",
    "description": "Customer ID combined with account event details must be flagged when the customer can be re-identified.",
    "outcome": "FLAG",
    "explanation": "The policy defines customer ID combined with account event details as a combination requiring flagging when the customer can be re-identified.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_07

triggered_rules contains {
    "rule_id": "CPII-CPII-08",
    "category": "CPII",
    "description": "Free-text comments containing personal identifiers must be flagged.",
    "outcome": "FLAG",
    "explanation": "The policy requires free-text comments containing personal identifiers to be flagged; the feedback column is not used as an executable PII condition.",
    "remediation": "Flag the record."
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
