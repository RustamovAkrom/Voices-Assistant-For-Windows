import yaml
from pathlib import Path


def change_language(lang_code):
    config_path = Path("src/core/config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config["language"] = lang_code
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True)

    return f"Язык успешно изменён на {lang_code}."
