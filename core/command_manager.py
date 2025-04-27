import importlib


def execute_command(function_path, args=None):
    """
    Download and execute a function from a given module path.
    """
    try:
        class_name = function_path.split(".")[-1]
        module_path = ".".join(function_path.split(".")[:-1])

        module = __import__(module_path, fromlist=[class_name])
        ClassHandler = getattr(module, class_name)
        handler = ClassHandler()
        return handler.handle(args)

    except (ImportError, AttributeError) as e:
        print(f"Error: {e}")
        return None
