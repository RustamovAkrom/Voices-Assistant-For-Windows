![img](banner.jpg)
## 🤖 Jarvis Voice Assistant (Offline, Windows)

Полноценный голосовой ассистент на Python, работающий **офлайн**, поддерживающий **русскую речь**, управление приложениями, поиск, выполнение системных команд и озвучку с помощью **Silero TTS**.

---

### 🚀 Быстрый старт

#### 1. Клонируй проект и создай виртуальное окружение:

```bash
git clone https://github.com/RustamovAkrom/Jarvis.git
cd Jarvis
python -m venv venv
```

#### 2. Активируй виртуальное окружение:

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

#### 3. Установи зависимости:

```bash
pip install -r requirements.txt
```

#### 4. Создай `.env` файл:

```env
# .env
PORCUPINE_ACCESS_KEY=your_key_from_picovoice
NEWS_API_ACCESS_KEY=your_key_from_newsapi
```

#### 5. Запусти ассистента:

```bash
python main.py
```

---

### ⚙️ Основные настройки (`core/settings.py`)

| Параметр                            | Описание                                                |
| ----------------------------------- | ------------------------------------------------------- |
| `PORCUPINE_KEYWORDS`                | Ключевые слова для активации: по умолчанию `jarvis`     |
| `ONLINE_VOICE_RECOGNIZER_IS_ACTIVE` | Включить онлайн-распознавание речи (`True/False`)       |
| `TRIGGERS`                          | Дополнительные триггеры: `джарвис`, `djarvis`, `чарльз` |
| `VOSK_MODEL_PATH`                   | Путь до модели VOSK: `data/models/vosk`                 |
| `SILERO_TTS_SPEAKER`                | Голос TTS: `aidar`, `baya`, `omaz`, `xenia`, `jane`     |
| `LOGGER_ACTIVE`                     | Включить логирование (`True/False`)                     |
| `AUDIO_FILES`                       | Аудиофайлы приветствия, ответа, отказа и т.п.           |

---

### 🗣 Команды, которые понимает ассистент

#### 💻 Управление системой:

* «отключись»
* «перезагрузить компьютер»
* «выключи компьютер»
* «спящий режим»
* «сделай скриншот»
* «звук на максимум / минимум / отключи звук»

#### 🔍 Поиск:

* «поиск в интернете»
* «найди в википедии»
* «найди новости»

#### 📂 Приложения:

* «открой / закрой телеграм»
* «открой / закрой блокнот»
* «открой / закрой браузер»
* «включи / выключи музыку»

#### 👋 Приветствие:

* «привет», «здравствуй», «доброе утро» и др.

---

### 🔊 Озвучка и ответ

Ассистент использует [Silero TTS](https://github.com/snakers4/silero-models) для генерации речи и поддерживает голоса:

* `aidar`, `baya`, `jane`, `omaz`, `xenia`

Также проигрывает кастомные аудиоответы (например, `jarvis-og_run1.wav`, `jarvis-og_thanks.wav` и т.д.)

---

### 📁 Структура проекта

```
JARVIS/
├── core/
│   ├── settings.py         # Все настройки
│   ├── logger.py           # Логирование
│   └── words_data.py       # Команды
├── data/
│   ├── media/              # Аудиофайлы
│   └── models/             # Vosk модели
├── recognizer/             # Слушатель и распознавание речи
│   ├── porcupine_listener.py
│   ├── offline.py
│   └── online.py
├── skills/                 # Реализация команд
│   ├── apps/
│   ├── default/
│   ├── news/
│   ├── web/
│   ├── wiki/
│   └── youtube/
├── tts/
│   ├── silero_tts.py       # TTS через Silero
│   ├── pyttsx3_tts.py
│   └── audio_play.py
├── utils/                  # Вспомогательные функции
├── main.py                 # Главный файл запуска
├── requirements.txt
└── .env
```

---

### 🛡 Безопасность и лицензия

* [Лицензия](LICENSE)
* [Документация](docs/)
* [Установка](docs/instalations.md)

---

### ✅ План на будущее

* [ ] Добавить поддержку голосов Google TTS
* [ ] Поддержка Android / Linux
* [ ] Расширение навыков: управление Bluetooth, Wi-Fi и пр.
* [ ] Многопользовательская система

---

### 📣 Благодарности

* [VOSK](https://alphacephei.com/vosk/)
* [Silero Models](https://github.com/snakers4/silero-models)
* [Picovoice Porcupine](https://picovoice.ai/)
* [News API](https://newsapi.org)


