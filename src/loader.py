import json
from pathlib import Path
import pandas as pd
import os

def _load_json(path: Path) -> pd.DataFrame:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("candidates", data.get("data", [data]))
    return pd.DataFrame(data)

def _load_jsonl(path: Path) -> pd.DataFrame:
    # Use pandas read_json for faster loading of large jsonl
    return pd.read_json(path, lines=True)

def load_file(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    suffix = p.suffix.lower()
    
    # Path inside repo for cache
    cache_dir = Path(__file__).resolve().parent.parent / "cache"
    cache_dir.mkdir(exist_ok=True)
    cache_path = cache_dir / f"{p.stem}.parquet"
    
    # Check if cache is valid
    if cache_path.exists():
        m1 = float(os.path.getmtime(cache_path))
        m2 = float(os.path.getmtime(p))
        if m1 > m2:
            print(f"DEBUG: loading from cache {cache_path}")
            return pd.read_parquet(cache_path)
    
    # Load and then cache
    if suffix == ".jsonl":
        df = _load_jsonl(p)
    elif suffix == ".json":
        df = _load_json(p)
    elif suffix == ".csv":
        df = pd.read_csv(p)
    else:
        raise ValueError(f"Unsupported dataset file type: {p}")
        
    # Save to cache
    try:
        df.to_parquet(cache_path)
    except Exception:
        pass
        
    return df

def load_dataset(root: str | Path) -> pd.DataFrame:
    root_path = Path(root)
    if root_path.is_file():
        return load_file(root_path)

    preferred = root_path / "candidates.jsonl"
    if preferred.exists():
        return load_file(preferred)

    dataset_dir = root_path / "dataset"
    if dataset_dir.exists():
        search_dir = dataset_dir
    else:
        search_dir = root_path

    for pattern in ("*.jsonl", "*.json", "*.csv"):
        files = sorted(search_dir.rglob(pattern))
        if files:
            return load_file(files[0])
    raise FileNotFoundError(f"No json/jsonl/csv dataset found under {root_path}")
