import os


def open_telegram():
    path = "C:/Users/user/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Telegram Desktop/Telegram.lnk"
    # subprocess.Popen([path], shell=True)
    os.startfile(path)


def close_telegram():
    os.system("taskkill /f /im Telegram.exe")
