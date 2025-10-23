import platform
import psutil


def get_system_info():
    info = {
        "OS": platform.system(),
        "Release": platform.release(),
        "CPU": platform.processor(),
        "RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
    }
    return info

def get_battery_status():
    battery = psutil.sensors_battery()
    if not battery:
        return "Батарея не найдена."
    percent = battery.percent
    plugged = "в сети" if battery.power_plugged else "от батареи"
    return f"Заряд: {percent}%. Питание: {plugged}."

