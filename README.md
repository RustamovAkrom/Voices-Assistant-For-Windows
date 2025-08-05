## Jarvis Voices Asistent


**Fast start**

**Step 1.** Create virutal environment

```
python -m venv venv
```

**Step 2.** If your operations system Windows:
```
venv\Scripts\activate
```
or Linux:
```
source venv/bin/activate
```

**Step 3.** Install required modules
```
pip install -r requirements.txt
```

**Step 4.** After all create `.env` file in your directory project and get access key from platform [PicoVoice](https://picovoice.ai/platform/porcupine/):

 - After that, you must replace access_key to your key from picovoice which you get in `.env` file

```sh
# /.env
PORCUPINE_ACCESS_KEY=access_key

```
**Step 5.** Finally you can run project with command:
```
python main.py
```

**Step 6 (Optional).** If Commands are not worked correct you should be update path of apps in direcotry [skills/apps/](skills/apps/) One of example:

```py
# skills/apps/browser.py
import os


def open_browser():
    path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" # <--- Replace to directory of your music collections path
    os.startfile(path)


# ...
```
So that, every file you can update path of directories which will work correct in your computer.

## How can use settings:
In [/core/settings.py](/core/settings.py) you can replace voice to other voices for example: `aidar`, `baya`, `jane`, `omaz`, `xenia`. Also, replace activation name which you want. All instructions already wrote in [settings.py](/core/settings.py)

 + ### [License](LICENSE) 
 + ### [Security](SECURITY.md)
 + ### [Documentations](docs/)
 + ### [Instalations](docs/instalations.md)

