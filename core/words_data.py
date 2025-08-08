DEFAULT_DATA = [
    # Exit program
    {
        "phrases": [
            "отключись",
            "на сегодня хватит",
            "хватит на сегодня",
            "хватит",
            "отключись пожалуйста",
            "отключись на сегодня",
            "на сегодня хватит",
        ],
        "handler": "default.windows.exit_programm.exit_handle",
        "param": False,
    },
    # Restart PK
    {
        "phrases": ["перезагрузить компьютер"],
        "handler": "default.windows.restart.restart_windows",
        "param": False,
    },
    # Shutdown PK
    {
        "phrases": ["выключи компьютер"],
        "handler": "default.windows.shutdown.shutdown_windows",
        "param": False,
    },
    # Sleep PK
    {
        "phrases": ["спящий режим"],
        "handler": "default.windows.sleep.sleep_windows",
        "param": False,
    },
    # Do Screenshot
    {
        "phrases": [
            "сделай скриншот",
            "скриншот",
        ],
        "handler": "default.windows.screen.screenshot_windows",
        "param": False,
    },
    # Set volume max
    {
        "phrases": [
            "звук на максимум",
            "увеличь громкость",
            "звук компьютера на максимум",
        ],
        "handler": "default.windows.volumes.set_volume_max",
        "param": False,
    },
    # Set volume mid
    {
        "phrases": ["звук на минимум", "нормальный звук", "звук компьютера на минимум"],
        "handler": "default.windows.volumes.set_volume_mid",
        "param": False,
    },
    # Set volume min
    {
        "phrases": [
            "отключить звук",
            "выключи звук",
            "отключения звука",
            "тихие режим",
        ],
        "handler": "default.windows.volumes.set_volume_min",
        "param": False,
    },
    # Clear recycle bin
    {
        "phrases": [
            "очистить корзинку",
            "очистки корзинку",
            "очисти корзинку",
        ],
        "handler": "default.windows.cleaner.clear_recycle_bin",
        "param": False,
    },
    {
        "phrases": [
            "очисти ненужные файлы",
            "очисти временные файлы",
        ],
        "handler": "default.windows.cleaner.clear_temp_folder",
        "param": False,
    },
    {
        "phrases": [
            "очисти компьютер",
            "очистить загрузки",
        ],
        "handler": "default.windows.cleaner.clear_downloads_except_import",
        "param": False,
    },
    {
        "phrases": [
            "очисти компьютер",
            "удалить все нужные файлы с компьютера",
            "давай очистим компьютер",
        ],
        "handler": "default.windows.cleaner.clear_all_files",
        "param": False,
    },
]

ANSWERS_TO_WORDS_DATA = [
    {
        "phrases": [
            "привет",
            "здравствуй",
            "доброе утро",
            "добрый день",
            "добрый вечер",
            "приветик",
            "приветствую",
            "здарова",
            "хай",
            "добрейшего времени суток",
        ],
        "handler": "default.answers.simple.simple_answer",
        "param": False,
    },
    # 
]

SEARCH_DATA = [
    # Search in web
    {
        "phrases": [
            "открой в браузере",
            "открой браузере",
            "поиск в интернете",
            "поиск в сети",
            "поиск информации",
            "найди информацию",
            "найди в интернете",
            "поиск в интернете",
            "поиск информации в интернете",
            "найти информацию",
            "найти в интернете кто такой",
            "поищи в интернете",
        ],
        "handler": "web.search_web",
        "param": True,
    },
    # Search in Wikipedia
    {
        "phrases": [
            "найди в википедии",
            "поиск в википедии",
            "узнай википедию",
            "расскажи о",
            "расскажи про",
            "расскажи что такое",
        ],
        "handler": "wiki.search_wiki",
        "param": True,
    },
    # Search news
    {
        "phrases": [
            "найди новости",
            "поиск новостей",
            "последние новости",
            "что нового в",
            "что говорят про",
            "что слышно о",
            "новости про",
            "расскажи новости",
            "узнай что происходит",
            "узнать что происходит в",
            "ищи новости",
            "ищи инфу",
            "что в новостях",
            "поиск информации",
            "есть ли новости про",
            "расскажи о",
            "что пишут о",
            "найди инфу",
            "что известно про",
        ],
        "handler": "news.search_news",
        "param": True,
    },
]

APPS_DATA = [
    # Telegram
    {
        "phrases": [
            "открой телеграм",
            "запусти телеграм",
            "запусти телеграф",
            "открой телеграф",
        ],
        "handler": "apps.telegram.open_telegram",
        "param": False,
    },
    {
        "phrases": [
            "закрой телеграм",
            "выключи телеграм",
            "закрой телеграф",
            "выключи телеграф",
        ],
        "handler": "apps.telegram.close_telegram",
        "param": False,
        "text": "Закрываю приложение...",
    },
    # Notepad
    {
        "phrases": [
            "открой блокнот",
            "запусти блокнот",
            "запусти ноутпад",
            "открой ноутпад",
        ],
        "handler": "apps.notepad.open_notepad",
        "param": False,
    },
    {
        "phrases": [
            "закрой блокнот",
            "выключи блокнот",
            "закрой ноутпад",
            "выключи ноутпад",
        ],
        "handler": "apps.notepad.close_notepad",
        "param": False,
        "text": "Закрываю приложение...",
    },
    # Browser
    {
        "phrases": [
            "открой гугл",
            "запусти гугл",
            "запусти хром",
            "открой хром",
            "открой браузер",
            "запусти браузер",
        ],
        "handler": "apps.browser.open_browser",
        "param": False,
    },
    {
        "phrases": [
            "закрой гугл",
            "выключи гугл",
            "закрой хром",
            "выключи хром",
            "закрой браузер",
            "выключи браузер",
        ],
        "handler": "apps.browser.close_browser",
        "param": False,
        "text": "Закрываю приложение...",
    },
    # Music
    {
        "phrases": [
            "открой музыку",
            "запусти музыку",
            "запусти музыку",
            "открой музыку",
            "открой музыку",
            "запусти музыку",
            "включи музыку",
            "включи песню",
            "поставь музыку",
            "давай музыку",
            "музыку включи",
            "музыку поставь",
            "музыку давай",
            "воспроизведи музыку",
            "поставь другую музыку",
        ],
        "handler": "apps.music.open_music",
        "param": False,
    },
    {
        "phrases": [
            "закрой музыку",
            "выключи музыку",
            "закрой музыку",
            "закрой музыку",
            "останови музыку",
            "прекрати музыку",
            "музыку выключи",
            "музыку останови",
            "музыку прекрати",
            "останови песню",
            "выключи песню",
        ],
        "handler": "apps.music.close_music",
        "param": False,
        "text": "Закрываю приложение...",
    },
]

data_set = []
data_set += DEFAULT_DATA
data_set += ANSWERS_TO_WORDS_DATA
data_set += SEARCH_DATA
data_set += APPS_DATA
