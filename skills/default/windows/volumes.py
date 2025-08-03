from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


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
