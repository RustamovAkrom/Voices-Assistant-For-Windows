import yaml
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / "data"
DEFAULT_CONFIG_PATH = DATA_PATH / "config.yaml"
DATASET_PATH = DATA_PATH / "commands.yaml"
MODELS_DIR = DATA_PATH / "models"

class Settings:
    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH, dataset_path: Path = DATASET_PATH):
        self.config_path = config_path
        self.dataset_path = dataset_path
        self.config = self.load_config(config_path)
        self.dataset = self.load_dataset(dataset_path)

    def load_config(self, path: Path):
        if not path.exists():
            print(f"[WARN] Config not found at {path}, using defaults.")
            # Значения по умолчанию
            return {
                "assistant": {"default_language": "ru"},
                "voice_enabled": True,
                "voice_engine": "silero",
                "voice_speed": 160,
                "voice_volume": 1.0,
                "voice_gender": "female",
                "voice_speaker": "aidar",
                "matcher_threshold": 60,
                "debug": False,
                "offline_mode": False,
                "auto_switch_mode": True,
                "wake_word": "джарвис",
            }
        with open(path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        # Проверка наличия необходимых ключей и настройка при их отсутствии:
        cfg.setdefault("voice_enabled", True)
        cfg.setdefault("voice_engine", "silero")
        cfg.setdefault("voice_speed", 160)
        cfg.setdefault("voice_volume", 1.0)
        cfg.setdefault("offline_mode", False)
        cfg.setdefault("auto_switch_mode", True)
        cfg.setdefault("debug", False)
        cfg.setdefault("matcher_threshold", 60)
        cfg.setdefault("wake_word", "джарвис")
        return cfg
    
    def load_dataset(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, *keys, default=None):
        data = self.config
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        return data

# Убираем кеширование, чтобы перезагрузка конфига реально читала файл заново
def get_settings(
    config_path: Path = DEFAULT_CONFIG_PATH, 
    dataset_path: Path = DATASET_PATH
):
    return Settings(config_path=config_path, dataset_path=dataset_path)
