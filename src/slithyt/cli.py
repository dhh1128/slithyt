# This file contains the command-line interface logic.
import argparse
import importlib.resources
from . import generator
from . import validator
from . import sentiment

def main():
    """
    Main function for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="SlithyT: A plausible word generation tool.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Generate command ---
    gen_parser = subparsers.add_parser("generate", help="Generate new words.")
    gen_parser.add_argument("--corpus", required=True, help="Path to the corpus file for training.")
    gen_parser.add_argument("--count", type=int, default=10, help="Number of words to generate.")
    gen_parser.add_argument("--min-len", type=int, default=5, help="Minimum word length.")
    gen_parser.add_argument("--max-len", type=int, default=10, help="Maximum word length.")
    gen_parser.add_argument("--matches-regex", help="A regex pattern the word must match.")
    gen_parser.add_argument("--reject-regex", help="A regex pattern the word must not match.")
    gen_parser.add_argument("--dictionary", help="Path to a dictionary file to check for novelty.")
    gen_parser.add_argument("--blocklist", help="Path to a blocklist file for profanity checking.")
    gen_parser.add_argument("--ngram-size", type=int, default=3, help="The n-gram size for the model (e.g., 3 for trigrams).")
    gen_parser.add_argument("--min-sentiment", type=float, help="Minimum sentiment score (0.0-1.0). Words below this are rejected.")
    gen_parser.add_argument("--max-sentiment", type=float, help="Maximum sentiment score (0.0-1.0). Words above this are rejected.")

    # --- Validate command ---
    val_parser = subparsers.add_parser("validate", help="Validate a potential word.")
    val_parser.add_argument("word", help="The word to validate.")
    val_parser.add_argument("--dictionary", help="Path to a dictionary file to check for novelty.")
    val_parser.add_argument("--blocklist", help="Path to a blocklist file for profanity checking.")
    
    args = parser.parse_args()

    # Determine the paths for the dictionary and blocklist.
    # Use the user-provided path if available, otherwise fall back to the packaged default.
    dictionary_path = args.dictionary
    if dictionary_path is None:
        try:
            dictionary_path = importlib.resources.files('slithyt.data').joinpath('en-dict.dat')
        except FileNotFoundError:
            print("WARNING: Default dictionary 'en-dict.dat' not found. No dictionary will be used.")

    blocklist_path = args.blocklist
    if blocklist_path is None:
        try:
            blocklist_path = importlib.resources.files('slithyt.data').joinpath('en-block.dat')
        except FileNotFoundError:
            print("WARNING: Default blocklist 'en-block.dat' not found. No blocklist will be used.")

    if args.command == "generate":
        print(f"INFO: Training model from '{args.corpus}'...")
        model = generator.train_model(args.corpus, n=args.ngram_size)
        
        if not model:
            print("ERROR: Model training failed. Exiting.")
            return

        print(f"INFO: Generating {args.count} words...")
        generated_words = []
        max_attempts = args.count * 100 # Try up to 100 times for each requested word
        attempts = 0

        while len(generated_words) < args.count and attempts < max_attempts:
            word = generator.generate_word(model, args.min_len, args.max_len, n=args.ngram_size)
            
            if validator.validate_word(
                word,
                matches_regex=args.matches_regex,
                reject_regex=args.reject_regex,
                dictionary_path=dictionary_path,
                blocklist_path=blocklist_path,
                min_sentiment=args.min_sentiment,
                max_sentiment=args.max_sentiment
            ):
                if word not in generated_words:
                    generated_words.append(word)
                    print(f"  - {word}")
            
            attempts += 1
        
        if len(generated_words) < args.count:
            print(f"\nWARNING: Could only generate {len(generated_words)}/{args.count} valid words.")
            print("Try relaxing your constraints or using a larger corpus.")


    elif args.command == "validate":
        # For validation, we don't need to pass sentiment args to the validator,
        # but we do want to calculate and display the score.
        is_valid = validator.validate_word(
            args.word,
            dictionary_path=dictionary_path,
            blocklist_path=blocklist_path,
        )
        score = sentiment.analyze_word_sentiment(args.word)
        result = "Valid" if is_valid else "Invalid"
        
        print(f"Validating word: '{args.word}'")
        print(f"  - Validation Result: {result}")
        print(f"  - Sentiment Score:   {score:.3f} (0=neg, 0.5=neu, 1=pos)")

if __name__ == "__main__":
    main()
