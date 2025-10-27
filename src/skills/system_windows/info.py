import platform
import psutil


# === 🧠 СИСТЕМНАЯ ИНФОРМАЦИЯ ===
def get_system_info(*args, **kwargs):
    lang = kwargs.get("lang", "ru").lower()

    info = {
        "OS": platform.system(),
        "Release": platform.release(),
        "CPU": platform.processor() or "Неизвестный процессор",
        "RAM": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
    }

    if lang == "ru":
        return (
            f"Система: {info['OS']} {info['Release']}. "
            f"Процессор: {info['CPU']}. "
            f"Оперативная память: {info['RAM']}."
        )
    elif lang == "en":
        return (
            f"System: {info['OS']} {info['Release']}. "
            f"Processor: {info['CPU']}. "
            f"Memory: {info['RAM']}."
        )
    elif lang == "uz":
        return (
            f"Tizim: {info['OS']} {info['Release']}. "
            f"Protsessor: {info['CPU']}. "
            f"Operativ xotira: {info['RAM']}."
        )
    else:
        return str(info)


# === 🔋 СОСТОЯНИЕ БАТАРЕИ ===
def get_battery_status(*args, **kwargs):
    lang = kwargs.get("lang", "ru").lower()
    battery = psutil.sensors_battery()

    if not battery:
        if lang == "ru":
            return "Батарея не найдена."
        elif lang == "en":
            return "Battery not found."
        elif lang == "uz":
            return "Batareya topilmadi."
        else:
            return "Battery not found."

    percent = battery.percent
    plugged = battery.power_plugged

    if lang == "ru":
        return (
            f"Заряд батареи: {percent}%. "
            f"Питание: {'подключено к сети' if plugged else 'от батареи'}."
        )
    elif lang == "en":
        return (
            f"Battery level: {percent}%. "
            f"Power: {'plugged in' if plugged else 'on battery'}."
        )
    elif lang == "uz":
        return (
            f"Batareya zaryadi: {percent}%. "
            f"Quvvat: {'tarmoqdan' if plugged else 'batareyadan'}."
        )
    else:
        return f"{percent}% {'plugged' if plugged else 'battery'}"
