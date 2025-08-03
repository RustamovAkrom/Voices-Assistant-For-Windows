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

**Step 4.** Finally you can run project with command:
```
python main.py
```
