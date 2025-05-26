import pyautogui


def minimize_window():
    pyautogui.hotkey('win', 'down')
    return "Свернул окна"