import os
import webbrowser

def open_browser():
    try:
        # cross-platform try
        webbrowser.open("https://www.google.com")
        return "Открываю браузер."
    except Exception as e:
        return f"Ошибка при открытии браузера: {e}"

def shutdown():
    # осторожно: реальные вызовы выключения выключены для безопасности
    # для production можно использовать os.system("shutdown /s /t 0") на Windows
    return "Команда выключения получена (в демо режимe не выполняю)."
