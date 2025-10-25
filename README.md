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

📚 Дополнительная документация:

* [📘 Описание команд (`commands.yaml`)](docs/COMMANDS.md)
* [⚙️ Конфигурация ассистента (`config.yaml`)](docs/CONFIG.md)

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

| Аргумент       | Тип   | Описание                                               |
| :------------- | :---- | :----------------------------------------------------- |
| `*args`        | tuple | Позиционные аргументы, если они были переданы напрямую |
| `**kwargs`     | dict  | Все служебные данные                                   |
| → `query`      | str   | Распознанный текст пользователя                        |
| → `dataset`    | dict  | Загруженный `commands.yaml`                            |
| → `language`   | str   | Текущий язык ассистента                                |
| → `config`     | dict  | Основная конфигурация из `config.yaml`                 |
| → `tts`        | obj   | Синтезатор речи                                        |
| → `ai`         | obj   | Экземпляр AI (Gemini)                                  |
| → `recognizer` | obj   | Распознаватель речи                                    |

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

## 📘 Добавление новых функций (`commands.yaml`)

Каждый блок в `data/commands.yaml` описывает **навык (skill)** и связанные с ним команды.
Ассистент автоматически определяет, какая функция Python должна выполниться при совпадении паттерна.

Пример:

```yaml
skills:
  system:
    description: "Системные команды"
    commands:
      - patterns:
          - "открой браузер"
          - "запусти chrome"
        action: "open_browser"

  weather:
    description: "Погода"
    commands:
      - patterns:
          - "погода в {city}"
        action: "get_weather"
        args:
          - "{city}"
```

📖 Подробное руководство:
➡️ [docs/COMMANDS.md](docs/COMMANDS.md)

---

## ⚙️ Конфигурация (`config.yaml`)

Все настройки хранятся в `data/config.yaml`:

```yaml
assistant:
  default_language: "ru"
  mode: "online"
  voice_engine: "silero"
  ai_enabled: true
  gemini_api_key: "ВАШ_API_КЛЮЧ"
  voice_speed: 160
  voice_volume: 1.0
  debug: true

silero:
  use_cuda: true
  sample_rate: 48000
```

📖 Подробное руководство:
➡️ [docs/CONFIG.md](docs/CONFIG.md)


---

## 🎙️ Примеры команд
| Команда                               | Действие             |
| :------------------------------------ | :------------------- |
| “Привет, Джарвис”                     | Запуск ассистента    |
| “Открой браузер”                      | Системная команда    |
| “Переведи ‘Как дела?’ на английский”  | Перевод текста       |
| “Найди в интернете погоду в Ташкенте” | Поиск в браузере     |
| “Останови работу”                     | Завершает ассистента |

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
