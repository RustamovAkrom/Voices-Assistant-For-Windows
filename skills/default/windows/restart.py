import os

def restart_windows() -> str:
    try:
        os.system("shutdown /r /t 5")
        return "Перезагружаю компьютер через 5 секунд"
    except Exception as e:
        return f"Не удалось перезагрузить компьютер: {str(e)}"
