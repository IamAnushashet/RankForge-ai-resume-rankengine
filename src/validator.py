from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


def repair_submission(path: Path) -> None:
    df = pd.read_csv(path)
    df = df[["candidate_id", "rank", "score", "reasoning"]].copy()
    df["candidate_id"] = df["candidate_id"].astype(str)
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)
    df = df.sort_values(["score", "candidate_id"], ascending=[False, True]).head(100)
    df["rank"] = range(1, len(df) + 1)
    df["score"] = df["score"].round(6)
    df["reasoning"] = df["reasoning"].fillna("").astype(str).str.slice(0, 140)
    df.to_csv(path, index=False)


def validate_or_repair(root: Path, submission_path: Path) -> None:
    validator = root / "validate_submission.py"
    if not validator.exists():
        return
    for attempt in range(2):
        result = subprocess.run(
            [sys.executable, str(validator), str(submission_path)],
            cwd=str(root),
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            return
        if attempt == 0:
            repair_submission(submission_path)
            continue
        raise RuntimeError((result.stdout or "") + (result.stderr or ""))

