import sys
from core.speakers.audio_play import PlayAudio
from core import settings

play_audio = PlayAudio(settings.AUDIO_FILES)


def exit_handle():
    """
    Завершает программу с кодом 1.
    """
    play_audio.play("off")
    sys.exit()
    settings.ASISTENT_IS_ACTIVE = False

