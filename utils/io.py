from __future__ import annotations

from pathlib import Path


TARGET_ROOT_FILES = ("candidate_schema.json", "validate_submission.py")
DISCOVERY_NAMES = (
    "candidate_schema.json",
    "job_description.txt",
    "validate_submission.py",
    "sample_submission.csv",
    "candidates.jsonl",
)


def find_root(start: str | Path = ".") -> Path:
    start_path = Path(start).expanduser().resolve()
    if start_path.is_file():
        start_path = start_path.parent

    for parent in [start_path] + list(start_path.parents):
        found_all = True
        for name in TARGET_ROOT_FILES:
            if not (parent / name).exists():
                found_all = False
                break
        if found_all:
            return parent

    search_roots = [start_path]
    if start_path.parent not in search_roots:
        search_roots.append(start_path.parent)

    for search_root in search_roots:
        hits: dict[Path, set[str]] = {}
        for p in search_root.rglob("*"):
            if p.is_file() and p.name in TARGET_ROOT_FILES:
                hits.setdefault(p.parent, set()).add(p.name)
        for directory, names in hits.items():
            if set(TARGET_ROOT_FILES).issubset(names):
                return directory
    raise FileNotFoundError(
        "Could not find challenge root containing candidate_schema.json and validate_submission.py"
    )


def discover_file(root: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        direct = root / name
        if direct.exists():
            return direct
    for p in root.rglob("*"):
        if p.is_file() and p.name in names:
            return p
    return None


def discover_challenge_files(start: str | Path = ".") -> dict[str, Path]:
    start_path = Path(start).expanduser().resolve()
    if start_path.is_file():
        start_path = start_path.parent

    search_roots = [start_path]
    if start_path.parent not in search_roots:
        search_roots.append(start_path.parent)

    found: dict[str, Path] = {}
    for search_root in search_roots:
        for p in search_root.rglob("*"):
            if not p.is_file():
                continue
            if p.name in DISCOVERY_NAMES or (
                p.name.startswith("submission_metadata") and p.suffix == ".yaml"
            ):
                found.setdefault(p.name, p)
    return found


def read_text(path: Path | None, default: str = "") -> str:
    if path is None or not path.exists():
        return default
    return path.read_text(encoding="utf-8", errors="ignore")
