"""
Connects Backend to the ML module (Step 8 of the build order).

Real contract, as implemented by the ML engineer's service (app.py / src/predict.py):

    POST {ML_SERVICE_URL}/analyze
    body: {"clause_text": "<one clause of policy text>"}
    ->  {
            "clause": str,
            "detected_categories": [str, ...],
            "category_confidences": {category: float, ...},
            "risk_score": int,          # 0-100, HIGHER = riskier
            "risk_level": "High"|"Medium"|"Low",
            "flags_count": int,
            "mode": str
        }

Their service scores ONE clause per call and does not do summarization,
tracker detection, or recommendations. So this module:
  1. Splits the scraped policy text into clause-sized chunks.
  2. Calls their /analyze endpoint once per clause.
  3. Aggregates the per-clause results into the shape the rest of Backend
     (models.Report, schemas.ReportOut) and Frontend already expect:
     {score, flagged_clauses, summary, trackers, recommendations}.

Two integration modes are supported:
1. ML_SERVICE_URL is set  -> call the real service as above.
2. ML_SERVICE_URL is empty -> fall back to a local stub (`_local_stub_analyze`)
   so the rest of the backend can still be developed/tested without the
   ML service running.
"""
import re
from typing import Any, Dict, List

import requests

from app.config import settings

# Cap how many clauses we send per scan so a huge policy doesn't turn into
# hundreds of sequential HTTP calls.
MAX_CLAUSES = 40


class MLServiceError(Exception):
    pass


def _split_into_clauses(policy_text: str) -> List[str]:
    """
    The ML service classifies one clause at a time, so break the scraped
    policy text into sentence/paragraph-sized pieces before sending it.
    """
    raw_pieces = re.split(r"(?<=[.!?])\s+|\n+", policy_text)
    clauses = [p.strip() for p in raw_pieces if len(p.strip()) > 25]
    return clauses[:MAX_CLAUSES]


def _call_ml_service(clause_text: str) -> Dict[str, Any]:
    resp = requests.post(
        f"{settings.ml_service_url.rstrip('/')}/analyze",
        json={"clause_text": clause_text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _aggregate(clause_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Roll per-clause risk results up into one report-level payload."""
    if not clause_results:
        return {
            "score": 100,
            "flagged_clauses": [],
            "summary": "No analyzable clauses were found in the scraped policy text.",
            "trackers": [],
            "recommendations": [],
        }

    risk_scores = [r.get("risk_score", 0) for r in clause_results]
    avg_risk = sum(risk_scores) / len(risk_scores)
    # ML's risk_score is "higher = riskier"; Backend/Frontend's score is
    # "higher = more privacy-friendly" (starts at 100). Invert it here.
    privacy_score = max(0, min(100, round(100 - avg_risk)))

    flagged_clauses = []
    level_counts = {"High": 0, "Medium": 0, "Low": 0}
    for r in clause_results:
        level = r.get("risk_level", "Low")
        level_counts[level] = level_counts.get(level, 0) + 1
        if level in ("High", "Medium"):
            categories = r.get("detected_categories") or ["Other"]
            flagged_clauses.append({
                "category": categories[0],
                "risk": level.lower(),
                "text": r.get("clause", "")[:300],
            })

    summary = (
        f"Analyzed {len(clause_results)} clauses: {level_counts.get('High', 0)} high-risk, "
        f"{level_counts.get('Medium', 0)} medium-risk, {level_counts.get('Low', 0)} low-risk. "
        f"Overall privacy score: {privacy_score}/100."
    )

    flagged_categories = {c["category"] for c in flagged_clauses}
    recommendations = []
    if "Third Party Sharing/Change" in flagged_categories:
        recommendations.append("Check whether you can opt out of third-party data sharing.")
    if "Data Retention" in flagged_categories:
        recommendations.append("Look for a data deletion or account-closure request option.")
    if "Policy Change" in flagged_categories:
        recommendations.append(
            "Watch for policy-update notifications, since terms may change without notice."
        )
    if not recommendations:
        recommendations.append("No major red flags detected in this policy's flagged clauses.")

    return {
        "score": privacy_score,
        "flagged_clauses": flagged_clauses,
        # NOTE: the ML service doesn't generate a plain-English summary
        # (no BART step in their code), so this is a rule-based rollup
        # rather than a true summarization. Swap in a real summary here if
        # they add a /summarize endpoint later.
        "summary": summary,
        # NOTE: tracker/cookie detection isn't implemented on the ML side
        # either — this stays empty until that piece exists somewhere.
        "trackers": [],
        "recommendations": recommendations,
    }


def _local_stub_analyze(policy_text: str) -> Dict[str, Any]:
    """Fallback used only when ML_SERVICE_URL is unset (local dev without the ML service running)."""
    length = len(policy_text)
    flagged = []
    if "third part" in policy_text.lower() or "third-party" in policy_text.lower():
        flagged.append({"category": "Third Party Sharing/Change", "risk": "high",
                         "text": "Policy text mentions sharing data with third parties."})
    if "retain" in policy_text.lower() or "retention" in policy_text.lower():
        flagged.append({"category": "Data Retention", "risk": "medium",
                         "text": "Policy text discusses data retention terms."})

    score = max(0, 100 - 15 * len(flagged))
    return {
        "score": score,
        "flagged_clauses": flagged,
        "summary": (
            f"Placeholder summary generated without the ML service running "
            f"({length} characters of policy text were analyzed)."
        ),
        "trackers": [],
        "recommendations": [
            "Set ML_SERVICE_URL and start the ML service for real scoring."
        ],
    }


def analyze_policy_text(policy_text: str) -> Dict[str, Any]:
    """Main entry point used by the /scan background task."""
    if not settings.ml_service_url:
        return _local_stub_analyze(policy_text)

    clauses = _split_into_clauses(policy_text)
    results = []
    try:
        for clause in clauses:
            results.append(_call_ml_service(clause))
    except requests.RequestException as exc:
        raise MLServiceError(f"ML service call failed: {exc}") from exc

    return _aggregate(results)
