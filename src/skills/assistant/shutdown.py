import sys


def shutdown_assistant(*args, **kwargs):
    """
    🛑 Корректно завершает работу Jarvis.

    В kwargs можно передавать:
      - context: { "workers": [...], "assistant_name": str }
      - query: исходная команда пользователя
    """

    context = kwargs.get("context", {})
    query = kwargs.get("query", "")
    assistant_name = context.get("assistant_name", "Jarvis")
    workers = context.get("workers", [])

    print(f"🧠 {assistant_name} получил команду завершения: {query}")
    print("🔻 Завершение активных процессов...")

    for w in workers:
        if hasattr(w, "stop"):
            try:
                w.stop()
                print(f"✅ Остановлен поток: {getattr(w, 'name', 'Unnamed')}")
            except Exception as e:
                print(f"⚠️ Не удалось остановить поток: {e}")

    print(f"👋 {assistant_name} завершает работу.")
    sys.exit(0)
