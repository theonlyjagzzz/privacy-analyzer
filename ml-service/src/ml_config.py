# src/ml_config.py

# Per-class calibrated probability thresholds
# Lower thresholds on sparse classes allow the model to trigger without relying solely on rules
CLASS_THRESHOLDS = {
    "First Party Collection/Use": 0.15,
    "Third Party Sharing/Change": 0.03,
    "User Choice/Control": 0.04,
    "User Access, Edit and Deletion": 0.04,
    "Data Retention": 0.03,
    "Data Security": 0.05,
    "Policy Change": 0.04,
    "International and Specific Audiences": 0.05,
    "Do Not Track": 0.05,
    "Other": 0.10
}