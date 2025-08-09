import requests
import webbrowser
from core import settings
from utils.decorators import require_internet, log_command, timeit, catch_errors


@catch_errors()
def get_news_data(query: str, api_key: str, language="en", speaker=None, max_results=3) -> None:
    url = f"https://newsapi.org/v2/everything?q={query}&language={language}&pageSize={max_results}&sortBy=publishedAt"
    headers = {"Authorization": api_key}

    response = requests.get(url, headers=headers)
    data = response.json()

    if "articles" in data and data["articles"]:
        for article in data["articles"]:
            title = article["title"]
            link = article["url"]
            description = article.get("description", "Без описания.")
            print(f"Заголовок: {title}\nОписание: {description}\nСсылка: {link}\n\n")
            webbrowser.open(link)
            result = f"Заголовок: {title}\nОписание: {description}."
            if speaker is not None:
                speaker.say(result)
        return
    else:
        speaker.say("Нет новостей по вашему запросу.")


@log_command("news.skill.search_news")
@timeit()
@require_internet()
def search_news(*args: tuple, **kwargs: dict) -> str:
    """
    Функция для получения последних новостей по запросу.
    """
    search_query = kwargs.get("phrase", None)
    speaker_silero = kwargs.get("speaker_silero", None)

    if not search_query:
        return "Что нужно найти?"
    
    if not speaker_silero:
        return "Error speaker Silero not found"

    get_news_data(
        search_query, 
        settings.NEWS_API_ACCESS_KEY, 
        language="ru", 
        speaker=speaker_silero,
        max_results=3
    )


__all__ = ("search_news",)
