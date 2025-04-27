import webbrowser


def open_youtube(*args: str) -> str:
    """
    Open YouTube in the default web browser.
    """

    url = "https://www.youtube.com"
    webbrowser.open(url)
    return "YouTube открыт в браузере."


def search_youtube(query: str) -> str:
    """
    Search for a query on YouTube.
    """
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)
    return f"Поиск '{query}' на YouTube."