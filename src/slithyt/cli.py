import argparse
import pathlib
from . import generator, validator, sentiment, pronounce

def main():
    """Main function for the command-line interface."""
    parser = argparse.ArgumentParser(description="SlithyT: A plausible word generation tool.")
    subparsers = parser.add_subparsers(dest="command", required=True)

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
    gen_parser.add_argument("--min-pronounceability", type=float, help="Minimum pronounceability score (0.0-1.0). Words below this are rejected.")

    val_parser = subparsers.add_parser("validate", help="Validate a potential word.")
    val_parser.add_argument("word", help="The word to validate.")
    val_parser.add_argument("--dictionary", help="Path to a dictionary file to check for novelty.")
    val_parser.add_argument("--blocklist", help="Path to a blocklist file for profanity checking.")
    
    args = parser.parse_args()

    # Determine default file paths using pathlib relative to this script
    module_path = pathlib.Path(__file__).parent
    default_dict_path = module_path / 'data' / 'en-dict.dat'
    default_block_path = module_path / 'data' / 'en-block.dat'

    # Load the dictionary and blocklist sets once for efficiency.
    # Use user-provided path if available, otherwise use the default.
    dict_to_load = args.dictionary if args.dictionary is not None else default_dict_path
    block_to_load = args.blocklist if args.blocklist is not None else default_block_path
    
    dictionary_set = validator.load_word_set(str(dict_to_load))
    blocklist_set = validator.load_word_set(str(block_to_load))

    if args.command == "generate":
        model = generator.train_model(args.corpus, n=args.ngram_size)
        if not model: return
        
        print(f"INFO: Generating {args.count} words...")
        generated_words = []
        for _ in range(args.count * 100):
            if len(generated_words) >= args.count: break
            word = generator.generate_word(model, args.min_len, args.max_len, n=args.ngram_size)
            if word and word not in generated_words and validator.validate_word(
                word, args.matches_regex, args.reject_regex, dictionary_set,
                blocklist_set, args.min_sentiment, args.max_sentiment, args.min_pronounceability
            ):
                generated_words.append(word)
                print(f"  - {word}")

    elif args.command == "validate":
        is_valid = validator.validate_word(args.word, dictionary_set=dictionary_set, blocklist_set=blocklist_set)
        s_score = sentiment.analyze_word_sentiment(args.word)
        p_score = pronounce.score_pronounceability(args.word)
        print(f"Validating word: '{args.word}'")
        print(f"  - Validation Result: {'Valid' if is_valid else 'Invalid'}")
        print(f"  - Sentiment Score:        {s_score:.3f}")
        print(f"  - Pronounceability Score: {p_score:.3f}")

if __name__ == "__main__":
    main()