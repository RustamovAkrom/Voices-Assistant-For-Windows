import subprocess


def open_program(path_to_exe: str) -> None:
    try:
        subprocess.Popen(path_to_exe)
    except Exception:
        pass
