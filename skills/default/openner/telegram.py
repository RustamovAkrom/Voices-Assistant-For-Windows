import os
import subprocess


def open_telegram() -> str:
    try:
        subprocess.Popen(['start', 'telegram'], shell=True)
        return "Открываю Telegram"
    except Exception as e:
        return f"Не удалось открыть Telegram: {str(e)}"
