from __future__ import annotations

import pandas as pd

from config import TOP_K


def rank_candidates(df: pd.DataFrame, top_k: int = TOP_K) -> pd.DataFrame:
    out = df.sort_values(["score", "candidate_id"], ascending=[False, True]).head(top_k).copy()
    out["rank"] = range(1, len(out) + 1)
    return out

