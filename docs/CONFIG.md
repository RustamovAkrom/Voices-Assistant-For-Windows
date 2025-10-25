# ⚙️ Документация по `config.yaml`

Файл `config.yaml` — это **основной конфигурационный файл ассистента**.
Он управляет всеми глобальными настройками: голосом, распознаванием, языками, режимами, путями, API-ключами и пр.

Каждый параметр можно менять без изменения кода — ассистент автоматически применяет новые настройки при запуске или перезагрузке.

---

## 🗂️ Общая структура

```yaml
# === Основные настройки голоса ===
voice_enabled: true
voice_engine: "silero"
voice_speed: 180
voice_volume: 1.0
voice_gender: "female"
voice_speaker: "aidar"

# === Настройки распознавания ===
language: "ru-RU"
wake_word: "джарвис"
wake_words:
  ru: ["джарвис", "жарвис"]
  en: ["jarvis", "hey jarvis"]
  uz: ["jarvis", "jarvisjon"]

# === Настройки ассистента ===
assistant:
  name: "Jarvis"
  default_language: "ru"
  voice: "default"
  personality: "friendly"
  gemeni_enabled: false
  gemeni_api_key: ""

# === Режимы работы ===
debug: true
offline_mode: true
auto_switch_mode: true

# === Папки и ресурсы ===
paths:
  datasets: "data/commands.yaml"
  tts_models: "data/models/tts"
  stt_models: "data/models/stt"
  cache_dir: "data/cache"

# === Дополнительно ===
silero:
  ru_speakers: ["aidar", "baya", "kseniya", "xenia", "eugene"]
  en_speakers: ["en_0", "en_1", "en_2"]
  uz_speakers: ["uz_0", "uz_1", "uz_2"]
  sample_rate: 48000
  use_cuda: true
```

---

## 🎙️ Раздел 1: Основные настройки голоса

Этот блок управляет **синтезом речи (Text-to-Speech)**.

| Параметр        | Тип     | Значение по умолчанию | Описание                                                                                                      |
| --------------- | ------- | --------------------- | ------------------------------------------------------------------------------------------------------------- |
| `voice_enabled` | `bool`  | `true`                | Включает или выключает озвучку ответов ассистента                                                             |
| `voice_engine`  | `str`   | `"silero"`            | Определяет TTS-движок: `"silero"` — реалистичный офлайн-голос, `"pyttsx3"` — стандартный офлайн               |
| `voice_speed`   | `int`   | `180`                 | Скорость речи (для `pyttsx3`), чем выше — тем быстрее                                                         |
| `voice_volume`  | `float` | `1.0`                 | Громкость (0.0 — тише, 1.0 — максимум)                                                                        |
| `voice_gender`  | `str`   | `"female"`            | Гендер голоса: `"male"` или `"female"`                                                                        |
| `voice_speaker` | `str`   | `"aidar"`             | Имя конкретного диктора для Silero. Поддерживаются `aidar`, `baya`, `kseniya`, `eugene`, `en_0`, `uz_0` и др. |

📘 **Пример: смена диктора и скорости**

```yaml
voice_enabled: true
voice_engine: "silero"
voice_speaker: "baya"
voice_speed: 190
```

💡 **Совет:**

* Silero звучит реалистично и не требует интернета.
* Для английского или узбекского языка указывай спикеров из соответствующего списка (`en_speakers`, `uz_speakers`).

---

## 🧠 Раздел 2: Настройки распознавания речи (STT)

| Параметр     | Тип    | Описание                                                                  |
| ------------ | ------ | ------------------------------------------------------------------------- |
| `language`   | `str`  | Язык распознавания по умолчанию, например `"ru-RU"`, `"en-US"`, `"uz-UZ"` |
| `wake_word`  | `str`  | Основное слово-пробуждение для активации ассистента                       |
| `wake_words` | `dict` | Список вариантов для разных языков                                        |

📘 **Пример:**

```yaml
language: "en-US"
wake_word: "jarvis"
wake_words:
  en: ["jarvis", "hey jarvis", "ok jarvis"]
```

💡 **Совет:**
Добавляй варианты произношения — это улучшит точность пробуждения.
Ассистент может активироваться по любому слову из списка `wake_words[текущий_язык]`.

---

## 🤖 Раздел 3: Настройки ассистента

| Параметр                     | Тип    | Описание                                                                                              |
| ---------------------------- | ------ | ----------------------------------------------------------------------------------------------------- |
| `assistant.name`             | `str`  | Имя ассистента, используемое в ответах или UI                                                         |
| `assistant.default_language` | `str`  | Язык по умолчанию (`ru`, `en`, `uz`)                                                                  |
| `assistant.voice`            | `str`  | Какой голос использовать (например, `"default"`, `"male"`, `"female"`)                                |
| `assistant.personality`      | `str`  | Личность ассистента: `"friendly"`, `"professional"`, `"funny"` — можно использовать для стиля общения |
| `assistant.gemeni_enabled`   | `bool` | Включить поддержку **Gemini / LLM-API**                                                               |
| `assistant.gemeni_api_key`   | `str`  | Ключ для подключения к Gemini или другому AI-провайдеру                                               |

📘 **Пример: включение Gemini**

```yaml
assistant:
  name: "Jarvis"
  default_language: "en"
  personality: "professional"
  gemeni_enabled: true
  gemeni_api_key: "YOUR_API_KEY_HERE"
```

💡 **Совет:**
При активном `gemeni_enabled` ассистент будет использовать онлайн-мозг (AI) для сложных вопросов.
В офлайн-режиме он будет работать с локальными скиллами.

---

## ⚡ Раздел 4: Режимы работы

| Параметр           | Тип    | Описание                                                      |
| ------------------ | ------ | ------------------------------------------------------------- |
| `debug`            | `bool` | Включает подробные логи в консоль                             |
| `offline_mode`     | `bool` | Работает только с локальными модулями без интернета           |
| `auto_switch_mode` | `bool` | Автоматически переключает онлайн/офлайн при потере соединения |

📘 **Пример: отладочный офлайн-режим**

```yaml
debug: true
offline_mode: true
auto_switch_mode: true
```

💡 **Совет:**
В продакшене лучше выключать `debug`, чтобы ускорить работу.
Если `auto_switch_mode = true`, ассистент будет сам включать офлайн-режим при отсутствии сети.

---

## 📁 Раздел 5: Пути и ресурсы

Указывает, где находятся модели и файлы данных.

| Параметр           | Тип   | Описание                                 |
| ------------------ | ----- | ---------------------------------------- |
| `paths.datasets`   | `str` | Путь к `commands.yaml`                   |
| `paths.tts_models` | `str` | Папка с моделями Silero                  |
| `paths.stt_models` | `str` | Папка с моделями распознавания речи      |
| `paths.cache_dir`  | `str` | Временный кэш для хранения аудио и логов |

📘 **Пример:**

```yaml
paths:
  datasets: "data/commands.yaml"
  tts_models: "data/models/tts"
  stt_models: "data/models/stt"
  cache_dir: "data/cache"
```

💡 **Совет:**
Можно указать абсолютные пути, если ассистент запускается как системный сервис.
При разработке достаточно относительных (`data/...`).

---

## 🧬 Раздел 6: Дополнительные настройки Silero

| Параметр             | Тип         | Описание                                                        |
| -------------------- | ----------- | --------------------------------------------------------------- |
| `silero.ru_speakers` | `list[str]` | Русские спикеры (`aidar`, `baya`, `kseniya`, `xenia`, `eugene`) |
| `silero.en_speakers` | `list[str]` | Английские спикеры (`en_0`, `en_1`, `en_2`)                     |
| `silero.uz_speakers` | `list[str]` | Узбекские спикеры (`uz_0`, `uz_1`, `uz_2`)                      |
| `silero.sample_rate` | `int`       | Частота дискретизации аудио (обычно `48000`)                    |
| `silero.use_cuda`    | `bool`      | Использовать GPU, если доступно                                 |

📘 **Пример:**

```yaml
silero:
  ru_speakers: ["aidar", "baya", "kseniya"]
  en_speakers: ["en_0", "en_1"]
  uz_speakers: ["uz_0", "uz_1"]
  sample_rate: 48000
  use_cuda: true
```

💡 **Совет:**
Если у тебя есть GPU (NVIDIA), включи `use_cuda: true` — это ускорит синтез голоса почти в 2-3 раза.
Если работаешь на CPU — оставь `false`.

---

## 🧭 Как ассистент использует `config.yaml` в коде

```python
import yaml

def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config

config = load_config()

if config["voice_enabled"]:
    print(f"🔊 Voice engine: {config['voice_engine']}")
if config["debug"]:
    print("🧩 Debug mode ON")
```

Ассистент подгружает настройки при старте,
и передаёт `config` в каждый модуль (через `**kwargs`).

---

## ✅ Резюме

| Раздел                       | Назначение                        |
| ---------------------------- | --------------------------------- |
| **Голосовые параметры**      | Управление синтезом речи          |
| **Распознавание речи (STT)** | Языки и пробуждение               |
| **Настройки ассистента**     | Имя, язык, личность, API-ключи    |
| **Режимы работы**            | Debug, офлайн и авто-переключение |
| **Пути и ресурсы**           | Расположение моделей и данных     |
| **Silero**                   | Параметры для TTS-движка          |

