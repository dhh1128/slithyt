import argparse
import pathlib
from . import generator, validator, sentiment, pronounce, rhyme

def main():
    """Main function for the command-line interface."""
    parser = argparse.ArgumentParser(description="SlithyT: A plausible word generation tool.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Generate command ---
    gen_parser = subparsers.add_parser("generate", help="Generate new words.")
    gen_parser.add_argument("--corpus", help="Path to the corpus file for training. Required unless using --rhymes-with.")
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
    gen_parser.add_argument("--rhymes-with", help="Generate words that rhyme with this word.")
    gen_parser.add_argument("--allow-corpus-words", action="store_true", help="Allow words from the training corpus to be generated.")

    # --- Validate command ---
    val_parser = subparsers.add_parser("validate", help="Validate a potential word.")
    val_parser.add_argument("word", help="The word to validate.")
    val_parser.add_argument("--dictionary", help="Path to a dictionary file to check for novelty.")
    val_parser.add_argument("--blocklist", help="Path to a blocklist file for profanity checking.")

    # --- Rhyme command ---
    rhyme_parser = subparsers.add_parser("rhyme", help="Get phonetic info for a word.")
    rhyme_parser.add_argument("word", help="The word to analyze for rhyming.")
    
    args = parser.parse_args()

    # --- Argument Validation ---
    if args.command == "generate" and not args.corpus and not args.rhymes_with:
        parser.error("--corpus is required unless --rhymes-with is used.")

    # --- Path and Data Loading ---
    module_path = pathlib.Path(__file__).parent
    default_dict_path = module_path / 'data' / 'en-dict.txt.gz'
    default_block_path = module_path / 'data' / 'en-block.txt.gz'

    block_to_load = args.blocklist if args.blocklist is not None else default_block_path
    blocklist_set = validator.load_word_set(str(block_to_load))

    dictionary_set = set()
    dict_to_load = args.dictionary if args.dictionary is not None else default_dict_path
    # Optimization: Don't load dictionary if it's the same as the corpus (for standard generation)
    if not (args.command == "generate" and hasattr(args, 'corpus') and args.corpus and str(dict_to_load) == args.corpus):
        dictionary_set = validator.load_word_set(str(dict_to_load))

    # --- Command Execution ---
    if args.command == "generate":
        if args.rhymes_with:
            # --- Rhyme Generation Logic ---
            cache_dir = pathlib.Path.home() / '.slithyt' / 'data'
            phonetic_model_path = cache_dir / 'phonetic-model.dat'
            transcription_model_path = cache_dir / 'transcription-model.dat'

            phonetic_model = rhyme.load_phonetic_model(str(phonetic_model_path))
            if not phonetic_model: return
            transcription_model = rhyme.load_transcription_model(str(transcription_model_path))
            if not transcription_model: return

            target_phonemes = rhyme.get_phonetic_breakdown(args.rhymes_with)
            if not target_phonemes:
                print(f"ERROR: Cannot find '{args.rhymes_with}' in phonetic dictionary.")
                return

            signature = rhyme.get_rhyme_signature(target_phonemes)
            if not signature:
                print(f"ERROR: Cannot find a valid rhyme signature for '{args.rhymes_with}'.")
                return
            
            print(f"INFO: Generating words that rhyme with '{args.rhymes_with}'...")
            generated_words = []
            for _ in range(args.count * 200):
                if len(generated_words) >= args.count: break
                
                new_phonemes = rhyme.generate_phonetic_word(phonetic_model, signature)
                if not new_phonemes: continue

                word = rhyme.transcribe_word(transcription_model, new_phonemes)

                if word and word not in generated_words and validator.validate_word(
                    word, args.matches_regex, args.reject_regex, dictionary_set, blocklist_set,
                    None, args.min_sentiment, args.max_sentiment, args.min_pronounceability
                ):
                    generated_words.append(word)
                    print(f"  - {word}")
        else:
            # --- Standard Generation Logic ---
            print(f"INFO: Training model from '{args.corpus}'...")
            model, corpus_set = generator.train_from_corpus(args.corpus, n=args.ngram_size)
            if not model: return

            corpus_rejection_set = None if args.allow_corpus_words else corpus_set
            
            print(f"INFO: Generating {args.count} words...")
            generated_words = []
            for _ in range(args.count * 100):
                if len(generated_words) >= args.count: break
                word = generator.generate_word(model, args.min_len, args.max_len, n=args.ngram_size)
                if word and word not in generated_words and validator.validate_word(
                    word, args.matches_regex, args.reject_regex, dictionary_set, blocklist_set,
                    corpus_rejection_set, args.min_sentiment, args.max_sentiment, args.min_pronounceability
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

    elif args.command == "rhyme":
        print(f"Analyzing word: '{args.word}'")
        phonemes = rhyme.get_phonetic_breakdown(args.word)
        if not phonemes:
            print("  - Word not found in the phonetic dictionary.")
            return
        
        print(f"  - Phonetic Breakdown: {' '.join(phonemes)}")
        
        signature = rhyme.get_rhyme_signature(phonemes)
        if signature:
            print(f"  - Rhyme Signature:    {' '.join(signature)}")

if __name__ == "__main__":
    main()