# SlithyT

A tool for generating novel, plausible, and pronounceable words based on linguistic corpuses.

The name is a reference to the "slithy toves" in Lewis Carroll's poem "Jabberwocky".

## Installation

```bash
pip install .
```

## Usage

```bash
# Generate 10 words based on a corpus
slithyt generate --corpus path/to/your/corpus.txt

# Generate highly positive words
slithyt generate --corpus path/to/corpus.txt --min-sentiment 0.8

# Generate highly negative words
slithyt generate --corpus path/to/corpus.txt --max-sentiment 0.2
```
