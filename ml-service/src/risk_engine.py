import re

HIGH_RISK_PATTERNS = [
    r"\b(share|sell|transfer|disclose)\b.*?\b(third parties|affiliates|partners|vendors)\b",
    r"\b(location|biometric|financial|credit card|social security)\b",
    r"\b(retain|store)\b.*?\b(indefinitely|permanently)\b",
    r"\b(change|modify)\b.*?\b(without notice|at any time)\b"
]

CATEGORY_BASE_WEIGHTS = {
    "First Party Collection/Use": 10,
    "Third Party Sharing/Change": 25,
    "User Choice/Control": 15,
    "User Access, Edit and Deletion": 10,
    "Data Retention": 20,
    "Data Security": 5,
    "Policy Change": 15,
    "International and Specific Audiences": 10,
    "Do Not Track": 15,
    "Other": 0
}

def calculate_clause_risk(clause_text: str, predicted_categories: list) -> dict:
    if not predicted_categories:
        return {"score": 0, "level": "Low", "flags_count": 0}

    base_score = sum(CATEGORY_BASE_WEIGHTS.get(cat, 5) for cat in predicted_categories)
    
    flags = []
    multiplier = 1.0
    
    for pattern in HIGH_RISK_PATTERNS:
        if re.search(pattern, clause_text, re.IGNORECASE):
            multiplier += 0.25
            flags.append(pattern)

    raw_score = base_score * multiplier
    final_score = min(int(raw_score), 100)

    if final_score >= 65:
        level = "High"
    elif final_score >= 35:
        level = "Medium"
    else:
        level = "Low"

    return {
        "score": final_score,
        "level": level,
        "flags_count": len(flags)
    }

if __name__ == "__main__":
    test_clause = "We may sell or share your location and financial data with third parties indefinitely without notice."
    test_cats = ["Third Party Sharing/Change", "Data Retention"]
    result = calculate_clause_risk(test_clause, test_cats)
    print(f"Test Clause Risk Analysis: {result}")