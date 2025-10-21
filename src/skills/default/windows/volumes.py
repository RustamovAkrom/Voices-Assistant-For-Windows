from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from utils.decorators import log_command, catch_errors, timeit


def controle_volume(volume: float) -> None:
    """
    Control the system volume.

    :param volume: Volume level to set (0.0 to 1.0).
    """
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
    volume_control = interface.QueryInterface(IAudioEndpointVolume)

    # Set the volume level
    volume_control.SetMasterVolumeLevelScalar(volume, None)
    print(f"Volume set to {volume * 100:.2f}%")


@log_command("default.windows.volumes.set_volume_max")
@catch_errors()
@timeit()
def set_volume_max() -> None:
    controle_volume(1.0)


@log_command("default.windows.volumes.set_volume_mid")
@catch_errors()
@timeit()
def set_volume_mid() -> None:
    controle_volume(0.5)


@log_command("default.windows.volumes.set_volume_min")
@catch_errors()
@timeit()
def set_volume_min() -> None:
    controle_volume(0)


__all__ = (
    "set_volume_max",
    "set_volume_mid",
    "set_volume_min",
)
