import webbrowser


def open_browser(*args, **kwargs):
    try:
        # cross-platform try
        webbrowser.open("https://www.google.com")
        return "Открываю браузер."
    except Exception as e:
        return f"Ошибка при открытии браузера: {e}"
