from core.recognizers.offline import OfflineRecognizer
from core.recognizers.online import OnlineRecognizer
from core.recognizers.porcupine_listener import PorcupineListener
from core.speakers.silero_tts import SpeakerSileroTTS
from core.speakers.pyttsx3_tts import SpeakerPyTTSx3
from core.speakers.audio_play import PlayAudio
from core import settings
from utils.fuzzy_matcher import find_best_match
from utils.resolve import resolve_attr
from utils.logger import logger
import skills
import random
import string
import time
import re


class VoicesAsistentProcess:

    def __init__(
        self,
        dataset: list[dict],
        speaker_silero: SpeakerSileroTTS,
        speaker_pyttsx3: SpeakerPyTTSx3,
        play_audio: PlayAudio,
    ) -> None:
        self.dataset = dataset

        # External components
        self.speaker_silero = speaker_silero
        self.speaker_pyttsx3 = speaker_pyttsx3
        self.play_audio = play_audio

    def clean_query_text(self, text: str):
        stop_words = {
            "о",
            "об",
            "в",
            "на",
            "про",
            "по",
            "из",
            "с",
            "от",
            "для",
            "и",
            "мне",
        }
        words = text.strip().split()
        if words and words[0] in stop_words:
            words.pop(0)
        return " ".join(words)

    def find_command_from_dataset(self, user_text, threshold: int = 95):
        # original_text = user_text
        user_text = user_text.lower().strip()
        user_text = user_text.translate(str.maketrans("", "", string.punctuation))

        for item in self.dataset:
            best_match, best_score = find_best_match(user_text, item["phrases"])
            if best_score >= threshold:
                pattern = re.escape(best_match.lower())
                cleaned_text = re.sub(pattern, "", user_text, count=1).strip()
                cleaned_text = self.clean_query_text(cleaned_text)
                return (
                    item.get("handler", None),
                    cleaned_text.strip(".|"),
                    item.get("text", None),
                    item.get("param", False),
                )

        return (None, None, None, False)

    def process_command(self, user_text) -> None:
        logger.debug(f"process_command: cmd_text='{user_text}'")
        handler, phrase, text, param_required = self.find_command_from_dataset(
            user_text
        )

        # If handler not found run that code
        if not handler:
            if text:
                logger.info(f"Команда не распознана: {phrase}")
                self.speaker_silero.say(text)
            else:
                logger.warning(f"Команда не распознана: {user_text}")
                print(f"[{user_text}] → Команда не распознана и не реализована")
                self.play_audio.play("not_found")
            return

        # If text already exist it will speak by SileroTTS
        if text:
            logger.info(f"Команда распознана: {phrase} → {handler}")
            self.speaker_silero.say(text)
        else:
            self.play_audio.play(random.choice(["ok1", "ok2", "ok3"]))

        try:
            func = resolve_attr(skills, handler)
            logger.debug(f"Resolved handler: {handler} → {func}")

            if param_required:
                # Если требуется параметр, передаем его в функцию
                logger.debug(
                    f"Выполнение команды с параметрами: {user_text}, phrase={phrase}, text={text}, param_required={param_required}"
                )
                result = func(
                    user_text,
                    handler=handler,
                    phrase=phrase,
                    text=text,
                    param_required=param_required,
                )
            else:
                logger.debug(
                    f"Выполнение команды без параметров: {user_text}, handler={handler}, phrase={phrase}, text={text}, param_required={param_required}"
                )
                result = func()

            if result:
                self.speaker_silero.say(result)
                logger.info(f"[{user_text}] → Выполнена команда: {result}")
                print(f"[{user_text}] → Выполнена команда: {result}")

            else:
                print(f"[{user_text}] → Команда выполнена, но нет ответа")

        except Exception as e:
            logger.error(f"[{user_text}] → Ошибка при выполнении команды: {e}")
            print(f"[{user_text}] → Ошибка при выполнении команды: {e}")
            self.play_audio.play("not_found")


class VoicesAsistentRunner:
    
    def __init__(
        self,
        dataset: list[dict],
        speaker_silero: SpeakerSileroTTS,
        speaker_pyttsx3: SpeakerPyTTSx3,
        play_audio: PlayAudio,
        porcupine_listener: PorcupineListener,
        offline_recognizer: OfflineRecognizer,
        online_recognizer: OnlineRecognizer,
    ) -> None:
        self.ACTIVATION_TIMEOUT = 15  # 15 секунд
        self.active_until = 0

        self.dataset = dataset

        self.speaker_silero = speaker_silero
        self.speaker_pyttsx3 = speaker_pyttsx3
        self.play_audio = play_audio

        self.porcupine_listener = porcupine_listener
        self.recognizer = (
            online_recognizer if settings.USE_ONLINE_RECOGNIZER else offline_recognizer
        )

    def play_activation_sound(self):
        self.play_audio.play(random.choice(["great1", "great2", "great3"]))

    def play_startup_sound(self):
        self.play_audio.play(random.choice(["run1", "run2"]))

    def splitter_commands(self, cmd_text: str) -> list[str]:
        splitters = settings.SPLITTERS
        commands = [cmd_text]
        for splitter in splitters:
            new_commands = []
            for c in commands:
                new_commands.extend([x.strip() for x in c.split(splitter) if x.strip()])
            commands = new_commands
        return commands

    def handle_command(self, cmd_text: str) -> None:
        # Create Process Commands
        voices_asistent = VoicesAsistentProcess(
            dataset=self.dataset,
            speaker_silero=self.speaker_silero,
            speaker_pyttsx3=self.speaker_pyttsx3,
            play_audio=self.play_audio,
        )
        # Split commands if they are many
        commands = self.splitter_commands(cmd_text=cmd_text)

        for single_cmd in commands:
            # Search triger
            trg = settings.TRIGGERS.intersection(single_cmd.split())
            # If triger exist play activation sound
            if trg:
                self.play_activation_sound()
                print("Активация продлена! Jarvis слушает еще 15 секунд...")
                logger.info(f"Команда активирована триггером: {trg}")
                self.active_until = time.time() + self.ACTIVATION_TIMEOUT
                cmd = single_cmd
                for t in trg:
                    cmd = cmd.replace(t, "").strip()
                if cmd:
                    logger.debug(f"Команда после триггера: {cmd}")
                    voices_asistent.process_command(cmd)
                continue
            else:
                logger.debug(f"Обработка команды: {single_cmd}")
                voices_asistent.process_command(single_cmd)

    def run(self):
        logger.info("Jarvis is starting...")
        self.play_startup_sound()

        while True:
            if time.time() > self.active_until:
                print(
                    f"Ожидание активационного слова ({settings.PORCUPINE_KEYWORDS})..."
                )

                if self.porcupine_listener.listen():
                    self.play_activation_sound()
                    print("Активация! Jarvis слушает команды 15 секунд...")
                    logger.info("Активация Jarvis через PorcupineListener")
                    self.active_until = time.time() + self.ACTIVATION_TIMEOUT
                continue

            print("Jarvis активен. Ожидание команды...")
            cmd_text = self.recognizer.listen().lower()

            if not cmd_text:
                print("Команда не распознана, повторите.")
                logger.warning("Команда не распознана, повторите.")
                continue

            print(f"Recognized command: {cmd_text}")
            logger.debug(f"Recognized command: {cmd_text}")
            self.handle_command(cmd_text=cmd_text)

            self.active_until = time.time() + self.ACTIVATION_TIMEOUT

    def close(self):
        self.porcupine_listener.close()
