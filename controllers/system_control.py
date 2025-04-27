import os
import platform
import subprocess
import psutil
import shutil
import socket


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


def get_network_info():
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    info = {}
    for iface, addr_list in addrs.items():
        info[iface] = {
            "IP": addr_list[1].address if len(addr_list) > 1 else None,
            "MAC": addr_list[0].address if len(addr_list) > 0 else None,
            "Is Up": stats[iface].isup
        }
    return info


def clean_temp_files():
    temp_paths = [
        os.getenv('TEMP'),
        os.getenv('TMP'),
        r"C:\Windows\Temp"
    ]
    for path in temp_paths:
        try:
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
        except Exception as e:
            print(f"Не удалось удалить {file_path}. Ошибка: {e}")
