import wikipedia


wikipedia.set_lang("ru")


def search_wikipedia(query):
    """
    Search Wikipedia for a given query and return the results.
    """

    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Слишком много значений: {e.options[:3]}"
    except Exception as e:
        return f"Ошибка поиска: {e}"
