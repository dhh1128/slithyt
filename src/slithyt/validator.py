# Contains logic for validating generated words against various constraints.
import re
import gzip  # Import the gzip module
from typing import Set
from . import sentiment
from . import pronounce

def load_word_set(file_path: str) -> Set[str]:
    """
    Loads a list of words from a plain text or gzipped file into a set
    for efficient lookup. Assumes gzipped if filename doesn't end in .txt.
    """
    if not file_path:
        return set()
    try:
        # Read the first two bytes to check for the gzip magic number
        with open(file_path, 'rb') as f:
            is_gzipped = (f.read(2) == b'\x1f\x8b')

        # Re-open the file in the correct mode (text or gzip)
        if is_gzipped:
            with gzip.open(file_path, 'rt', encoding="utf-8") as f_gz:
                return {line.strip().lower() for line in f_gz if line.strip()}
        else:
            with open(file_path, 'r', encoding="utf-8") as f_txt:
                return {line.strip().lower() for line in f_txt if line.strip()}

    except FileNotFoundError:
        print(f"WARNING: File not found at {file_path}. Skipping this check.")
        return set()
    except gzip.BadGzipFile:
        print(f"WARNING: File {file_path} is not a valid gzip file. Skipping this check.")
        return set()
    

def validate_word(
    word: str,
    matches_regex: str = None,
    reject_regex: str = None,
    dictionary_set: Set[str] = None,
    blocklist_set: Set[str] = None,
    min_sentiment: float = None,
    max_sentiment: float = None,
    min_pronounceability: float = None
) -> bool:
    """
    Validates a word against a set of constraints.

    Args:
        word: The word to validate.
        matches_regex: A regex pattern the word must match.
        reject_regex: A regex pattern the word must not match.
        dictionary_path: Path to a file of common words to reject.
        blocklist_path: Path to a file of profane/blocked words to reject.
        min_sentiment: The minimum allowed sentiment score (0.0 to 1.0).
        max_sentiment: The maximum allowed sentiment score (0.0 to 1.0).
        min_pronounceability: The minimum allowed pronounceability score (0.0 to 1.0).

    Returns:
        True if the word is valid, False otherwise.
    """
    if not word:
        return False

    word_lower = word.lower()

    # Regex checks are case-insensitive for broader matching
    if matches_regex and not re.search(matches_regex, word, re.IGNORECASE):
        return False
    if reject_regex and re.search(reject_regex, word, re.IGNORECASE):
        return False
        
    if dictionary_set and word_lower in dictionary_set:
        return False

    # Blocklist check (for profanity)
    if blocklist_set and word_lower in blocklist_set:
        return False

    # Sentiment check
    if min_sentiment is not None or max_sentiment is not None:
        score = sentiment.analyze_word_sentiment(word)
        if min_sentiment is not None and score < min_sentiment:
            return False
        if max_sentiment is not None and score > max_sentiment:
            return False
        
    # Pronounceability check
    if min_pronounceability is not None:
        score = pronounce.score_pronounceability(word)
        if score < min_pronounceability:
            return False

    return True
