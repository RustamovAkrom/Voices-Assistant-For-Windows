import queue
import sounddevice as sd
import vosk
import json
import words
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from speaker.silero_tts import Speaker


def recognize(data, vectorizer, clf):
    # Разбиваем входной текст на предложения/команды (по запятым, "и", точкам)
    import re
    commands = re.split(r'[,.!?;]|\s+и\s+', data)
    commands = [cmd.strip() for cmd in commands if cmd.strip()]

    from controllers import handlers
    from controllers import weather, time_service, music

    handlers_dict = {
        "reply_here": handlers.reply_here,
        "reply_greeting": handlers.reply_greeting,
        "reply_howareyou": handlers.reply_howareyou,
        "reply_skills": handlers.reply_skills,
        "reply_joke": handlers.reply_joke,
        "get_news": handlers.get_news,
        "get_location": handlers.get_location,
        "turn_on_light": handlers.turn_on_light,
        "turn_off_light": handlers.turn_off_light,
        "play_music": handlers.play_music,
        "stop_music": handlers.stop_music,
        "get_weather": weather.get_weather,
        "get_time": time_service.get_time,
        "get_music": music.get_music,
    }

    for cmd in commands:
        text_vector = vectorizer.transform([cmd]).toarray()[0]
        func_name = clf.predict([text_vector])[0]
        handler = handlers_dict.get(func_name)
        if handler:
            result = handler()
            print(f"[{cmd}] → {result}")
            speaker.say(result)
        else:
            print(f"[{cmd}] → Команда не реализована")


def traning_data(data_set:dict):
    # Подготовка обучающих данных
    X = []
    y = []
    for phrases, answer in words.data_set.items():
        for phrase in phrases:
            X.append(phrase)
            y.append(answer)

    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(X)

    clf = LogisticRegression()
    clf.fit(vectors, y)

    return vectorizer, clf

 
class OfflineRecognizer:
    def __init__(self):
        self.q = queue.Queue()
        self.model = vosk.Model("models/vosk")
        self.device = sd.default.device
        self.samplerate = int(sd.query_devices(self.device[0], 'input')['default_samplerate'])

    def callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def listen(self):
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, device=self.device[0], dtype='int16', channels=1, callback=self.callback):
            rec = vosk.KaldiRecognizer(self.model, self.samplerate)
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result['text']
                    return text

def main():
    vectorizer, clf = traning_data(words.data_set)

    start_time = time.time() - 1000

    while True:
        print("Ожидание активационного слова...")
        text = recognizer.listen().lower()
        print(f"Recognized text: {text}")

        trg = words.TRIGGERS.intersection(text.split())

        if trg:
            print("Активация! Jarvis слушает команды 15 секунд...")
            start_time = time.time()
            
            while (time.time() - start_time) <= 15:
                cmd_text = recognizer.listen()
                print(f"Recognized command: {cmd_text}")

                if cmd_text:
                    if any(t in cmd_text.split() for t in words.TRIGGERS):
                        print("да, сэр")
                        continue
                    recognize(cmd_text, vectorizer, clf)
                else:
                    print("Команда не распознана, повторите.")

                


if __name__ == "__main__":
    recognizer = OfflineRecognizer()
    speaker = Speaker()

    main()
