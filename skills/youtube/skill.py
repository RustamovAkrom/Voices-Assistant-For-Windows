import webbrowser


def search_youtube(*args: tuple, **kwargs: dict) -> str:
    search_query = kwargs.get("phrase", None)

    if not search_query:
        return "Что нужно найти?"
        
    url = f"https://www.youtube.com/results?search_query={search_query}"
    webbrowser.open(url)
    return f"Поиск '{search_query}' на YouTube."
