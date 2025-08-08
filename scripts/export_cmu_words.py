# scripts/export_cmu_words.py

import pronouncing

def export_cmu_words(output_file: str):
    """
    Exports all unique words from the CMU Pronouncing Dictionary to a file.
    """
    print("Exporting words from the CMU Pronouncing Dictionary...")
    
    # Use a set to automatically handle duplicate entries
    all_words = set()

    # pronouncing.cmudict.entries() returns a list of (word, pronunciation) tuples
    for word, pron in pronouncing.cmudict.entries():
        # Clean the word: convert to lowercase and remove numbers for alternate
        # pronunciations (e.g., "WORD(1)" -> "word")
        clean_word = word.lower().split('(')[0]
        all_words.add(clean_word)

    print(f"Found {len(all_words)} unique words.")
    
    # Sort the words alphabetically for a clean output file
    sorted_words = sorted(list(all_words))
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for word in sorted_words:
            f_out.write(f"{word}\n")
            
    print(f"Word list saved to '{output_file}'.")


if __name__ == "__main__":
    output_path = "cmu-dict-words.txt"
    export_cmu_words(output_path)