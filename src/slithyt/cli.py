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
    gen_parser.add_argument("--min-len", type=int, default=5, help="Minimum word length. (Corpus should have words of this length.)")
    gen_parser.add_argument("--max-len", type=int, default=10, help="Maximum word length.")
    gen_parser.add_argument("--matches-regex", help="A regex pattern the word must match.")
    gen_parser.add_argument("--reject-regex", help="A regex pattern the word must not match.")
    gen_parser.add_argument("--dictionary", help="Path to a dictionary file to check for novelty.")
    gen_parser.add_argument("--blocklist", help="Path to a blocklist file for profanity checking.")
    gen_parser.add_argument("--ngram-size", type=int, default=3, help="The n-gram size for the model (e.g., 3 for trigrams).")
    gen_parser.add_argument("--min-sentiment", type=float, help="Minimum sentiment score (0.0-1.0). Words below this are rejected.")
    gen_parser.add_argument("--max-sentiment", type=float, help="Maximum sentiment score (0.0-1.0). Words above this are rejected.")
    gen_parser.add_argument("--min-pronounceability", type=float, help="Minimum pronounceability score (0.0-1.0). Words below this are rejected.")
    gen_parser.add_argument("--allow-corpus-words", action="store_true", help="Allow words from the training corpus to be generated.")

    val_parser = subparsers.add_parser("validate", help="Validate a potential word.")
    val_parser.add_argument("word", help="The word to validate.")
    val_parser.add_argument("--dictionary", help="Path to a dictionary file to check for novelty.")
    val_parser.add_argument("--blocklist", help="Path to a blocklist file for profanity checking.")
    
    args = parser.parse_args()

    # Determine default file paths using pathlib relative to this script
    module_path = pathlib.Path(__file__).parent
    default_dict_path = module_path / 'data' / 'en-dict.dat'
    default_block_path = module_path / 'data' / 'en-block.dat'

    # Load the blocklist set once for efficiency.
    block_to_load = args.blocklist if args.blocklist is not None else default_block_path
    blocklist_set = validator.load_word_set(str(block_to_load))

    # Load the dictionary set, but only if it's not the same as the corpus.
    dictionary_set = set()
    if not (hasattr(args, 'corpus') and str(default_dict_path) == args.corpus):
        dict_to_load = args.dictionary if args.dictionary is not None else default_dict_path
        dictionary_set = validator.load_word_set(str(dict_to_load))

    if args.command == "generate":
        print(f"INFO: Training model from '{args.corpus}'...")
        model, corpus_set = generator.train_from_corpus(args.corpus, n=args.ngram_size)
        if not model: return

        # By default, reject words from the corpus unless the flag is passed.
        corpus_rejection_set = None if args.allow_corpus_words else corpus_set
        
        print(f"INFO: Generating {args.count} words...")
        generated_words = []
        for _ in range(args.count * 100):
            if len(generated_words) >= args.count: break