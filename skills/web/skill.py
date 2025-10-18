import webbrowser

from utils.decorators import require_internet, log_command, timeit


@log_command("web.skill.search_web")
@timeit()
@require_internet()
def search_web(*args: tuple, **kwargs: dict) -> str:

    search_query = kwargs.get("phrase", None)
    speaker_silero = kwargs.get("speaker_silero", None)

    if not search_query:
        return "Что нужно найти?"

    if not speaker_silero:
        return "Error speaker Silero not found"

    search_url = f"https://google.com/search?q={search_query}"
    webbrowser.open(search_url)
    speaker_silero.say(f"Я открыл Google для поиска по запросу: {search_query}")
