import os


def open_downloads() -> str:
    downloads_path = os.path.expanduser("~/Downloads")
    try:
        if os.path.exists(downloads_path):
            os.startfile(downloads_path)
            return "Открываю папку Загрузки"
        else:
            return "Папка Загрузок не найдена"
    except Exception as e:
        return f"Не удалось открыть папку Загрузок: {str(e)}"
