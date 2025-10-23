import re
import webbrowser

def search_internet(*args, **kwargs):
    """
    Универсальная функция поиска в интернете.
    Работает с любыми аргументами (*args, **kwargs).
    В kwargs можно передавать:
      - dataset: словарь команд (из commands.yaml)
      - query: текст команды пользователя
    """

    dataset = kwargs.get("dataset", {})
    query = kwargs.get("text")

    # 🧠 Если query не задан — пытаемся взять из args
    if not query and args:
        query = " ".join(str(a) for a in args if isinstance(a, str)).strip()

    if not query:
        return "⚠️ Не понял, что искать."

    # 🧩 Извлекаем паттерны из dataset (если есть)
    patterns = []
    for skill_data in dataset.get("skills", {}).values():
        for command in skill_data.get("commands", []):
            if command.get("action") == "search_web.search_internet":
                patterns.extend(command.get("patterns", []))

    # 🔁 Резервные паттерны
    if not patterns:
        patterns = [
            "найди в интернете", "поиск в интернете", "search", "find", "google it",
            "internetda qidir", "internetda izla"
        ]

    # 🧹 Очищаем команду от паттернов и служебных слов
    clean_query = query.lower()
    for pattern in patterns:
        clean_query = re.sub(re.escape(pattern.lower()), "", clean_query, flags=re.IGNORECASE)

    clean_query = re.sub(r"\b(джарвис|jarvis)[,]*", "", clean_query, flags=re.IGNORECASE)
    clean_query = clean_query.strip()

    if not clean_query:
        return "⚠️ Не понял, что искать."

    # 🌍 Выполняем поиск
    print(f"🌍 Открываю поиск: {clean_query}")
    webbrowser.open(f"https://www.google.com/search?q={clean_query}")

    return f"🔎 Ищу в интернете: {clean_query}"
