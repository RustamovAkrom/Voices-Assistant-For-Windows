import time
from functools import wraps
from utils.logger import logger
from utils.base import check_internet


def timeit():
    def decorator(func):
        """Измеряет время выполнения функции."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"Function {func.__name__} executed in {duration:.4f}s")
            return result

        return wrapper

    return decorator


def catch_errors(log=True, default=None):
    """Обрабатывает ошибки в функции и не падает."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log:
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                return default

        return wrapper

    return decorator


def retry_on_exception(retries=3, delay=1, exceptions=(Exception,)):
    """Повторяет выполнение при ошибках."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(
                        f"Retry {attempt+1}/{retries} for {func.__name__} due to: {e}"
                    )
                    time.sleep(delay)
            return None

        return wrapper

    return decorator


# utils/decorators.py


def log_command(handler_path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"[COMMAND] Handler called: {handler_path}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_internet():
    def decorator(func):
        def wrapper(*args, **kwargs):
            if check_internet():
                return func(*args, **kwargs)
            else:
                logger.warning(
                    f"[COMMAND]({func.__name__}) can`t work because internet is desconnected!"
                )
            return None

        return wrapper

    return decorator
