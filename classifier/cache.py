intent_cache = {}


def get_chaed_intent(text):
    return intent_cache.get(text)


def set_cached_intent(text, intent):
    intent_cache[text] = intent
