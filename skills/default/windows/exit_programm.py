import sys
from core.speakers.audio_play import PlayAudio
from core import settings
from utils.decorators import log_command, catch_errors, timeit


play_audio = PlayAudio(settings.AUDIO_FILES)

@log_command("default.windows.exit_program.exit_handle")
@catch_errors()
@timeit()
def exit_handle():
    """
    Завершает программу с кодом 1.
    """
    play_audio.play("off")
    sys.exit()
    settings.ASISTENT_IS_ACTIVE = False


__all__ = ("exit_handle", )