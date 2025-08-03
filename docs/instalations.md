### 1. Clone repository
```sh
git clone https://github.com/RustamovAkrom/Jarvis.git
```
### 2. Create virtual environment and activate
Windows:

```sh
python -m venv venv
venv\Scripts\activate
```

Linux:
```sh
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencias
Windows:
```sh
pip install -r requirements.txt
```

Linux:
```sh
pip3 install -r requirements.txt
```

### 4. After you must register in site [PicoVoice](https://picovoice.ai/platform/porcupine/) and get access key. While you need create `.env` file inside directory and add access key, for example:
```sh
#!/bin/bash
# This is an example .env file for the script
# Set the path to the directory where the script is located
# you must get access key from https://picovoice.ai/platform/porcupine/
PORCUPINE_ACCESS_KEY=your_access_key # There need your access key from PicoVoice