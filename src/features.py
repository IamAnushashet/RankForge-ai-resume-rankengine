import numpy as np
import pandas as pd

PRODUCTION_EVIDENCE_TERMS = ["production", "shipped", "launched", "deployed", "serving", "monitoring", "scaling", "latency"]
OWNERSHIP_TERMS = ["owned", "led", "architected", "lead", "senior", "principle", "founding", "ownership"]
RETRIEVAL_EVIDENCE_TERMS = ["retrieval", "search", "rag", "vector database", "elasticsearch", "milvus", "pinecone", "chromadb"]
DEPLOYMENT_EVIDENCE_TERMS = ["deployment", "docker", "kubernetes", "k8s", "aws", "gcp", "azure", "terraform", "github actions", "ci/cd"]
STARTUP_FIT_TERMS = ["startup", "fast-paced", "ambiguous", "seed", "series", "zero to one"]
RANKING_EVIDENCE_TERMS = ["ranking", "recommendation", "ltr", "learning to rank", "personalization", "ndcg", "mrr"]
AI_TERMS = ["ai", "ml", "machine learning", "deep learning", "nlp", "llm", "rag", "pytorch", "tensorflow", "transformer"]
TARGET_TITLES = ["ai engineer", "ml engineer", "machine learning engineer", "data scientist", "backend engineer", "data engineer"]
CHEAT_TITLE_TERMS = ["marketing", "hr", "human resources", "consultant", "consulting", "research", "sales", "graphic designer"]



def _term_density(text: str, terms: list[str]) -> float:
    low = str(text).lower()
    if not low:
        return 0.0
    count = sum(1 for t in terms if t in low)
    return min(count / max(len(terms), 1), 1.0)


def _title_match(role: str) -> float:
    low = str(role).lower()
    if any(title in low for title in TARGET_TITLES):
        return 1.0
    if any(token in low for token in ["machine", "learning", "ai", "ml", "data", "backend"]):
        return 0.72
    if any(token in low for token in ["software", "engineer", "analytics"]):
        return 0.55
    return 0.20


def build_features(df: pd.DataFrame, jd: dict) -> pd.DataFrame:
    out = df.copy()
    text = out["candidate_text"].fillna("").astype(str)
    
    # Stage 4: Capability Scoring
    out["production_evidence"] = text.map(lambda x: _term_density(x, PRODUCTION_EVIDENCE_TERMS))
    out["ownership"] = text.map(lambda x: _term_density(x, OWNERSHIP_TERMS))
    out["retrieval_evidence"] = text.map(lambda x: _term_density(x, RETRIEVAL_EVIDENCE_TERMS))
    out["deployment_evidence"] = text.map(lambda x: _term_density(x, DEPLOYMENT_EVIDENCE_TERMS))
    out["startup_fit"] = text.map(lambda x: _term_density(x, STARTUP_FIT_TERMS))
    out["ranking_evidence"] = text.map(lambda x: _term_density(x, RANKING_EVIDENCE_TERMS))
    
    # Combined Production Score (Stage 4)
    out["production_score"] = (
        out["production_evidence"] * 0.25 +
        out["ownership"] * 0.15 +
        out["retrieval_evidence"] * 0.20 +
        out["deployment_evidence"] * 0.15 +
        out["startup_fit"] * 0.10 +
        out["ranking_evidence"] * 0.15
    ).clip(0, 1)
    
    # Stage 3: Behavior Scoring
    out["behavior_score"] = (
        (out["profile_completeness"] / 100.0) * 0.20 +
        out["response_rate"] * 0.25 +
        (out["github_activity"].clip(0, 100) / 100.0) * 0.15 +
        (out["saved_by_recruiters"].clip(0, 20) / 20.0) * 0.15 +
        out["interview_completion"] * 0.15 +
        (1 - out["notice_days"].clip(0, 90) / 90.0) * 0.10
    ).clip(0, 1)
    
    out["career_score"] = ((out["years"] / 10.0) * 0.50 + out["role"].map(_title_match) * 0.50).clip(0, 1)
    
    out["availability_score"] = (
        out["open_to_work"].astype(float) * 0.50 +
        (1 - out["notice_days"].clip(0, 90) / 90.0) * 0.50
    ).clip(0, 1)
    
    out["trust_score"] = (
        (out["profile_completeness"] / 100.0) * 0.30 +
        out["verified_email"].astype(float) * 0.20 +
        out["verified_phone"].astype(float) * 0.20 +
        out["linkedin_connected"].astype(float) * 0.30
    ).clip(0, 1)
    
    # Flags for Boost/Penalty
    out["is_product_company"] = text.str.contains("SaaS|Product|Consumer|Fintech|B2B", case=False, na=False).astype(int)
    out["is_open_source"] = text.str.contains("Open Source|Contributor|Maintainer", case=False, na=False).astype(int)
    
    return out
