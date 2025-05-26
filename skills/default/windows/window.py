import pyautogui


def close_window():
    """
    Close the currently active window.
    """
    pyautogui.hotkey('alt', 'f4')
    return "Закрыл окно"
