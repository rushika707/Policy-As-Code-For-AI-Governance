package policy

import rego.v1

# ========================================
# EXTRACTED POLICY RULES
# ========================================

# PII-PII-01: Full name is a direct identifier and must trigger a flag.
rule_PII_PII_01 if {
    object.get(input, "customer_name", "") != ""
}

# PII-PII-02: Personal email address is a direct identifier and must trigger a flag.
rule_PII_PII_02 if {
    object.get(input, "email", "") != ""
}

# PII-PII-03: Telephone number is a direct identifier and must trigger a flag.
rule_PII_PII_03 if {
    object.get(input, "phone", "") != ""
}

# PII-PII-04: Residential address is a direct identifier and must trigger a flag.
rule_PII_PII_04 if {
    object.get(input, "address", "") != ""
}

# PII-PII-05: National identity number is prohibited unless removed or approved.
rule_PII_PII_05 if {
    false
}

# PII-PII-06: Passport identifier is prohibited unless removed or approved.
rule_PII_PII_06 if {
    object.get(input, "passport_number", "") != ""
}

# PII-PII-07: Driving licence identifier is prohibited unless removed or approved.
rule_PII_PII_07 if {
    false
}

# PII-PII-08: Financial account details are prohibited unless removed or approved.
rule_PII_PII_08 if {
    false
}

# PII-PII-09: Persistent online identifiers must trigger a flag.
rule_PII_PII_09 if {
    false
}

# SPII-SPII-01: Medical information must be blocked.
rule_SPII_SPII_01 if {
    object.get(input, "medical_condition", "") != ""
}

# SPII-SPII-02: Racial or ethnic information must be blocked.
rule_SPII_SPII_02 if {
    object.get(input, "ethnicity", "") != ""
}

# SPII-SPII-03: Religious information must be blocked.
rule_SPII_SPII_03 if {
    object.get(input, "religion", "") != ""
}

# SPII-SPII-04: Political affiliation or views must be blocked.
rule_SPII_SPII_04 if {
    object.get(input, "political_view", "") != ""
}

# SPII-SPII-05: Union membership must be blocked.
rule_SPII_SPII_05 if {
    false
}

# SPII-SPII-06: Biometric or genetic information must be blocked.
rule_SPII_SPII_06 if {
    false
}

# CPII-CPII-01: A full name combined with birth date is an indirect identifier and must trigger a flag.
rule_CPII_CPII_01 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "dob", "") != ""
}

# CPII-CPII-02: A full name combined with residential address must trigger a flag.
rule_CPII_CPII_02 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "address", "") != ""
}

# CPII-CPII-03: A full name combined with telephone number must trigger a flag.
rule_CPII_CPII_03 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "phone", "") != ""
}

# CPII-CPII-04: A full name combined with personal email must trigger a flag.
rule_CPII_CPII_04 if {
    object.get(input, "customer_name", "") != ""
    object.get(input, "email", "") != ""
}

# CPII-CPII-05: Birth date, postcode, and sex together must trigger a flag.
rule_CPII_CPII_05 if {
    false
}

# CPII-CPII-06: Staff ID, team, and job title must trigger a flag where a person can be identified.
rule_CPII_CPII_06 if {
    object.get(input, "employee_id", "") != ""
    object.get(input, "department", "") != ""
    object.get(input, "job_role", "") != ""
}

# CPII-CPII-07: Customer reference combined with transaction details enabling re-identification must trigger a flag.
rule_CPII_CPII_07 if {
    false
}

# CPII-CPII-08: Free-text notes containing identifiable personal details must trigger a flag.
rule_CPII_CPII_08 if {
    false
}

# ========================================
# TRIGGERED RULES
# ========================================

triggered_rules contains {
    "rule_id": "PII-PII-01",
    "category": "PII",
    "description": "Full name is a direct identifier and must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy identifies full name as a direct identifier.",
    "remediation": "Flag the record."
} if rule_PII_PII_01

triggered_rules contains {
    "rule_id": "PII-PII-02",
    "category": "PII",
    "description": "Personal email address is a direct identifier and must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy identifies personal email address as a direct identifier.",
    "remediation": "Flag the record."
} if rule_PII_PII_02

triggered_rules contains {
    "rule_id": "PII-PII-03",
    "category": "PII",
    "description": "Telephone number is a direct identifier and must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy identifies telephone number as a direct identifier.",
    "remediation": "Flag the record."
} if rule_PII_PII_03

triggered_rules contains {
    "rule_id": "PII-PII-04",
    "category": "PII",
    "description": "Residential address is a direct identifier and must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy identifies residential address as a direct identifier.",
    "remediation": "Flag the record."
} if rule_PII_PII_04

triggered_rules contains {
    "rule_id": "PII-PII-05",
    "category": "PII",
    "description": "National identity number is prohibited unless removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing a national identity number to be blocked until removal or approval.",
    "remediation": "Remove the national identity number or obtain approval before allowing the record."
} if rule_PII_PII_05

triggered_rules contains {
    "rule_id": "PII-PII-06",
    "category": "PII",
    "description": "Passport identifier is prohibited unless removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing a passport identifier to be blocked until removal or approval.",
    "remediation": "Remove the passport identifier or obtain approval before allowing the record."
} if rule_PII_PII_06

triggered_rules contains {
    "rule_id": "PII-PII-07",
    "category": "PII",
    "description": "Driving licence identifier is prohibited unless removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing a driving licence identifier to be blocked until removal or approval.",
    "remediation": "Remove the driving licence identifier or obtain approval before allowing the record."
} if rule_PII_PII_07

triggered_rules contains {
    "rule_id": "PII-PII-08",
    "category": "PII",
    "description": "Financial account details are prohibited unless removed or approved.",
    "outcome": "BLOCK",
    "explanation": "The policy requires records containing financial account details to be blocked until removal or approval.",
    "remediation": "Remove the financial account details or obtain approval before allowing the record."
} if rule_PII_PII_08

triggered_rules contains {
    "rule_id": "PII-PII-09",
    "category": "PII",
    "description": "Persistent online identifiers must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy identifies persistent online identifiers as direct identifiers requiring a flag.",
    "remediation": "Flag the record."
} if rule_PII_PII_09

triggered_rules contains {
    "rule_id": "SPII-SPII-01",
    "category": "SPII",
    "description": "Medical information must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy classifies medical information as sensitive personal data.",
    "remediation": "Block the record."
} if rule_SPII_SPII_01

triggered_rules contains {
    "rule_id": "SPII-SPII-02",
    "category": "SPII",
    "description": "Racial or ethnic information must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy classifies racial or ethnic information as sensitive personal data.",
    "remediation": "Block the record."
} if rule_SPII_SPII_02

triggered_rules contains {
    "rule_id": "SPII-SPII-03",
    "category": "SPII",
    "description": "Religious information must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy classifies religious information as sensitive personal data.",
    "remediation": "Block the record."
} if rule_SPII_SPII_03

triggered_rules contains {
    "rule_id": "SPII-SPII-04",
    "category": "SPII",
    "description": "Political affiliation or views must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy classifies political affiliation or views as sensitive personal data.",
    "remediation": "Block the record."
} if rule_SPII_SPII_04

triggered_rules contains {
    "rule_id": "SPII-SPII-05",
    "category": "SPII",
    "description": "Union membership must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy classifies union membership as sensitive personal data.",
    "remediation": "Block the record."
} if rule_SPII_SPII_05

triggered_rules contains {
    "rule_id": "SPII-SPII-06",
    "category": "SPII",
    "description": "Biometric or genetic information must be blocked.",
    "outcome": "BLOCK",
    "explanation": "The policy classifies biometric or genetic information as sensitive personal data.",
    "remediation": "Block the record."
} if rule_SPII_SPII_06

triggered_rules contains {
    "rule_id": "CPII-CPII-01",
    "category": "CPII",
    "description": "A full name combined with birth date is an indirect identifier and must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of full name and birth date as an indirect identifier.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_01

triggered_rules contains {
    "rule_id": "CPII-CPII-02",
    "category": "CPII",
    "description": "A full name combined with residential address must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of full name and residential address as an indirect identifier.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_02

triggered_rules contains {
    "rule_id": "CPII-CPII-03",
    "category": "CPII",
    "description": "A full name combined with telephone number must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of full name and telephone number as an indirect identifier.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_03

triggered_rules contains {
    "rule_id": "CPII-CPII-04",
    "category": "CPII",
    "description": "A full name combined with personal email must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of full name and personal email as an indirect identifier.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_04

triggered_rules contains {
    "rule_id": "CPII-CPII-05",
    "category": "CPII",
    "description": "Birth date, postcode, and sex together must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy defines the combination of birth date, postcode, and sex as an indirect identifier.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_05

triggered_rules contains {
    "rule_id": "CPII-CPII-06",
    "category": "CPII",
    "description": "Staff ID, team, and job title must trigger a flag where a person can be identified.",
    "outcome": "FLAG",
    "explanation": "The policy defines staff ID, team, and job title as a combination rule when a person can be identified.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_06

triggered_rules contains {
    "rule_id": "CPII-CPII-07",
    "category": "CPII",
    "description": "Customer reference combined with transaction details enabling re-identification must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy defines customer reference and transaction details enabling re-identification as an indirect identifier combination.",
    "remediation": "Flag the record."
} if rule_CPII_CPII_07

triggered_rules contains {
    "rule_id": "CPII-CPII-08",
    "category": "CPII",
    "description": "Free-text notes containing identifiable personal details must trigger a flag.",
    "outcome": "FLAG",
    "explanation": "The policy requires a flag for free-text notes containing identifiable personal details.",
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
