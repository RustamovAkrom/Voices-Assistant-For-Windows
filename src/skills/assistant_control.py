import yaml
from pathlib import Path
import sys


def change_language(lang_code):
    
    config_path = Path("src/core/config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config["language"] = lang_code
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True)

    return f"Язык успешно изменён на {lang_code}."

def shutdown_assistant(*args, **kwargs):
    """
    Корректно завершает работу Jarvis.
    Останавливает фоновые воркеры и завершает процесс.
    """
    print("🛑 Остановка Jarvis...")
    print(*args, **kwargs)
    # context = kwargs.get("context", {})
    # workers = context.get("workers", [])

    # # Пробуем корректно завершить все потоки
    # for w in workers:
    #     if hasattr(w, "stop"):
    #         try:
    #             w.stop()
    #             print(f"[INFO] 🔻 Остановлен поток: {w.name}")
    #         except Exception as e:
    #             print(f"[WARN] Не удалось остановить {w.name}: {e}")

    # # Если потоков нет, просто выходим
    # print("👋 Jarvis завершает работу.")
    # sys.exit(0)
