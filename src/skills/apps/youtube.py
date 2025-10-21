import os


def open_youtube():
    path = r"c:\Users\user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Приложения Chrome\YouTube.lnk"
    os.startfile(path)


def close_youtube():
    os.system("taskkill /f /im YouTube.exe")
