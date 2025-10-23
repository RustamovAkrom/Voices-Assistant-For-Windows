import re
import webbrowser

def search_internet(query: str = None):
    """
    Выполняет поиск в интернете.
    Извлекает запрос из текста команды и открывает браузер.
    """
    if not query:
        print("⚠️ Нет текста для поиска.")
        return {
            "ru": "Не понял, что искать.",
            "en": "I didn't catch what to search for.",
            "uz": "Nimani izlash kerakligini tushunmadim."
        }["ru"]

    # Очищаем текст от служебных слов
    patterns = [
        r"джарвис[,]*", r"найди в интернете", r"искать", r"в интернете",
        r"search", r"in the internet", r"find", r"online",
        r"internetda", r"top", r"kimligini", r"haqida", r"malumot"
    ]
    clean_query = query.lower()
    for p in patterns:
        clean_query = re.sub(p, "", clean_query, flags=re.IGNORECASE)

    clean_query = clean_query.strip()
    if not clean_query:
        print("⚠️ Не удалось извлечь запрос.")
        return "Не понял, что искать."

    print(f"🌍 Открываю поиск: {clean_query}")
    webbrowser.open(f"https://www.google.com/search?q={clean_query}")

    return {
        "ru": f"Ищу в интернете: {clean_query}",
        "en": f"Searching the internet for {clean_query}",
        "uz": f"Internetda {clean_query} ni qidirmoqdaman"
    }["ru"]
