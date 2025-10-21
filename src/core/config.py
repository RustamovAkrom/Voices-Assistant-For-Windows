import yaml
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / "data"
CONFIG_PATH = DATA_PATH / "config.yaml"
DATASET_PATH = DATA_PATH / "commands.yaml"
MODELS_DIR = DATA_PATH / "models"

VOSK_MODEL_URLS = {
    "ru": "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip",
    "en": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
    "uz": "https://alphacephei.com/vosk/models/vosk-model-small-uz-0.22.zip",
}

DETECT_LANGUAGE_WORDS = {
    "en": {"hello", "thanks", "how", "you", "open", "music"},
    "uz": {"salom", "rahmat", "qandaysiz", "yaxshi"},
    "ru": {"привет", "спасибо", "открой", "включи", "поставь"},
}

class Settings:
    def __init__(
            self, 
            config_path: Path = CONFIG_PATH,
            dataset_path: Path = DATASET_PATH
    ):
        self.config_path = config_path
        self.dataset_path = dataset_path
        self.config = self.load_config(config_path)
        self.dataset = self.load_dataset(dataset_path)

    def load_config(self, path: str):
        p = Path(path or self.config_path)
        if not p.exists():
            print(f"[WARN] Config not found at {p}, using defaults.")
            return {
                "language_default": "ru",
                "voice_enabled": False,
                "speech_rate": 160,
                "matcher_threshold": 60,
                "debug": True
            }
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def load_dataset(self, path: str):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def get(self, *keys, default=None):
        data = self.config
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        return data
    

@lru_cache(maxsize=30)
def get_settings(
    config_path: Path = CONFIG_PATH, 
    dataset_path: Path = DATASET_PATH
):
    return Settings(
        config_path=config_path,
        dataset_path=dataset_path,
    )
