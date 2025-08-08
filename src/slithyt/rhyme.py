import pronouncing
import pickle
import random

def get_phonetic_breakdown(word: str) -> list[str] | None:
    """
    Gets the phonetic breakdown for a word using the pronouncing library.
    """
    pronunciations = pronouncing.phones_for_word(word)
    if not pronunciations:
        return None
    return pronunciations[0].split()

def get_rhyme_signature(phonemes: list[str]) -> list[str] | None:
    """
    Extracts the rhyming part of a word from its list of phonemes.
    """
    last_stressed_vowel_index = -1
    for i, p in enumerate(phonemes):
        if p[-1] in ('1', '2'):
            last_stressed_vowel_index = i
            
    if last_stressed_vowel_index == -1:
        return None
        
    return phonemes[last_stressed_vowel_index:]

def load_phonetic_model(model_path: str) -> dict:
    """
    Loads a pre-computed phonetic model from a file.
    """
    try:
        with open(model_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"ERROR: Phonetic model not found at {model_path}.")
        print("Please run 'python scripts/build_phonetic_model.py' first.")
        return None

def generate_phonetic_word(model: dict, rhyme_signature: list[str], n: int = 3) -> list[str] | None:
    """
    Generates a new sequence of phonemes that ends with the given rhyme signature.
    """
    if not model:
        return None

    prefix_len = n - 1
    current_prefix = tuple(["^"] * prefix_len)
    generated_phonemes = []

    for _ in range(10):
        if current_prefix not in model:
            return None
        
        next_phoneme = random.choice(model[current_prefix])
        
        if next_phoneme == "$":
            break
            
        generated_phonemes.append(next_phoneme)
        current_prefix = tuple(list(current_prefix[1:]) + [next_phoneme])

    return generated_phonemes + rhyme_signature

def load_transcription_model(model_path: str) -> dict:
    """
    Loads a pre-computed transcription model from a file.
    """
    try:
        with open(model_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"ERROR: Transcription model not found at {model_path}.")
        print("Please run 'python scripts/build_transcription_model.py' first.")
        return None

def transcribe_word(transcription_model: dict, phonemes: list[str]) -> str:
    """
    Transcribes a sequence of phonemes into a plausible word spelling.
    """
    word = []
    for p in phonemes:
        # Remove stress markers for lookup (e.g., 'EH1' -> 'EH')
        base_phoneme = p.rstrip('012')
        if base_phoneme in transcription_model and transcription_model[base_phoneme]:
            # Choose one of the common spellings for that phoneme
            word.append(random.choice(transcription_model[base_phoneme]))
        else:
            # Fallback for phonemes not in the model (less common)
            # This prevents crashes but may result in less accurate spelling.
            word.append('?')

    return "".join(word)
