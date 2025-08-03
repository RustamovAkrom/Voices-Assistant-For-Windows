import os


def open_notepad():
    path = "C:/Program Files/WindowsApps/Microsoft.WindowsNotepad_11.2504.62.0_x64__8wekyb3d8bbwe/Notepad/Notepad.exe" # Replace to your directory
    os.startfile(path)


def close_notepad():
    os.system("taskkill /f /im Notepad.exe")
