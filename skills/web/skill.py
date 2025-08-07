import webbrowser


def search_web(*args: tuple, **kwargs: dict) -> str:
    
    search_query = kwargs.get("phrase", None)
    print(search_query)

    if not search_query:
        return "Что нужно найти?"

    search_url = f"https://google.com/search?q={search_query}"
    webbrowser.open(search_url)
    return f"Я открыл Google для поиска по запросу: {search_query}"
