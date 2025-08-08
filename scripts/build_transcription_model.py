import sys
import os
import pickle
import pathlib
from collections import defaultdict

# Add the src directory to the Python path to allow importing slithyt
script_dir = pathlib.Path(__file__).parent.resolve()
project_root = script_dir.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from slithyt import utils
import pronouncing

def build_transcription_model(corpus_path: str) -> dict:
    """
    Builds a statistical model for transcribing phonemes to graphemes (spellings).
    This version iterates through a given corpus, looks up the phonetics for each
    word, and learns the most common spellings for each phoneme.
    """
    print(f"Building transcription model from corpus: {corpus_path}...")
    model = defaultdict(lambda: defaultdict(int))

    with utils.open_any(corpus_path) as f:
        for word in f:
            word = word.strip().lower()
            if not word:
                continue

            phones_list = pronouncing.phones_for_word(word)
            if not phones_list:
                continue
            
            phonemes = phones_list[0].split()
            
            # This is a simple heuristic for aligning phonemes to letters.
            # It's not perfect but provides a good statistical basis.
            # We assume a rough correspondence between the sequence of
            # phonemes and the sequence of letters.
            if len(phonemes) == len(word):
                for i, p in enumerate(phonemes):
                    base_phoneme = p.rstrip('012')
                    letter = word[i]
                    model[base_phoneme][letter] += 1

    # Create the final model: a dictionary mapping phonemes to a list of likely spellings
    final_model = {}
    for phoneme, spellings in model.items():
        sorted_spellings = sorted(spellings.items(), key=lambda item: item[1], reverse=True)
        final_model[phoneme] = [s[0] for s in sorted_spellings[:3]] # Keep top 3

    print("Transcription model build complete.")
    return final_model


if __name__ == "__main__":
    corpus_file = project_root / 'src' / 'slithyt' / 'data' / 'cmu.txt.gz'
    
    cache_dir = pathlib.Path.home() / '.slithyt' / 'data'
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_file = cache_dir / 'transcription-model.dat'
    
    transcription_model = build_transcription_model(str(corpus_file))
    
    with open(output_file, "wb") as f:
        pickle.dump(transcription_model, f)
        
    print(f"Transcription model saved to {output_file}")