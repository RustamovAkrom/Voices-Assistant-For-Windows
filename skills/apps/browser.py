import os


def open_browser():
    path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"  # Replace to your directory
    os.startfile(path)


def close_browser():
    os.system("taskkill /f /im Browser.exe")
