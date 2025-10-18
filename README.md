 - [UV](https://docs.astral.sh/uv/) - Modern virtual environment
 - [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) - Online speach recognition
 - [Vosk](https://pypi.org/project/vosk/) - Offline speach recognition
 - [Sounddevice](https://pypi.org/project/sounddevice/) - For audio
 - [RapidFuzz](https://pypi.org/project/RapidFuzz/) - For checking words
 - [PyYAML](https://pypi.org/project/PyYAML/) - For load .yaml files
 - [pyttsx3](https://pypi.org/project/pyttsx3/) - For local text to speach
  
 + 🎤 Пользователь говорит →
 + 🎧 Listener записывает звук →
 + 🧠 Recognizer превращает речь в текст →
 + 🔍 Executor анализирует текст и ищет совпадение со skill →
 + ⚙️ Skill выполняет команду →
 + 🗣️ TTS озвучивает ответ


```bash
+------------------+
|  🎤 Listener     |
|  (запись звука)  |
+--------+---------+
         |
         v
+------------------+
|  🧠 Recognizer   |
|  (speech → text) |
+--------+---------+
         |
         v
+------------------+
|  ⚙️ Executor     |
|  (поиск skill)   |
+--------+---------+
         |
         v
+------------------+
|  💡 SkillLoader  |
|  (вызов функции) |
+--------+---------+
         |
         v
+------------------+
|  🗣️  TTS Output  |
|  (ответ голосом) |
+------------------+
```