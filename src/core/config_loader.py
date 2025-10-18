import yaml
from pathlib import Path

def load_config(path: str = "data/config.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        # дефолтная конфигурация
        return {
            "language_default": "ru",
            "voice_enabled": False,
            "speech_rate": 160,
            "matcher_threshold": 60,
            "debug": True
        }
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
