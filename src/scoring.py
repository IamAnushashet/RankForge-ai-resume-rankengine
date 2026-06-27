import numpy as np
import pandas as pd
from config import FINAL_WEIGHTS

def normalize(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    values = series.astype(float).values
    lo, hi = np.min(values), np.max(values)
    if hi <= lo:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return pd.Series((values - lo) / (hi - lo), index=series.index)

def score_candidates(df: pd.DataFrame) -> pd.DataFrame:
    """Implement Phase 2: Final Rank Formula + Boosts/Penalties."""
    out = df.copy()
    
    # Base Score Calculation
    total = pd.Series(np.zeros(len(out)), index=out.index, dtype=float)
    for column, weight in FINAL_WEIGHTS.items():
        if column not in out:
            continue
        total += normalize(out[column].fillna(0)) * weight
    
    out["score"] = total
    
    # Penalties
    role = out["role"].fillna("").astype(str).str.lower()
    text = out["candidate_text"].fillna("").astype(str).str.lower()
    
    # Apply penalties via .loc
    # Research-only: ×0.82
    is_research = role.str.contains("research", na=False) & ~text.str.contains("production|shipped|deployed", na=False)
    out.loc[is_research, "score"] *= 0.82
    
    # No production: ×0.75
    out.loc[out["production_score"] < 0.20, "score"] *= 0.75
    
    # Experience <4: ×0.80
    out.loc[out["years"] < 4, "score"] *= 0.80
    
    # Inactive: ×0.90 
    out.loc[out["behavior_score"] < 0.30, "score"] *= 0.90
    
    # Low recruiter response: ×0.90
    out.loc[out["response_rate"] < 0.20, "score"] *= 0.90
    
    # Long notice: ×0.90
    out.loc[out["notice_days"] > 60, "score"] *= 0.90
    
    # Keyword stuffing: ×0.85
    tech_count = text.str.count("python|ml|ai|sql|aws|gcp|docker|kubernetes|pytorch|tensorflow")
    is_stuffed = (tech_count / text.str.len().replace(0, 1)) > 0.05
    out.loc[is_stuffed, "score"] *= 0.85
    
    # Service-only career: ×0.88
    is_service = text.str.contains("consultant|tcs|infosys|wipro|cognizant|accenture", case=False, na=False)
    out.loc[is_service, "score"] *= 0.88
    
    # Boosts
    # retrieval deployed: ×1.15
    has_retrieval_prod = (out["retrieval_evidence"] > 0.4) & (out["deployment_evidence"] > 0.4)
    out.loc[has_retrieval_prod, "score"] *= 1.15
    
    # ranking ownership: ×1.10
    has_ranking_own = (out["ranking_evidence"] > 0.4) & (out["ownership"] > 0.4)
    out.loc[has_ranking_own, "score"] *= 1.10
    
    # product company: ×1.08
    out.loc[out["is_product_company"] == 1, "score"] *= 1.08
    
    # open source: ×1.06
    out.loc[out["is_open_source"] == 1, "score"] *= 1.06
    
    # response >0.5: ×1.05
    out.loc[out["response_rate"] > 0.50, "score"] *= 1.05
    
    out["base_score"] = total.round(6)
    out["score"] = normalize(out["score"]).clip(0, 1).round(6)
    
    return out
