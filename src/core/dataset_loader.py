import yaml
from pathlib import Path


def load_dataset(path: str = "data/commands.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
