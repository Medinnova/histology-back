import enum

SUBSCRIPTION_TYPE = (
    (0, "FREE"),
    (1, "FULL"),
    (2, "GROUP"),
    (3, "UNIVERSITY"),
)

TRANSACTION_TYPE = (
    (0, 'refill'),
    (1, 'purchase'),
    (2, 'patient_fee')
)