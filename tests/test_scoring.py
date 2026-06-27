import pytest
import pandas as pd
import numpy as np
from src.scoring import score_candidates, normalize
from src.retrieval import compute_retrieval
from src.honeypot import detect_honeypots

def test_normalize():
    s = pd.Series([10, 20, 30])
    norm = normalize(s)
    assert norm.min() == 0
    assert norm.max() == 1
    assert norm[1] == 0.5

def test_scoring_logic():
    df = pd.DataFrame({
        "candidate_id": ["CAND_0000001", "CAND_0000002"],
        "semantic_score": [0.8, 0.2],
        "retrieval_score": [0.7, 0.3],
        "production_score": [0.9, 0.1],
        "career_score": [0.8, 0.4],
        "behavior_score": [0.9, 0.2],
        "availability_score": [1.0, 0.5],
        "trust_score": [1.0, 0.8],
        "years": [5, 2],
        "role": ["AI Engineer", "Intern"],
        "candidate_text": ["Production ML systems, LLM, RAG, Deployed models", "Self learning AI"],
        "response_rate": [0.8, 0.1],
        "notice_days": [30, 90],
        "is_product_company": [1, 0],
        "is_open_source": [0, 0],
        "retrieval_evidence": [0.8, 0.1],
        "ranking_evidence": [0.7, 0.1],
        "deployment_evidence": [0.9, 0.1],
        "ownership": [0.8, 0.1]
    })
    scored = score_candidates(df)
    assert scored.iloc[0]["score"] > scored.iloc[1]["score"]

def test_honeypot_detection():
    df = pd.DataFrame({
        "candidate_id": ["CAND_0000003"],
        "candidate_text": ["AI AI AI AI AI ML ML ML ML Python Python Python"],
        "role": ["Marketing Manager"],
        "skills_text": ["AI, ML, Python, Java, C++, Ruby, Rust, Go, SQL, AWS, GCP, Azure, Docker, Kubernetes"],
        "years": [1]
    })
    trusted = detect_honeypots(df)
    assert trusted.iloc[0]["trust_score"] < 0.6
