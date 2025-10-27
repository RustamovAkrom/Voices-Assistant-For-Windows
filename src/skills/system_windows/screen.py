import os
import platform


def lock_screen():
    if platform.system() == "Windows":
        os.system("rundll32.exe user32.dll,LockWorkStation")
    else:
        os.system("gnome-screensaver-command -l")
