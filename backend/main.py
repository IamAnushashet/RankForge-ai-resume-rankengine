import subprocess
import sys
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from config import DEFAULT_JD
from src.features import build_features
from src.flatten import flatten_candidates
from src.jd_parser import parse_jd
from src.loader import load_dataset
from src.retrieval import compute_retrieval
from src.scoring import score_candidates
from utils.io import discover_file, find_root, read_text

REPO_ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(title="Redrob AI Recruiter Dashboard")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for PoC
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _root() -> Path:
    return find_root(REPO_ROOT)

def _submission_path() -> Path:
    return _root() / "submission.csv"

@lru_cache(maxsize=1)
def _raw_records() -> list[dict[str, Any]]:
    df = load_dataset(_root())
    return df.to_dict("records")

@lru_cache(maxsize=1)
def _scored() -> pd.DataFrame:
    root = _root()
    jd_path = discover_file(root, ("job_description.txt",))
    jd_text = read_text(jd_path, DEFAULT_JD).strip() or DEFAULT_JD
    raw = pd.DataFrame(_raw_records())
    flat = flatten_candidates(raw)
    featured = build_features(flat, parse_jd(jd_text))
    retrieved = compute_retrieval(featured, jd_text)
    return score_candidates(retrieved)

def _submission() -> pd.DataFrame:
    path = _submission_path()
    if not path.exists():
        raise HTTPException(status_code=404, detail="submission.csv not found. Run ranking first.")
    return pd.read_csv(path)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2026.1.0"}

@app.get("/top100")
def top100() -> list[dict[str, Any]]:
    return _submission().to_dict("records")

@app.get("/candidate/{candidate_id}")
def candidate(candidate_id: str) -> dict[str, Any]:
    record = next((r for r in _raw_records() if r.get("candidate_id") == candidate_id), None)
    if record is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    score_row = pd.DataFrame()

    debug_path = REPO_ROOT / "outputs" / "top10_debug.csv"

    if debug_path.exists():
        try:
            score_row = pd.read_csv(debug_path)
            score_row = score_row[
                score_row["candidate_id"] == candidate_id
            ]
        except Exception:
            score_row = pd.DataFrame()
    submission = _submission()
    rank_row = submission[submission["candidate_id"] == candidate_id]
    
    # Load explanation if exists
    exp_path = REPO_ROOT / "outputs" / "explanations" / f"{candidate_id}.json"
    explanation = {}
    if exp_path.exists():
        explanation = json.loads(exp_path.read_text())
        
    score = score_row.iloc[0].to_dict() if not score_row.empty else {}
    ranking = rank_row.iloc[0].to_dict() if not rank_row.empty else {}
    def make_json_safe(obj):
        import numpy as np

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        if isinstance(obj, dict):
            return {
                k: make_json_safe(v)
                for k, v in obj.items()
            }

        if isinstance(obj, list):
            return [
                make_json_safe(v)
                for v in obj
            ]

        return obj
    return make_json_safe({
        "candidate": record,
        "ranking": ranking,
        "explanation": explanation,
    })
@app.post("/run")
def run_ranker() -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "rank.py"), "--root", str(_root())],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=600,
    )
    _scored.cache_clear()
    _raw_records.cache_clear()
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stdout + result.stderr)
    return {"status": "ok", "output": str(_submission_path()), "log": result.stdout + result.stderr}

@app.post("/validate")
def validate() -> dict[str, Any]:
    validator_script = _root() / "validate_submission.py"
    if not validator_script.exists():
        raise HTTPException(status_code=404, detail="validate_submission.py not found in challenge root")
    
    result = subprocess.run(
        [sys.executable, str(validator_script), str(_submission_path())],
        cwd=str(_root()),
        text=True,
        capture_output=True,
    )
    return {
        "valid": result.returncode == 0,
        "output": result.stdout + result.stderr
    }

@app.get("/metrics")
def metrics() -> dict[str, Any]:
    submission = _submission()
    scored = _scored()
    top_ids = set(submission["candidate_id"].astype(str))
    top = scored[scored["candidate_id"].isin(top_ids)].copy()
    merged = submission.merge(top, on="candidate_id", how="left")
    
    return {
        "totalCandidates": int(len(scored)),
        "topScore": float(submission["score"].max()),
        "averageScore": float(submission["score"].mean()),
        "pipelineRuntime": "under 5 min",
        "scoreDistribution": submission["score"].round(2).value_counts().sort_index().reset_index().rename(
            columns={"score": "score", "count": "count"}
        ).to_dict("records"),
        "explainability": [
            {
                "name": name,
                "average": float(merged[col].fillna(0).mean()),
                "weight": weight,
                "contribution": float(merged[col].fillna(0).mean() * weight),
            }
            for name, col, weight in [
                ("Semantic", "semantic_score", 0.25),
                ("Retrieval", "retrieval_score", 0.25),
                ("Production", "production_score", 0.20),
                ("Career", "career_score", 0.10),
                ("Behavior", "behavior_score", 0.10),
                ("Availability", "availability_score", 0.05),
                ("Trust", "trust_score", 0.05),
            ]
        ],
    }

@app.get("/download")
def download() -> FileResponse:
    path = _submission_path()
    if not path.exists():
        raise HTTPException(status_code=404, detail="submission.csv not found")
    return FileResponse(path, media_type="text/csv", filename="submission.csv")

@app.get("/debug")
def debug() -> dict[str, Any]:
    debug_csv = REPO_ROOT / "outputs" / "top10_debug.csv"
    if not debug_csv.exists():
        raise HTTPException(status_code=404, detail="top10_debug.csv not found")
    df = pd.read_csv(debug_csv)
    return {"top10": df.to_dict("records")}
