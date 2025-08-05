# Tests for the validator module.
import tempfile
import os
from slithyt import validator

def test_basic_validator():
    """
    Tests the validation logic with temporary dictionary and blocklist files.
    """
    dict_content = "common\nordinary\n"
    block_content = "blocked\nforbidden\n"

    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as dict_tmp, \
         tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as block_tmp:
        dict_tmp.write(dict_content)
        block_tmp.write(block_content)
        dict_path = dict_tmp.name
        block_path = block_tmp.name

    try:
        # Test a valid word
        assert validator.validate_word("zentoria", dictionary_path=dict_path, blocklist_path=block_path) == True

        # Test a word that is a common word
        assert validator.validate_word("common", dictionary_path=dict_path, blocklist_path=block_path) == False

        # Test a word that is on the blocklist
        assert validator.validate_word("forbidden", dictionary_path=dict_path, blocklist_path=block_path) == False

        # Test regex constraints
        assert validator.validate_word("startgood", matches_regex="^start") == True
        assert validator.validate_word("startbad", matches_regex="^wrong") == False
        assert validator.validate_word("endgood", reject_regex="bad$") == True
        assert validator.validate_word("endbad", reject_regex="bad$") == False

    finally:
        # Clean up the temporary files
        os.remove(dict_path)
        os.remove(block_path)

def test_sentiment_validator():
    """Tests the sentiment validation logic."""
    # These words are constructed to have clear sentiment leanings
    # based on morphemes in the VADER lexicon (e.g., 'win', 'love', 'doom', 'bad').
    positive_word = "winlove"
    negative_word = "doomfoul"
    neutral_word = "zxyabc" # No morphemes in VADER lexicon
    
    # Test min_sentiment: positive word should pass, negative word should fail.
    assert validator.validate_word(positive_word, min_sentiment=0.75) == True
    assert validator.validate_word(negative_word, min_sentiment=0.75) == False

    # Test max_sentiment: negative word should pass, positive word should fail.
    assert validator.validate_word(negative_word, max_sentiment=0.35) == True
    assert validator.validate_word(positive_word, max_sentiment=0.35) == False

    # Test a neutral word in a neutral range
    assert validator.validate_word(neutral_word, min_sentiment=0.4, max_sentiment=0.6) == True

    # Test a positive word failing a neutral range
    assert validator.validate_word(positive_word, min_sentiment=0.4, max_sentiment=0.6) == False
