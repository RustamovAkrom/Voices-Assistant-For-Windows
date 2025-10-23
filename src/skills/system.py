import os
import webbrowser
import platform

def open_browser(*args, **kwargs):
    try:
        # cross-platform try
        webbrowser.open("https://www.google.com")
        return "Открываю браузер."
    except Exception as e:
        return f"Ошибка при открытии браузера: {e}"


def shutdown(*args, **kwargs):
    # if platform.system() == "Windows":
    #     os.system("shutdown /s /t 1")
    # else:
    #     os.system("sudo shutdown now")
    # осторожно: реальные вызовы выключения выключены для безопасности
    # для production можно использовать os.system("shutdown /s /t 0") на Windows
    return "Команда выключения получена (в демо режимe не выполняю)."


def restart(*args, **kwargs):
    # if platform.system() == "Windows":
    #     os.system("shutdown /r /t 1")
    # else:
    #     os.system("sudo reboot")
    return "Команда выключения получена (в демо режимe не выполняю)."


def sleep(*args, **kwargs):
    # os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return "Команда выключения получена (в демо режимe не выполняю)."


def lock_screen():
    if platform.system() == "Windows":
        os.system("rundll32.exe user32.dll,LockWorkStation")
    else:
        os.system("gnome-screensaver-command -l")
