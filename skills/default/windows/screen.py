import os
from datetime import datetime
import pyautogui

from utils.decorators import log_command, catch_errors, timeit


@log_command("default.windows.screen.screenshot_windows")
@catch_errors()
@timeit()
def screenshot_windows():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = os.path.join(desktop, filename)
    image = pyautogui.screenshot()
    image.save(path)
    return f"Скриншот сохранен на рабочем столе: {path}"


__all__ = ("screenshot_windows",)
