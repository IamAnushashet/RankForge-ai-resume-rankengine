from __future__ import annotations

import re


TECH_TERMS = [
    "python", "sql", "machine learning", "ml", "ai", "llm", "nlp", "rag",
    "retrieval", "tensorflow", "pytorch", "scikit", "xgboost", "spark",
    "airflow", "mlops", "docker", "kubernetes", "aws", "gcp", "azure",
    "vector", "embedding", "model deployment", "monitoring", "evaluation",
]

NEGATIVE_TERMS = ["marketing", "hr", "consulting", "research only", "sales", "graphic designer"]


def parse_jd(text: str) -> dict:
    text = str(text)
    lower = text.lower()
    must_have = [term for term in TECH_TERMS if term in lower] or TECH_TERMS[:12]
    nice_to_have = [t for t in ["github", "fast response", "production", "cloud", "relocate"] if t in lower]
    negative_signals = [term for term in NEGATIVE_TERMS if term in lower] or NEGATIVE_TERMS

    location = ""
    loc_match = re.search(r"\b(?:location|based in)\s*[:\-]?\s*([A-Za-z ,]+)", text, re.I)
    if loc_match:
        location = loc_match.group(1).strip().splitlines()[0]

    exp = 3.0
    exp_match = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)", lower)
    if exp_match:
        exp = float(exp_match.group(1))

    return {
        "must_have": must_have,
        "nice_to_have": nice_to_have,
        "negative_signals": negative_signals,
        "location": location,
        "experience": exp,
        "raw_text": text,
    }

