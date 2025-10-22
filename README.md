# 🧠 Voices Assistant for Windows

> 🚀 Умный голосовой ассистент с поддержкой AI, офлайн/онлайн распознаванием и реалистичным синтезом речи.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)
![Status](https://img.shields.io/badge/Status-Active_Development-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![AI](https://img.shields.io/badge/AI-Gemini_Integration-blueviolet?logo=google)
![banner](/data/media/banner.webp)

---

## 🌟 О проекте

**Voices Assistant for Windows** — это гибридный голосовой ассистент, вдохновлённый *Jarvis* из Marvel.  
Он понимает речь на **🇷🇺 русском**, **🇺🇿 узбекском** и **🇬🇧 английском** языках,  
умеет говорить **реалистичным голосом** через `Silero TTS`,  
распознавать команды **онлайн и офлайн**,  
и общаться с помощью **AI (Gemini)** 🤖.

Ассистент поддерживает **локальный режим без интернета**,  
а также имеет **интеллектуальную озвучку, навыки и гибкую систему конфигурации**.

---

## ⚙️ Основные возможности

### 🧠 Распознавание речи
- 🎤 Онлайн через [`SpeechRecognition`](https://pypi.org/project/SpeechRecognition/)
- 📴 Оффлайн через [`Vosk`](https://pypi.org/project/vosk/)
- 🌍 Автоматическое определение языка (`langdetect`)
- 🔄 Автоматическое переключение между online/offline режимами
- ⚙️ Поддержка трёх языков (RU / UZ / EN)

### 🗣️ Озвучивание речи
- 🔊 **Silero TTS** — реалистичный синтез речи (через `torch`)
- 🗣️ **pyttsx3** — офлайн-альтернатива
- 🎧 **tqdm**-индикатор загрузки моделей Silero
- 🎵 Воспроизведение WAV-файлов из `data/media/audios`
- 🧩 Автоматическое переключение между движками при ошибках

### 🤖 AI-интеграция (Gemini)
- Если команда не распознана — запрос отправляется в **Gemini**
- Возможность включать/выключать AI (`ai_enabled`)
- Поддержка пользовательского API-ключа (`gemini_api_key`)
- Продвинутая логика ответов и обработка естественной речи

### 🧩 Расширения и навыки
- Каждый навык — отдельный Python-модуль в `src/skills/`
- Можно добавлять свои команды, действия и контекстные реакции
- Простая интеграция новых функций (например, системных команд, поиска и т.д.)

---

## 🗂️ Структура проекта

```bash

Voices-Assistant-For-Windows/
├── src/
│   ├── core/
│   │   ├── config.py          # Загрузка и управление конфигурацией
│   │   ├── recognizer.py      # Распознавание речи (SpeechRecognition/Vosk)
│   │   ├── tts.py             # Гибридный TTS (Silero + pyttsx3)
│   │   ├── executor.py        # Выполнение команд
│   │   ├── skill_manager.py   # Менеджер навыков
│   │   └── ...
│   ├── utils/                 # Вспомогательные функции
│   ├── skills/
│   │   ├── ai_skill.py        # Интеграция с Gemini AI
│   │   ├── system_skill.py    # Системные команды Windows
│   │   └── ...
│   └── main.py                # Точка входа
│
├── data/
│   ├── media/audios/          # Звуковые эффекты (например, Jarvis.wav)
│   ├── models/tts/            # Модели Silero TTS
│   ├── commands.yaml          # Команды и синонимы
│   └── config.yaml            # Основные настройки
│
├── .venv/
├── pyproject.toml
└── README.md

````

---

## 📦 Основные зависимости


| Модуль | Назначение |
| :-- | :-- |
| [UV](https://docs.astral.sh/uv/) | Современный менеджер окружений |
| [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) | Онлайн распознавание речи |
| [Vosk](https://pypi.org/project/vosk/) | Оффлайн распознавание речи |
| [Sounddevice](https://pypi.org/project/sounddevice/) | Работа с микрофоном и аудио |
| [RapidFuzz](https://pypi.org/project/RapidFuzz/) | Сравнение строк и команд |
| [PyYAML](https://pypi.org/project/PyYAML/) | Работа с YAML-конфигурацией |
| [langdetect](https://pypi.org/project/langdetect/) | Определение языка текста |
| [numpy](https://pypi.org/project/numpy/) | Работа с аудио-данными |
| [pyttsx3](https://pypi.org/project/pyttsx3/) | Локальный синтез речи |
| [gTTS](https://pypi.org/project/gTTS/) | Онлайн синтез речи (Google) |
| [torch](https://pypi.org/project/torch/) | Поддержка моделей Silero |
| [soundfile](https://pypi.org/project/soundfile/) | Чтение/воспроизведение WAV |
| [tqdm](https://pypi.org/project/tqdm/) | Прогресс-бар при загрузке моделей |

---

## ⚙️ Установка

```bash
# Клонировать репозиторий
git clone https://github.com/RustamovAkrom/Voices-Assistant-For-Windows.git
cd Voices-Assistant-For-Windows

# Создать виртуальное окружение и установить зависимости
uv venv .venv
.venv\Scripts\activate
uv sync
````

---

## 🧪 Запуск

```bash
uv run python main.py
```

Ассистент автоматически:

* загрузит модели Silero (если их нет),
* определит доступ к интернету,
* выберет оптимальный движок TTS,
* и начнёт слушать голосовые команды 🎧

---

## 🧰 Пример конфигурации (`data/config.yaml`)

```yaml
assistant:
  default_language: "ru"
  mode: "online"
  voice_engine: "silero"    # или "pyttsx3"
  ai_enabled: true
  gemini_api_key: "ВАШ_API_КЛЮЧ"
  voice_speed: 160
  voice_volume: 1.0
  debug: true

silero:
  use_cuda: true
  sample_rate: 48000
```

---

## 🎙️ Примеры команд

| Команда                        | Действие                    |
| :----------------------------- | :-------------------------- |
| “Привет, Джарвис”              | Приветствие и запуск        |
| “Открой браузер”               | Выполняет системную команду |
| “Что ты думаешь об этом?”      | Отправляет запрос в AI      |
| “Выключи компьютер”            | Завершает работу Windows    |
| “Переключи язык на английский” | Меняет язык речи            |

---

## 🔮 В планах

* 💡 Расширение AI-функций
* 🧭 Контекстные диалоги и память
* 🗓️ Напоминания и расписание
* 🎨 Графический интерфейс (GUI)
* 🧩 Плагины и кастомные навыки
* 🔊 Горячее слово “Hey Jarvis”
* ☁️ Интеграция с внешними API

---

## 👨‍💻 Автор

**Akrom** — программист, парикмахер и студент,
создающий умного голосового ассистента,
способного понимать, говорить и взаимодействовать с Windows 🧠💬

📫 **Контакты:**
[🐙 GitHub](https://github.com/RustamovAkrom) • [💬 Telegram](https://t.me/Akrom_Rustamov)

---

## ⚠️ Примечание

> 🧪 Проект находится в активной разработке.
> Возможны ошибки и недоработки.
> Если нашёл баг или хочешь помочь — создавай Issue или Pull Request ❤️

---

## ⭐ Поддержи проект

Если тебе нравится идея —
⭐ поставь звёздочку репозиторию
и помоги развивать **Jarvis Assistant** дальше!
