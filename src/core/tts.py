import torch
import requests
import sounddevice as sd
from pathlib import Path


try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class HybridTTS:
    """
    Многофункциональный TTS:
    - Поддерживает Silero (офлайн, RU/EN/UZ)
    - Поддерживает pyttsx3 (офлайн fallback)
    - Автоматически подгружает модели
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.voice_enabled = self.config.get("voice_enabled", True)
        self.default_lang = self.config.get("assistant", {}).get("default_language", "ru")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models_dir = Path("data/models/tts")
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Список поддерживаемых языков и моделей
        self.supported_langs = {
            "ru": "v3_1_ru",
            "en": "v3_en",
            "uz": "v3_uz",
        }

        # Настройки Silero
        self.silero_speakers = {
            "ru": ["aidar", "baya", "kseniya", "xenia", "eugene"],
            "en": ["en_0", "en_1", "en_2"],
            "uz": ["uz_0", "uz_1", "uz_2"],
        }

        self.current_lang = self.default_lang
        self.current_speaker = self.config.get("voice_speaker", "baya")
        self.current_engine = "silero"  # или "pyttsx3"

        # Модель Silero
        self.model = None
        self._ensure_models_exist()
        self._load_model(self.current_lang)

        # pyttsx3 fallback
        self.engine = None
        if pyttsx3 is not None:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.config.get("speech_rate", 160))

    # === Проверка и загрузка Silero моделей ===
    def _ensure_models_exist(self):
        base_url = "https://models.silero.ai/models/tts"
        for lang, model_name in self.supported_langs.items():
            model_path = self.models_dir / f"{model_name}.pt"
            if not model_path.exists():
                print(f"⬇️ Скачиваю Silero модель для {lang.upper()}...")
                try:
                    url = f"{base_url}/{lang}/{model_name}.pt"
                    r = requests.get(url, stream=True, timeout=15)
                    with open(model_path, "wb") as f:
                        f.write(r.content)
                    print(f"✅ Модель {model_name} установлена.")
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки модели {lang.upper()}: {e}")

    # === Загрузка модели Silero ===
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

    # === Говорит текст ===
    def speak(self, text: str, lang: str = None, speaker: str = None, engine: str = None):
        if not self.voice_enabled or not text.strip():
            print(f"🔊 {text}")
            return

        lang = lang or self.current_lang
        speaker = speaker or self.current_speaker
        engine = engine or self.current_engine

        # если Silero недоступен → fallback на pyttsx3
        if engine == "silero" and self.model:
            try:
                if speaker not in self.silero_speakers.get(lang, []):
                    speaker = self.silero_speakers[lang][0]
                print(f"🗣️ [{lang.upper()}:{speaker}] {text}")
                audio = self.model.apply_tts(
                    text=text,
                    speaker=speaker,
                    sample_rate=48000,
                    put_accent=True,
                    put_yo=True,
                )
                sd.play(audio, 48000)
                sd.wait()
                return
            except Exception as e:
                print(f"[Silero error] {e}")
                engine = "pyttsx3"

        # fallback → pyttsx3
        if self.engine and engine == "pyttsx3":
            print(f"🔊 [pyttsx3] {text}")
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[TTS fallback error] {e}")

    # === Быстрое переключение языка ===
    def set_language(self, lang: str):
        if lang not in self.supported_langs:
            print(f"⚠️ Язык {lang} не поддерживается.")
            return
        self.current_lang = lang
        self._load_model(lang)

    # === Быстрое переключение голоса ===
    def set_voice(self, speaker: str):
        self.current_speaker = speaker
        print(f"🎤 Голос изменён на: {speaker}")

    # === Быстрое переключение движка ===
    def set_engine(self, engine: str):
        if engine not in ("silero", "pyttsx3"):
            print(f"⚠️ Неизвестный движок: {engine}")
            return
        self.current_engine = engine
        print(f"⚙️ TTS-движок: {engine}")

    # === Тест ===
    def test(self):
        self.speak("Привет, я офлайн ассистент!", "ru", "baya")
        self.speak("Hello, I can speak English!", "en", "en_1")
        self.speak("Salom, men O'zbek tilida gapira olaman!", "uz", "uz_2")
