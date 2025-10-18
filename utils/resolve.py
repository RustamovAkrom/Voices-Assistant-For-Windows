def resolve_attr(obj, dotted_path: str):
    try:
        for part in dotted_path.split("."):
            obj = getattr(obj, part)
        return obj
    except AttributeError as e:
        print(f"[ERROR] Не найден атрибут: {part}")
        return None
