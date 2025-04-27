import socket
import subprocess


def open_program(path_to_exe: str) -> None:
    try:
        subprocess.Popen(path_to_exe)
    except Exception:
        pass


def check_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False
