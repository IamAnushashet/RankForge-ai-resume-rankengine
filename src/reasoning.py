import pandas as pd

def _generate_snippet(row) -> str:
    parts = []
    text = str(row.get("candidate_text", "")).lower()
    
    # Core Capability
    if row.get("retrieval_evidence", 0) > 0.5:
        parts.append("Built retrieval infra")
    elif "ranking" in text or row.get("ranking_evidence", 0) > 0.5:
        parts.append("Shipped ranking systems")
    elif row.get("production_score", 0) > 0.6:
        parts.append("Production ML systems")
    elif "deployment" in text or row.get("deployment_evidence", 0) > 0.5:
        parts.append("Deployed ML models")
    
    # Specific Signal
    if row.get("ownership", 0) > 0.5:
        parts.append("end-to-end ownership")
    
    # Product/Startup context
    if row.get("is_product_company", 0) == 1:
        parts.append("product experience")
    elif row.get("startup_fit", 0) > 0.5:
        parts.append("startup builder")
    
    # Behavior/Availability
    if row.get("response_rate", 0) > 0.7:
        parts.append("high recruiter response")
    
    # Years of experience
    years = float(row.get("years", 0))
    parts.append(f"{years:.1f} yrs exp")
    
    if not parts:
        return "Verified AI/ML profile with production evidence"
        
    # Join parts with commas, capitalize first letter
    reason = ", ".join(parts)
    return reason[0].upper() + reason[1:]

def add_reasoning(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["reasoning"] = out.apply(_generate_snippet, axis=1)
    return out
