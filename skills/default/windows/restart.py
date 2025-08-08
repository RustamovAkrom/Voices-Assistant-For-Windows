import os

from utils.decorators import log_command, catch_errors, timeit


@log_command("default.windows.restart.restart_windows")
@catch_errors()
@timeit()
def restart_windows() -> str:
    try:
        os.system("shutdown /r /t 5")
        return "Перезагружаю компьютер через 5 секунд"
    except Exception as e:
        return f"Не удалось перезагрузить компьютер: {str(e)}"

__all__ = ("restart_windows", )