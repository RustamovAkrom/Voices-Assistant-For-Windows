import os
import platform
import subprocess


def shutdown():
    """
    Shutdown the system.
    """
    system = platform.system()
    if system == "Windows":
        os.system("shutdown /s /t 1")
    elif system == "Linux":
        os.system("poweroff")
    elif system == "Darwin":  # macOS
        os.system("os shutdown -h now")
        
    return "System is shutting down..."


def restart():
    """
    Restart the system.
    """
    system = platform.system()
    if system == "Windows":
        os.system("shutdown /r /t 1")
    elif system == "Linux":
        os.system("reboot")
    elif system == "Darwin":
        os.system("sudo reboot")

    return "System is restarting..."
