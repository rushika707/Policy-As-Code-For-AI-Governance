package policy

# FLAG:
# Customer name + email are present
flag if {
    input.customer_name != ""
    input.email != ""
}

# BLOCK:
# Bank account OR credit card is present
block if {
    input.bank_account != ""
}

block if {
    input.credit_card_number != ""
}

# PASS:
# No FLAG or BLOCK condition applies
pass if {
    not flag
    not block
}