import torch
import requests
import sounddevice as sd
from pathlib import Path

try:
    import soundfile as sf
except ImportError:
    sf = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

class HybridTTS:
    """
    Гибридный синтезатор речи: Silero (offline) + pyttsx3 (offline) + аудиоэффекты.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.voice_enabled = self.config.get("voice_enabled", True)
        self.default_lang = self.config.get("assistant", {}).get("default_language", "ru")
        # Устройство вывода (GPU/CPU) учитывает настройку use_cuda
        self.device = "cuda" if torch.cuda.is_available() and self.config.get("silero", {}).get("use_cuda", True) else "cpu"

        self.models_dir = Path("data/models/tts")
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Поддерживаемые языки и соответствующие им модели Silero
        self.supported_langs = {
            "ru": "v3_1_ru",
            "en": "v3_en",
            "uz": "v3_uz",
        }
        self.silero_speakers = {
            "ru": ["aidar", "baya", "kseniya", "xenia", "eugene"],
            "en": ["en_0", "en_1", "en_2"],
            "uz": ["uz_0", "uz_1", "uz_2"],
        }

        self.current_lang = self.default_lang
        self.current_speaker = self.config.get("voice_speaker", "aidar")
        self.current_engine = self.config.get("voice_engine", "silero")

        self.model = None
        self._ensure_models_exist()
        self._load_model(self.current_lang)

        # Инициализация pyttsx3, если он есть
        self.engine = None
        if pyttsx3 is not None:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.config.get("voice_speed", 160))
            self.engine.setProperty("volume", self.config.get("voice_volume", 1.0))
            # Если задан пол голоса, пробуем подобрать (пример: женский => kseniya)
            voices = self.engine.getProperty("voices")
            gender = self.config.get("voice_gender", "female")
            for voice in voices:
                if gender.lower() in voice.name.lower():
                    self.engine.setProperty("voice", voice.id)
                    break

    def _ensure_models_exist(self):
        base_url = "https://models.silero.ai/models/tts"
        for lang, model_name in self.supported_langs.items():
            model_path = self.models_dir / f"{model_name}.pt"
            if not model_path.exists():
                print(f"⬇️ Скачиваю Silero модель ({model_name}) для {lang.upper()}...")
                try:
                    url = f"{base_url}/{lang}/{model_name}.pt"
                    r = requests.get(url, stream=True, timeout=15)
                    with open(model_path, "wb") as f:
                        f.write(r.content)
                    print(f"✅ Модель {model_name} установлена.")
                except Exception as e:
                    print(f"⚠️ Не удалось скачать модель {model_name}: {e}")

    def _load_model(self, lang: str):
        try:
            model_name = self.supported_langs.get(lang, "v3_1_ru")
            self.model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-models",
                model="silero_tts",
                language=lang,
                speaker=model_name
            )
            self.model.to(self.device)
            print(f"🎙️ Silero TTS загружен для языка {lang.upper()}.")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки Silero ({lang}): {e}")
            self.model = None
            # Если Silero не доступен, переключаемся на pyttsx3
            self.current_engine = "pyttsx3"

    def speak(self, text: str, lang: str = None, speaker: str = None, engine: str = None):
        """
        Говорит текст: Silero (offline) или pyttsx3.
        Если голос выключен, просто выводит текст в консоль.
        """
        if not text or not self.voice_enabled:
            print(f"🔊 {text}")
            return

        lang = lang or self.current_lang
        speaker = speaker or self.current_speaker
        engine = engine or self.current_engine

        # Попытка синтеза Silero
        if engine == "silero" and self.model:
            try:
                if speaker not in self.silero_speakers.get(lang, []):
                    speaker = self.silero_speakers[lang][0]
                print(f"🗣️ [{lang.upper()}:{speaker}] {text}")
                audio = self.model.apply_tts(
                    text=text,
                    speaker=speaker,
                    sample_rate=self.config.get("silero", {}).get("sample_rate", 48000),
                    put_accent=True,
                    put_yo=True,
                )
                sd.play(audio, self.config.get("silero", {}).get("sample_rate", 48000))
                sd.wait()
                return
            except Exception as e:
                print(f"[Silero error] {e}")
                engine = "pyttsx3"

        # Фоллбэк на pyttsx3
        if self.engine and engine == "pyttsx3":
            print(f"🔊 [pyttsx3] {text}")
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[TTS error] {e}")

    def play_audio_file(self, file_path: Path):
        """
        Проигрывает WAV-файл (например, аудиоклип из data/media/audios).
        """
        if not file_path.exists():
            print(f"⚠️ Аудиофайл не найден: {file_path}")
            return
        if sf is None:
            print(f"⚠️ Для воспроизведения нужен модуль soundfile.")
            return
        try:
            data, fs = sf.read(str(file_path))
            sd.play(data, fs)
            sd.wait()
        except Exception as e:
            print(f"⚠️ Ошибка при воспроизведении {file_path}: {e}")

    def set_language(self, lang: str):
        if lang not in self.supported_langs:
            print(f"⚠️ Язык {lang} не поддерживается.")
            return
        self.current_lang = lang
        self._load_model(lang)

    def set_voice(self, speaker: str):
        self.current_speaker = speaker
        print(f"🎤 Голос изменён на: {speaker}")

    def set_engine(self, engine: str):
        if engine not in ("silero", "pyttsx3"):
            print(f"⚠️ Неизвестный движок: {engine}")
            return
        self.current_engine = engine
        print(f"⚙️ TTS-движок: {engine}")

    def test(self):
        # Пример теста всех режимов
        self.speak("Привет, я офлайн-ассистент!", "ru", "baya", "silero")
        self.speak("Hello, I can speak English!", "en", "en_1", "silero")
        self.speak("Salom, men O'zbek tilida gapira olaman!", "uz", "uz_2", "silero")
