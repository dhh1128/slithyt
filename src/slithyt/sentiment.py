# New module for handling sentiment analysis of novel words.
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the analyzer and its lexicon once when the module is loaded for efficiency.
_analyzer = SentimentIntensityAnalyzer()
_lexicon = _analyzer.lexicon

def _normalize_score(score: float) -> float:
    """
    Normalizes a VADER sentiment score from its typical [-4, 4] range to [0, 1].
    A score of 0 is maximally negative, 1 is maximally positive, and 0.5 is neutral.
    """
    # VADER scores are roughly in the range of -4 to 4.
    # We add 4 to shift the range to [0, 8] and then divide by 8.
    return (score + 4) / 8

def analyze_word_sentiment(word: str) -> float:
    """
    Analyzes the sentiment of a novel word by performing a greedy,
    non-overlapping search for morphemes in the VADER sentiment lexicon.

    Args:
        word: The word to analyze.

    Returns:
        A sentiment score between 0.0 (very negative) and 1.0 (very positive).
        Returns 0.5 (neutral) if no sentiment-bearing morphemes are found.
    """
    word_lower = word.lower()
    found_scores = []
    i = 0
    while i < len(word_lower):
        # Find the longest possible morpheme starting at position i
        best_match = ""
        for j in range(len(word_lower), i + 1, -1):
            substring = word_lower[i:j]
            if substring in _lexicon:
                best_match = substring
                break
        
        if best_match:
            found_scores.append(_lexicon[best_match])
            i += len(best_match) # Move past the found morpheme
        else:
            i += 1 # No morpheme found, advance by one character

    if not found_scores:
        return 0.5 # Return neutral sentiment if no parts are found

    # Calculate the average score of the found morphemes
    avg_score = sum(found_scores) / len(found_scores)
    
    return _normalize_score(avg_score)