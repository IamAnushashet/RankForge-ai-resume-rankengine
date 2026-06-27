from __future__ import annotations

from pathlib import Path


def load_sentence_transformer(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
    except Exception:
        return None

    candidates = [
        Path(model_name),                    # ./models/all-MiniLM-L6-v2
        Path("models") / model_name,         # fallback
        Path("models_cache") / model_name,
    ]

    for path in candidates:
        if path.exists():
            try:
                return SentenceTransformer(
                    str(path),
                    local_files_only=True
                )
            except Exception:
                continue

    try:
        return SentenceTransformer(
            model_name,
            local_files_only=True
        )
    except Exception:
        return None