# scripts/purify_corpus.py

import pronouncing
import sys

def purify_dictionary(input_file: str, output_file: str):
    """
    Reads a large word list and writes a new, purified version containing only
    words that have a known pronunciation in the CMU Pronouncing Dictionary.
    """
    print(f"Reading from '{input_file}'...")
    
    # Using a set to handle potential duplicates in the input file
    purified_words = set()
    
    with open(input_file, 'r', encoding='utf-8') as f_in:
        for i, line in enumerate(f_in):
            word = line.strip().lower()
            
            # Skip empty lines or words with non-alphabetic characters
            if not word or not word.isalpha():
                continue

            # The core of the filter: check if the word is in the CMU dictionary
            if pronouncing.phones_for_word(word):
                purified_words.add(word)

            if (i + 1) % 10000 == 0:
                print(f"  ...processed {i+1} lines, found {len(purified_words)} valid words.")

    print(f"\nFound a total of {len(purified_words)} pronounceable words.")
    
    # Sort the words alphabetically for a clean output file
    sorted_words = sorted(list(purified_words))
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for word in sorted_words:
            f_out.write(f"{word}\n")
            
    print(f"Purified dictionary saved to '{output_file}'.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python purify_corpus.py <path_to_input_dict> <path_to_output_dict>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    purify_dictionary(input_path, output_path)