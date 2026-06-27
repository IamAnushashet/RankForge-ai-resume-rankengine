import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import MODEL_NAME
from models.model_loader import load_sentence_transformer


def _normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return values
    lo, hi = float(values.min()), float(values.max())
    if hi <= lo:
        return np.zeros_like(values)
    return (values - lo) / (hi - lo)


def compute_retrieval(df: pd.DataFrame, jd_text: str) -> pd.DataFrame:
    """Implement Phase 2: 2-stage retrieval & ranking."""
    out = df.copy()
    jd_text = str(jd_text)
    texts = out["candidate_text"].fillna("").astype(str).tolist()
    
    # Stage 1: Fast Candidate Retrieval (TFIDF + Keyword/Skill Match)
    # We'll use TFIDF scores as a proxy for BM25-lite
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=10000)
    tfidf_matrix = vectorizer.fit_transform(texts + [jd_text])
    jd_vector = tfidf_matrix[-1:]
    candidate_vectors = tfidf_matrix[:-1]
    
    tfidf_sims = cosine_similarity(candidate_vectors, jd_vector).ravel()
    
    # Simple Skill Match Boost for Stage 1
    jd_terms = set(re.findall(r"\w+", jd_text.lower()))
    skill_scores = []
    for text in texts:
        cand_terms = set(re.findall(r"\w+", str(text).lower()))
        matches = len(jd_terms.intersection(cand_terms))
        skill_scores.append(matches / max(len(jd_terms), 1))
    
    stage1_score = 0.7 * tfidf_sims + 0.3 * np.array(skill_scores)
    out["retrieval_score"] = _normalize(stage1_score)
    
    # Select Top 500 for Stage 2
    top_500_indices = out["retrieval_score"].sort_values(ascending=False).head(500).index
    
    # Stage 2: Semantic Ranking (sentence-transformers)
    out["semantic_score"] = 0.0
    top_500_texts = out.loc[top_500_indices, "candidate_text"].fillna("").astype(str).tolist()
    
    model = load_sentence_transformer(MODEL_NAME)
    if model is not None:
        # Encode JD and Top 500 candidates
        jd_emb = model.encode([jd_text], convert_to_numpy=True, normalize_embeddings=True)
        cand_embs = model.encode(top_500_texts, batch_size=32, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True)
        semantic_sims = np.asarray(cand_embs @ jd_emb[0], dtype=float)
        out.loc[top_500_indices, "semantic_score"] = _normalize(semantic_sims)
    else:
        # Fallback if model fails to load
        out.loc[top_500_indices, "semantic_score"] = out.loc[top_500_indices, "retrieval_score"]
        
    return out
