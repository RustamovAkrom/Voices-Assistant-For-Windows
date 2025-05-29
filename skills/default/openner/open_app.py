import subprocess
from core import settings

def open_app(*args, **kwargs) -> str:
    cmd_text = str(args[0]).lower().strip() if args else ""
    if not cmd_text:
        return "Не указано приложение для открытия."

    for keys, path in settings.APPS_DIR.items():
        names = (keys,) if isinstance(keys, str) else keys
        if any(name in cmd_text for name in names):
            try:
                subprocess.Popen(path)
                return f"Открываю {names[0]}..."
            except Exception as e:
                return f"Не удалось открыть приложение {names[0]}: {e}"
    return "Приложение не найдено."
