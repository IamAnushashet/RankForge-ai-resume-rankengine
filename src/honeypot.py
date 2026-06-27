import pandas as pd
import numpy as np
import re

def detect_honeypots(df: pd.DataFrame) -> pd.DataFrame:
    """Implement Phase 3: Honeypot & Bias Detection."""
    out = df.copy()
    text = out["candidate_text"].fillna("").astype(str).str.lower()
    role = out["role"].fillna("").astype(str).str.lower()
    skills = out["skills_text"].fillna("").astype(str).str.lower()
    
    # 1. Keyword Stuffing
    # Ratio of unique tech terms to total words
    tech_terms = ["python", "ml", "ai", "machine learning", "pytorch", "tensorflow", "aws", "gcp", "docker", "kubernetes", "sql", "spark", "hadoop", "nlp", "llm", "rag"]
    tech_count = sum(text.str.contains(term).astype(int) for term in tech_terms)
    word_count = text.str.split().str.len().replace(0, 1)
    out["keyword_stuffing_score"] = (tech_count / word_count).clip(0, 1)
    
    # 2. Fake AI Resumes / AI-Generated Profiles
    # Checking for specific repetitive patterns or overly generic "AI Enthusiast" padding
    out["ai_generated_score"] = text.str.contains("passionate ai professional with expertise in cutting-edge algorithms|leveraging machine learning to drive business value", case=False).astype(float) * 0.5
    
    # 3. Title Mismatch
    # If role contains AI/ML but candidate_text doesn't have technical evidence
    out["title_mismatch"] = ((role.str.contains("ai|ml|machine learning")) & ~(text.str.contains("pytorch|tensorflow|scikit|sql|python|pipeline"))).astype(float)
    
    # 4. Inflated Skills
    # Skills count vs Experience years ratio
    skill_list_len = skills.str.split(",").str.len()
    out["skill_inflation"] = (skill_list_len / (out["years"].replace(0, 1) * 5)).clip(0, 1)
    
    # 5. Career Inconsistency
    # Large gaps or very short tenures everywhere (simplified)
    # This requires more complex data, but we'll use a placeholder for now
    out["career_inconsistency"] = 0.0
    
    # Calculate Trust Score (already partially in features.py, but we'll refine it)
    # Lower trust if stuffing, mismatch, or inflation detected
    out["trust_score"] = (
        (1 - out["keyword_stuffing_score"] * 0.4) +
        (1 - out["title_mismatch"] * 0.3) +
        (1 - out["skill_inflation"] * 0.3)
    ).clip(0, 1)
    
    # Duplicate Candidates detection (by ID mainly, but we can check similar fields if needed)
    # Handled by deduplication in loader/ranking if necessary.
    
    # Report Generation
    report = out[out["trust_score"] < 0.6][["candidate_id", "trust_score", "keyword_stuffing_score", "title_mismatch", "skill_inflation"]]
    report_path = "outputs/honeypot_report.csv"
    report.to_csv(report_path, index=False)
    
    return out

if __name__ == "__main__":
    # Test with dummy data if needed
    pass
