from core.asistent import VoicesAsistentRunner
from core.speakers.silero_tts import SpeakerSileroTTS
from core.speakers.pyttsx3_tts import SpeakerPyTTSx3
from core.speakers.audio_play import PlayAudio
from core.recognizers.offline import OfflineRecognizer
from core.recognizers.online import OnlineRecognizer
from core.recognizers.porcupine_listener import PorcupineListener

from core.words_data import data_set
from core import settings

from utils.logger import logger

import sys


def main() -> None:
    voices_asistent_runner = VoicesAsistentRunner(
        dataset=data_set,
        speaker_silero=SpeakerSileroTTS(settings.SILERO_TTS_SPEAKER),
        speaker_pyttsx3=SpeakerPyTTSx3(),
        play_audio=PlayAudio(settings.AUDIO_FILES),
        porcupine_listener=PorcupineListener(
            settings.PORCUPINE_KEYWORDS, settings.PORCUPINE_ACCESS_KEY
        ),
        offline_recognizer=OfflineRecognizer(settings.VOSK_MODEL_PATH),
        online_recognizer=OnlineRecognizer(),
    )

    try:
        voices_asistent_runner.run()
    except KeyboardInterrupt:
        voices_asistent_runner.close()
        print("\nExiting Jarvis...")
        logger.info("Exiting Jarvis...")
        sys.exit(0)


if __name__ == "__main__":
    main()
