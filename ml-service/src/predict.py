import os
import sys
from pathlib import Path

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Handle import of risk_engine from root directory safely across all platforms/subprocesses
try:
    from .risk_engine import calculate_clause_risk
except ModuleNotFoundError:
    try:
        from .risk_engine import calculate_clause_risk
    except (ImportError, ValueError):
        # Force parent directory into sys.path if relative import fails
        PARENT_DIR = str(Path(__file__).resolve().parent.parent)
        if PARENT_DIR not in sys.path:
            sys.path.insert(0, PARENT_DIR)
        from risk_engine import calculate_clause_risk

MODEL_DIR = "models/legal_bert_opp115"

CATEGORIES = [
    "First Party Collection/Use",
    "Third Party Sharing/Change",
    "User Choice/Control",
    "User Access, Edit and Deletion",
    "Data Retention",
    "Data Security",
    "Policy Change",
    "International and Specific Audiences",
    "Do Not Track",
    "Other"
]

# Calibrated per-class threshold mapping
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

class PolicyAnalyzer:
    def __init__(self, model_dir=MODEL_DIR):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_loaded = False

        if os.path.exists(model_dir):
            print(f"[*] Loading fine-tuned Legal-BERT model from '{model_dir}'...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(self.device)
            self.model.eval()
            self.model_loaded = True
        else:
            print("[!] Model directory not found. Running in HEURISTIC PREVIEW mode.")

    def analyze_clause(self, clause_text: str) -> dict:
        detected_categories = []
        confidences = {}

        # 1. Sliding-Window Neural Classification via Legal-BERT
        if self.model_loaded:
            inputs = self.tokenizer(
                clause_text,
                truncation=True,
                max_length=256,
                stride=128,
                return_overflowing_tokens=True,
                return_tensors="pt"
            ).to(self.device)

            inputs.pop("overflow_to_sample_mapping", None)

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.sigmoid(outputs.logits).cpu().numpy()
                
            # Max-pooling across token windows
            pooled_probs = probs.max(axis=0)

            # Apply per-class calibrated thresholds
            for idx, cat_name in enumerate(CATEGORIES):
                prob_val = float(pooled_probs[idx])
                thresh = CLASS_THRESHOLDS.get(cat_name, 0.05)
                if prob_val >= thresh:
                    detected_categories.append(cat_name)
                    confidences[cat_name] = round(prob_val * 100, 2)

        # 2. Safety Net Keyword Ensembling
        lower_text = clause_text.lower()
        if "share" in lower_text or "third part" in lower_text or "sell" in lower_text or "rent" in lower_text:
            if "Third Party Sharing/Change" not in detected_categories:
                detected_categories.append("Third Party Sharing/Change")
                confidences["Third Party Sharing/Change"] = confidences.get("Third Party Sharing/Change", 95.0)
                
        if "collect" in lower_text or "use" in lower_text or "track" in lower_text or "location" in lower_text:
            if "First Party Collection/Use" not in detected_categories:
                detected_categories.append("First Party Collection/Use")
                confidences["First Party Collection/Use"] = confidences.get("First Party Collection/Use", 95.0)
                
        if "retain" in lower_text or "store" in lower_text or "indefinitely" in lower_text:
            if "Data Retention" not in detected_categories:
                detected_categories.append("Data Retention")
                confidences["Data Retention"] = confidences.get("Data Retention", 95.0)
                
        if "modify" in lower_text or "update" in lower_text or "without prior notice" in lower_text:
            if "Policy Change" not in detected_categories:
                detected_categories.append("Policy Change")
                confidences["Policy Change"] = confidences.get("Policy Change", 95.0)

        # Cleanup fallback category
        if "Other" in detected_categories and len(detected_categories) > 1:
            detected_categories.remove("Other")
            confidences.pop("Other", None)
        elif not detected_categories:
            detected_categories.append("Other")
            confidences["Other"] = 50.0

        # 3. Calculate Risk Score & Detailed Explanations
        risk_analysis = calculate_clause_risk(clause_text, detected_categories)

        return {
            "clause": clause_text,
            "detected_categories": detected_categories,
            "category_confidences": confidences,
            "risk_score": risk_analysis["score"],
            "risk_level": risk_analysis["level"],
            "flags_count": risk_analysis["flags_count"],
            "mode": "Legal-BERT Model (Hybrid Calibrated)" if self.model_loaded else "Heuristic Preview"
        }