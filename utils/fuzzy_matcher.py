from fuzzywuzzy import fuzz


def find_best_match(text, phrases, threshold=70):
    best_match = None
    best_score = 0

    for phrase in phrases:
        score = fuzz.partial_ratio(text, phrase)
        if score > best_score and score >= threshold:
            best_match = phrase
            best_score = score
    
    return best_match
