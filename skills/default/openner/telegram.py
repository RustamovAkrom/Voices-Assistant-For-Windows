import os
import subprocess


def open_telegram() -> str:
    try:
        telegram_path = r"C:\Users\user\AppData\Roaming\Telegram Desktop\Telegram.exe"
        subprocess.Popen([telegram_path])
        return "Telegram успешно открыт."
    except Exception as e:
        return f"Не удалось открыть Telegram: {str(e)}"
