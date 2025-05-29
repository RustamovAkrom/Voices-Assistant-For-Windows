import webbrowser


def search_web(*args: tuple, **kwargs) -> str:
    print(args, kwargs)
    query = str(args[0]) if args else None
    phrase = kwargs.get('phrase', None)

    if not query:
        return "Что нужно найти?"
    
    search_query = query.replace(phrase, '', 1).strip() if phrase else query

    if not search_query:
        return "Что нужно найти?"
    
    search_url = f"https://google.com/search?q={search_query}"
    webbrowser.open(search_url)
    return f"Я открыл Google для поиска по запросу: {search_query}"
