import sys
import os
import pickle
import pathlib

# Add the src directory to the Python path to allow importing slithyt
# This path is constructed relative to the script's location
script_dir = pathlib.Path(__file__).parent.resolve()
project_root = script_dir.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from slithyt import utils
import pronouncing

def build_phonetic_model(corpus_path: str, n: int = 3) -> dict:
    """
    Builds a phonetic n-gram model from a word corpus.
    """
    print(f"Building phonetic model from {corpus_path}...")
    model = {}
    prefix_len = n - 1

    with utils.open_any(corpus_path) as f:
        for word in f:
            word = word.strip().lower()
            if not word:
                continue
            
            phones_list = pronouncing.phones_for_word(word)
            if not phones_list:
                continue
            
            phonemes = phones_list[0].split()
            padded_phonemes = (["^"] * prefix_len) + phonemes + ["$"]
            
            for i in range(len(padded_phonemes) - prefix_len):
                prefix = tuple(padded_phonemes[i : i + prefix_len])
                next_phoneme = padded_phonemes[i + prefix_len]
                
                if prefix not in model:
                    model[prefix] = []
                model[prefix].append(next_phoneme)
    
    print("Model build complete.")
    return model

if __name__ == "__main__":
    # The default dictionary is a good source for a phonetic model.
    # Its path is now constructed relative to the project root.
    corpus_file = project_root / 'src' / 'slithyt' / 'data' / 'en-dict.txt.gz'
    
    # Define the canonical cache directory in the user's home folder
    cache_dir = pathlib.Path.home() / '.slithyt' / 'data'
    cache_dir.mkdir(parents=True, exist_ok=True) # Create directory if it doesn't exist
    output_file = cache_dir / 'phonetic-model.dat'
    
    phonetic_model = build_phonetic_model(str(corpus_file), n=3)
    
    with open(output_file, "wb") as f:
        pickle.dump(phonetic_model, f)
        
    print(f"Phonetic model saved to {output_file}")