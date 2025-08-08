import os

from utils.decorators import log_command, catch_errors, timeit


@log_command("default.windows.sleep.sleep_windows")
@catch_errors()
@timeit()
def sleep_windows():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

__all__ = ("sleep_windows", )