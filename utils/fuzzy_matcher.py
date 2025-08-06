# from fuzzywuzzy import fuzz


# def find_best_match(text, phrases, threshold=70):
#     best_match = None
#     best_score = 0

#     for phrase in phrases:
#         score = fuzz.partial_ratio(text, phrase)
#         if score > best_score and score >= threshold:
#             best_match = phrase
#             best_score = score

#     return best_match, best_score
from rapidfuzz import process, fuzz


def find_best_match(text, phrases, threshold=70):
    result = process.extractOne(
        text, phrases, scorer=fuzz.partial_ratio, score_cutoff=threshold
    )
    if result:
        return result[0], result[1]
    return None, 0
