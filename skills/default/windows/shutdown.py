import os

from utils.decorators import log_command, catch_errors, timeit


@log_command("default.windows.shutdown.shutdown_windows")
@catch_errors()
@timeit()
def shutdown_windows() -> str:
    try:
        os.system("shutdown /s /t 5")
        return "Выключаю компьютер через 5 секунд"
    except Exception as e:
        return f"Не удалось выключить компьютер: {str(e)}"

__all__ = ("shutdown_windows", )
