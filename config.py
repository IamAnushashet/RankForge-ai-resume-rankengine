from __future__ import annotations

DEFAULT_JD = """
AI Engineer / Machine Learning Engineer role focused on production ML systems,
LLMs, NLP, retrieval, model deployment, data pipelines, Python, SQL, MLOps,
vector databases, cloud, evaluation, monitoring, and cross-functional delivery.
Prefer hands-on builders with 3+ years experience, strong software engineering,
GitHub activity, fast recruiter response, verified profiles, and availability.
Avoid pure marketing, HR, consulting, research-only, skills-only, or title-mismatched
profiles that mention AI without production evidence.
"""

FINAL_WEIGHTS = {
    "semantic_score": 0.25,
    "retrieval_score": 0.25,
    "production_score": 0.20,
    "career_score": 0.10,
    "behavior_score": 0.10,
    "availability_score": 0.05,
    "trust_score": 0.05,
}

MODEL_NAME = "./models/all-MiniLM-L6-v2"
TOP_K = 100
