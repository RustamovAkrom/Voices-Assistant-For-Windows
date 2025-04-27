from typing import List, Tuple
from core.config import config
from utils.text_cleaner import clean_text
from utils.fuzzy_matcher import find_best_match


commands = config.get_commands().get('commands', [])


def extract_commands(text: str) -> List[Tuple[str, str]]:
    """
    Extracts commands from the given text.
    """
    
    results = []
    original_text = clean_text(text)
    text_to_search = original_text.lower()

    while text_to_search:
        best_match = None
        best_cmd = None
        best_start_idx = -1

        for cmd in commands:
            matched_phrase = find_best_match(text_to_search, [p.lower() for p in cmd["phrases"]])
            if matched_phrase:
                start_idx = text_to_search.find(matched_phrase)
                if start_idx != -1 and (best_start_idx == -1 or start_idx < best_start_idx):
                    best_match = matched_phrase
                    best_cmd = cmd
                    best_start_idx = start_idx

        if best_cmd and best_match:
            start_idx = text_to_search.find(best_match)
            end_idx = start_idx + len(best_match)

            args = text_to_search[end_idx:].strip(" .,!?;:")
            results.append((best_cmd["function"], args))

            text_to_search = (text_to_search[:start_idx] + text_to_search[end_idx:]).strip()
        else:
            break

    return results
