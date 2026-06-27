from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_rank_default_command():
    repo = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, "rank.py"], cwd=repo, check=True, timeout=300)
    sys.path.insert(0, str(repo))
    from utils.io import find_root

    root = find_root(repo)
    out = root / "submission.csv"
    assert out.exists()
    df = pd.read_csv(out)
    assert len(df) == 100
    assert df["candidate_id"].is_unique
    assert df["score"].is_monotonic_decreasing


if __name__ == "__main__":
    test_rank_default_command()
