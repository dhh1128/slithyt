# Improve --rhymes-with output quality (transcription algorithm)
kind: idea
tags: rhyme
created: 2026-06-19T23:44Z

- 2026-06-19T23:45Z Rhyme generation via --rhymes-with produces rough, often unpronounceable words (e.g. 'borcrineerynrji' for synergy). Root cause is the phoneme->grapheme transcription model (build.build_transcription_model keeps only the top-3 spellings per base phoneme; rhyme.transcribe_word greedily applies them) plus the phonetic n-gram generator. Pre-existing behavior, untouched in the 1.1.0 modernization. Improving it means a better transcription model and/or post-filtering by pronounceability score.
