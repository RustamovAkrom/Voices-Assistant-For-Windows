# 🗣️ Voices Assistant For Windows

> 🚧 *Work in Progress — Голосовой ассистент на стадии активной разработки*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)
![Status](https://img.shields.io/badge/Status-Active_Development-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![AI](https://img.shields.io/badge/AI-Gemini_Integration-blueviolet?logo=google)

---

## 🌟 О проекте

**Voices Assistant For Windows** — это умный, многозадачный и живой голосовой ассистент,
который понимает речь на **трёх языках**: 🇷🇺 Русском, 🇺🇿 Узбекском и 🇬🇧 Английском.

Ассистент работает **онлайн и офлайн**,
умеет говорить **реалистичным голосом**,
использует **AI (Gemini)** для ответов на свободные вопросы
и даже воспроизводит **аудиоэффекты** из фильмов (например, из *Jarvis* 🎬).

---

## ⚙️ Основные возможности

### 🧠 Распознавание речи

* Онлайн через [`SpeechRecognition`](https://pypi.org/project/SpeechRecognition/)
* Оффлайн через [`Vosk`](https://pypi.org/project/vosk/)
* Поддержка 3 языков (RU / UZ / EN)
* Автоматическое определение языка (`langdetect`)
* Автоматическое переключение между online/offline при отсутствии интернета

### 🗣️ Озвучивание

* 🔊 `Silero TTS` — реалистичный синтез речи *(по умолчанию)*
* 🗣️ `pyttsx3` — офлайн-альтернатива
* 🎵 Воспроизведение WAV-файлов из `data/media/audios`

### 🤖 AI-интеграция (Gemini)

* Если команда не распознана — отправляется запрос в **Gemini**
* AI можно включать/отключать в настройках (`ai_enabled`)
* Требуется собственный API-ключ (`gemini_api_key`)
* Без ключа ассистент продолжит работать без AI

### 🧩 Расширения и навыки

* Каждый навык — отдельный Python-файл в `src/skills/`
* Возможность добавления собственных действий, логики и реакций

---

## 🗂️ Структура проекта

```
Voices-Assistant-For-Windows/
├── src/
│   ├── core/
│   │   ├── config.py
│   │   ├── recognizer.py
│   │   ├── tts.py
│   │   ├── executor.py
│   │   ├── skill_manager.py
│   │   └── utils.py
│   ├── skills/
│   │   ├── ai_skill.py        # Интеграция с Gemini
│   │   ├── system_skill.py    # Системные и базовые команды
│   │   └── ...
│   └── main.py
├── data/
│   ├── media/audios/          # Звуковые эффекты (например, Jarvis.wav)
│   └── datasets/
├── settings.yaml
└── README.md
```

---

## 📦 Основные зависимости

| Модуль                                                           | Назначение                     |
| :--------------------------------------------------------------- | :----------------------------- |
| [UV](https://docs.astral.sh/uv/)                                 | Современный менеджер окружений |
| [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) | Онлайн распознавание речи      |
| [Vosk](https://pypi.org/project/vosk/)                           | Оффлайн распознавание речи     |
| [Sounddevice](https://pypi.org/project/sounddevice/)             | Работа с микрофоном            |
| [RapidFuzz](https://pypi.org/project/RapidFuzz/)                 | Анализ похожести слов          |
| [PyYAML](https://pypi.org/project/PyYAML/)                       | Работа с конфигурацией         |
| [langdetect](https://pypi.org/project/langdetect/)               | Определение языка текста       |
| [numpy](https://pypi.org/project/numpy/)                         | Работа с массивами             |
| [pyttsx3](https://pypi.org/project/pyttsx3/)                     | Оффлайн синтез речи            |
| [gTTS](https://pypi.org/project/gTTS/)                           | Онлайн TTS (Google)            |
| [playsound](https://pypi.org/project/playsound/)                 | Воспроизведение аудио          |
| [torch](https://pypi.org/project/torch/)                         | Поддержка моделей Silero       |
| [soundfile](https://pypi.org/project/soundfile/)                 | Работа с аудиофайлами          |

---

## ⚙️ Установка

```bash
# Клонировать репозиторий
git clone https://github.com/username/Voices-Assistant-For-Windows.git
cd Voices-Assistant-For-Windows

# Создать виртуальное окружение и установить зависимости
uv sync
```

---

## 🧪 Запуск

```bash
uv run python src/main.py
```

---

## 🧰 Пример конфигурации (`settings.yaml`)

```yaml
assistant:
  default_language: "ru"
  mode: "online"
  voice_engine: "silero"   # или "pyttsx3"
  ai_enabled: true
  gemini_api_key: "ВАШ_API_КЛЮЧ"
  speech_rate: 160
  debug: true
```

---

## 🎧 Примеры команд

| Команда                   | Действие                          |
| :------------------------ | :-------------------------------- |
| “Привет, Джарвис”         | Воспроизводит приветственный звук |
| “Открой браузер”          | Выполняет системную команду       |
| “Что ты думаешь об этом?” | Отправляется в AI (Gemini)        |
| “Выключи компьютер”       | Завершает работу Windows          |

---

## 🔮 В планах

* 💡 Расширение AI-функций
* 📅 Напоминания и календарь
* 🎨 Графический интерфейс (GUI) для Windows
* 🔌 API для интеграции с внешними приложениями
* 🎙️ Поддержка горячего слова (“Hey Jarvis”)

---

## 👨‍💻 Автор

**Akrom** — разработчик, программист и студент,
создающий многофункционального и живого голосового ассистента.

📫 Контакты: [Telegram](https://t.me/) • [GitHub](https://github.com/)

---

## ⚠️ Примечание

> 🧪 Проект находится в **активной разработке**, возможны ошибки и недоработки.
> Пожалуйста, сообщайте об ошибках и предлагайте улучшения через **Issues** на GitHub ❤️

---

## 💬 Если хочешь помочь

⭐ Поставь звёздочку репозиторию,
💬 предложи идею или добавь новый навык —
вместе сделаем ассистента лучше!


 <!-- - [UV](https://docs.astral.sh/uv/) - Modern virtual environment
 - [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) - Online speach recognition
 - [Vosk](https://pypi.org/project/vosk/) - Offline speach recognition
 - [Sounddevice](https://pypi.org/project/sounddevice/) - For audio
 - [RapidFuzz](https://pypi.org/project/RapidFuzz/) - For checking words
 - [PyYAML](https://pypi.org/project/PyYAML/) - For load .yaml files
 - [langdetect](https://pypi.org/project/langdetect/) - For text language detection
 - [numpy](https://pypi.org/project/numpy/) - For array 
 - [pyttsx3](https://pypi.org/project/pyttsx3/) - For local text to speach
 - [gTTS](https://pypi.org/project/gTTS/) - gTTS (Google Text-to-Speech)
 - [playsound](https://pypi.org/project/playsound/) -  For playing sounds
 - [torch](https://pypi.org/project/torch/) - Tensor computation (like NumPy) with strong GPU acceleration
 - [soundfile](https://pypi.org/project/soundfile/) - For playing audio files -->
