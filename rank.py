import json
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import sys

from config import DEFAULT_JD
from src.features import build_features
from src.flatten import flatten_candidates
from src.honeypot import detect_honeypots
from src.jd_parser import parse_jd
from src.loader import load_dataset
from src.ranking import rank_candidates
from src.reasoning import add_reasoning
from src.retrieval import compute_retrieval
from src.scoring import score_candidates
from src.validator import validate_or_repair
from utils.io import discover_challenge_files, discover_file, find_root, read_text
from utils.logger import get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline Redrob candidate ranker")
    parser.add_argument("--root", default=None, help="Challenge root containing validate_submission.py")
    parser.add_argument("--dataset", default=None, help="Optional dataset file or directory")
    parser.add_argument("--jd", default=None, help="Optional job_description.txt path")
    parser.add_argument("--out", default=None, help="Optional output CSV path")
    return parser.parse_args()


def resolve_root(value: str | None) -> Path:
    if value is not None:
        target = Path(value)
        return find_root(target)
    discover_challenge_files(Path("."))
    return find_root(Path("."))


def write_top10_debug(scored, repo_root: Path) -> None:
    debug_path = repo_root / "outputs" / "top10_debug.csv"
    debug_path.parent.mkdir(parents=True, exist_ok=True)
    debug = scored.sort_values(["score", "candidate_id"], ascending=[False, True]).head(10).copy()
    debug = debug.rename(
        columns={
            "role": "title",
            "semantic_score": "semantic",
            "retrieval_score": "retrieval",
            "production_score": "production",
            "behavior_score": "behavior",
            "score": "final_score",
        }
    )
    cols = ["candidate_id", "title", "semantic", "retrieval", "production", "behavior", "final_score"]
    debug[cols].to_csv(debug_path, index=False)


def write_explanations(ranked: pd.DataFrame, repo_root: Path) -> None:
    exp_dir = repo_root / "outputs" / "explanations"
    exp_dir.mkdir(parents=True, exist_ok=True)
    for _, row in ranked.head(100).iterrows():
        cid = row["candidate_id"]
        # Convert row to dict, handling non-serializable objects
        data = row.to_dict()
        # Clean up data for JSON
        serializable = {}
        for k, v in data.items():
            if isinstance(v, (np.integer, np.floating)):
                serializable[k] = float(v)
            elif isinstance(v, (pd.Timestamp, Path)):
                serializable[k] = str(v)
            else:
                serializable[k] = v
        
        with open(exp_dir / f"{cid}.json", "w") as f:
            json.dump(serializable, f, indent=2)


def main() -> None:
    args = parse_args()
    log = get_logger()
    root = resolve_root(args.root)
    repo_root = Path(__file__).resolve().parent
    dataset_path = Path(args.dataset).expanduser() if args.dataset else root
    jd_path = Path(args.jd).expanduser() if args.jd else discover_file(root, ("job_description.txt",))
    output_path = root / "submission.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    jd_text = read_text(jd_path, DEFAULT_JD).strip() or DEFAULT_JD
    log.info("Using challenge root: %s", root)
    log.info("Loading dataset from: %s", dataset_path)
    raw = load_dataset(dataset_path)
    flat = flatten_candidates(raw)
    jd = parse_jd(jd_text)
    
    # Pipeline
    log.info("Building features...")
    featured = build_features(flat, jd)
    log.info("Applying honeypot detection...")
    trusted = detect_honeypots(featured)
    log.info("Computing retrieval and semantic ranking...")
    retrieved = compute_retrieval(trusted, jd_text)
    log.info("Scoring candidates...")
    scored = score_candidates(retrieved)
    
    write_top10_debug(scored, repo_root)
    log.info("Ranking and adding reasoning...")
    ranked = add_reasoning(rank_candidates(scored))
    
    log.info("Exporting explanations...")
    write_explanations(ranked, repo_root)
    
    submission = ranked[["candidate_id", "rank", "score", "reasoning"]].copy()
    submission.to_csv(output_path, index=False)
    validate_or_repair(root, output_path)
    log.info("Wrote valid submission: %s", output_path)
    print("FINAL OUTPUT PATH:", output_path)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
