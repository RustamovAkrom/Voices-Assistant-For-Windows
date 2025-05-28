import os
import subprocess


def open_browser(url: str) -> str:
    try:
        subprocess.Popen(['start', 'chrome', url], shell=True)
        return "Открываю браузер"
    except Exception as e:
        return f"Не удалось открыть браузер: {str(e)}"
