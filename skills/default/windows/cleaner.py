import shutil
import ctypes
from pathlib import Path
import tempfile

from utils.decorators import timeit, log_command


@log_command("default.windows.cleaner.clear_temp_folder")
@timeit
def clear_temp_folder():
    """Clear temp files folder"""

    temp_path = Path(tempfile.gettempdir())
    print(f"[TEMP] Очистка временной папки: {temp_path}")
    for item in temp_path.iterdir():
        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            print(f"Не удалось удалить: {item} — {e}")


@log_command("default.windows.cleaner.clear_recycle_bin")
@timeit
def clear_recycle_bin():
    """Clear recycle bin"""

    print("[Recycle Bin] Очистка корзины...")
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
    except Exception as e:
        print(f"Не удалось очистить корзину: {e}")


@log_command("default.windows.cleaner.clear_windows_except_important")
@timeit
def clear_downloads_except_important(keep_extensions=None):
    """Clear downloads folder"""

    if keep_extensions is None:
        keep_extensions = [
            ".img",
            ".jpeg",
            ".jpg",
            ".mp3",
            ".mp4",
        ]  # Примеры расширений для сохранения
    downloads_path = Path.home() / "Downloads"
    print(f"[Downloads] Очистка папки загрузок: {downloads_path}")

    for item in downloads_path.iterdir():
        try:
            if item.is_file() and item.suffix not in keep_extensions:
                item.unlink()
                print(f"Удален файл: {item}")
            elif item.is_dir():
                shutil.rmtree(item)
                print(f"Удалена папка: {item}")
        except Exception as e:
            print(f"Не удалось удалить: {item} — {e}")


def clean_all_files():
    clear_recycle_bin()
    clear_downloads_except_important()
    clear_temp_folder()