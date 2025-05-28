import webbrowser


def search_web(query: str) -> str:
    if not query:
        return "Что нужно найти?"
    
    search_url = f"https://google.com/search?q={query}"
    webbrowser.open(search_url)
    return f"Я открыл Google для поиска по запросу: {query}"
