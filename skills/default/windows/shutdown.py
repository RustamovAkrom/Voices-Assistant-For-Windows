import os


def shutdown_windows() -> str:
    try:
        os.system("shutdown /s /t 5")
        return "Выключаю компьютер через 5 секунд"
    except Exception as e:
        return f"Не удалось выключить компьютер: {str(e)}"
