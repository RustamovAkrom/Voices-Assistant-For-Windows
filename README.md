
# Jarvis Voice Assistant

![Jarvis Banner](https://raw.githubusercontent.com/Akrom-dev/jarvis-assets/main/banner.png)

## Описание
Jarvis — это офлайн голосовой ассистент для Windows с поддержкой расширяемых навыков (skills), нечетким распознаванием команд, активацией по ключевому слову и гибкой архитектурой для разработчиков.

---

## Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск ассистента
```bash
python main.py
```

> **Требования:** Python 3.7+, Windows 10/11, микрофон.

---

## Архитектура

```
main.py
├── core/
│   ├── words_data.py      # Датасет команд и триггеров
│   ├── config.py          # Конфиг и настройки
│   └── ...
├── recognizer/           # Распознавание речи (Vosk, Porcupine)
├── tts/                  # Синтез речи (Silero, pyttsx3)
├── skills/               # Навыки (skills) — расширяемые обработчики
├── controllers/          # Логика команд (погода, музыка, время и т.д.)
└── utils/                # Утилиты (fuzzy matching, text cleaner)
```

---

## Как добавить свой скилл (навык)

1. **Создайте папку** в `skills/` (например, `skills/my_skill/`).
2. **Создайте файл** `skill.py` с функцией-обработчиком:
    ```python
    # skills/my_skill/skill.py
    def my_handler(query: str = None) -> str:
        return f"Вы сказали: {query}"
    ```
3. **Добавьте ключевые фразы** в `core/words_data.py`:
    ```python
    data_set.append({
        "phrases": ["мой скилл", "запусти мой скилл"],
        "handler": "my_skill.my_handler",
        "param": True
    })
    ```
4. **Готово!** Теперь Jarvis распознает ваш навык.

---

## Расширенные возможности
- **Fuzzy matching**: команды распознаются даже с ошибками и лишними словами.
- **Активация по ключевому слову**: PorcupineListener ("джарвис", "jarvis" и др.).
- **Оффлайн-распознавание**: Vosk.
- **TTS**: Silero TTS (по умолчанию) или pyttsx3.
- **Легко расширяемая архитектура**: добавляйте свои skills и контроллеры.

---

## Пример работы

![Jarvis Demo](https://raw.githubusercontent.com/Akrom-dev/jarvis-assets/main/demo.gif)

---

## FAQ
- **Где лежат команды?** — В `core/words_data.py` (или `words.py` в старых версиях).
- **Как добавить обработчик?** — Просто добавьте функцию и пропишите путь в `handler`.
- **Как сменить голос?** — В tts/silero_tts.py или tts/pyttsx3_tts.py.
- **Как сменить активационное слово?** — В PorcupineListener (см. `main.py`).

---

## Лицензия
MIT License

---

## Контакты и поддержка
- [GitHub Issues](https://github.com/Akrom-dev/jarvis/issues)
- [Telegram](https://t.me/akrom_dev)

---

> ![Jarvis Logo](https://raw.githubusercontent.com/Akrom-dev/jarvis-assets/main/jarvis_icon.png)
