# SlithyT

A tool for generating novel, plausible, and pronounceable words based on
linguistic corpuses.

The name is a reference to the "slithy toves" in Lewis Carroll's poem
"Jabberwocky".

(Code was written substantially by AI, although I did a fair amount of reviewing,
criticizing, revising and debugging.)

## Install

`slithyt` is published on [PyPI](https://pypi.org/project/slithyt/). The
recommended install puts it on your `PATH` as a standalone tool via
[uv](https://docs.astral.sh/uv/) (needs Python 3.11+):

```sh
uv tool install slithyt
```

Then **`slithyt update`** self-updates to the latest release (it runs
`uv tool upgrade slithyt`). `slithyt` also prints a one-line nudge, at most once
a day, when a newer version exists — silence it with `SLITHYT_NO_UPDATE_CHECK=1`
or `slithyt --no-update-check`. The check is offline-safe (any network failure is
ignored).

`slithyt --version` prints the installed version.

Other install paths:

```sh
pipx install slithyt            # if you prefer pipx
pip install slithyt             # into the current environment

# from source:
git clone https://github.com/dhh1128/slithyt && cd slithyt
uv tool install .               # or: pip install .
```

## Usage

Generate a word that looks/sounds like it fits with other words in a given
corpus. Similarity is determined partly by ngram analysis and partly by
pronunciation.

You can make your own corpus, or use one of the pregenerated ones bundled with
the package (under `slithyt/data/`):

* Astronomy names (stars, galaxies, planets)
* Transliterated Greek, Latin, Hebrew, Egyptian names
* Harry Potter or Star Wars names
* Drug names
* Latin words from biology taxonomy (genus, species)

You can also use the whole dictionary as your corpus, in which case you will get
words with no particular flavor to them. A good corpus has at least a couple
hundred words in it.

By default, generated words are *novel*, meaning they won't appear in the corpus
you reference. You can also add a blocklist to avoid generating curse words,
words that violate trademarks or spam filters, etc.

All corpora and dictionary/block list files used by this tool are text files
having a single word per line, and can optionally be gzipped. Sentiment
analysis, pronounceability, and rhyming are moderately English-centric, though
they tolerate romance and germanic languages a bit as well.

```sh
# Generate 10 realistic words that sound like they belong in a corpus.
slithyt generate --corpus path/to/your/corpus.txt

# Generate words that have a positive connotation due to sound symbolism
# (see https://en.wikipedia.org/wiki/Sound_symbolism), using n=4 for ngram
# analysis. (--ngram-size is a tradeoff. Default is 3. Bigger values make the
# resonance with the corpus stronger, but also make it harder to be creative;
# it may be impossible to generate words if you go too high. Smaller values
# give the algorithm more freedom in both size and character sequence, but the
# output might sound less like the corpus.)
slithyt generate --corpus path/to/corpus.txt --min-sentiment 0.8 --ngram-size 4

# Generate words between 4 and 8 characters long that are at least moderately
# pronounceable. (Pronounceability depends partly on the speaker's judgment;
# slithyt uses a simple algorithm to predict scores from 0 (hardest) to 1
# (easiest), but the corpus may affect how reasonable 0.5 is. These values
# constrain output but may make generation impossible if nothing in the corpus
# is as small or as large as what was requested.)
slithyt generate --corpus path/to/corpus.txt --min-len 4 --max-len 8 --min-pronounceability 0.5

# Generate 5 words that rhyme with synergy.
slithyt generate --count 5 --rhymes-with synergy

# Report the rhyming analysis for synergy. (Only known words are usable as a
# rhyming template; passing made-up words here will do nothing useful.)
slithyt rhyme synergy

# Check whether a particular made-up word would pass certain tests.
slithyt validate synerjee
```

## Commands

| Command | What it does |
| --- | --- |
| `slithyt generate --corpus <file> [options]` | Generate novel words that resemble a corpus. |
| `slithyt generate --rhymes-with <word> [options]` | Generate novel words that rhyme with a known word. |
| `slithyt validate <word>` | Report whether a word is novel/allowed, plus its sentiment and pronounceability. |
| `slithyt rhyme <word>` | Print the phonetic breakdown and rhyme signature of a known word. |
| `slithyt build-cache [--corpus <file>]` | (Re)build the phonetic + transcription models used for rhyming. |
| `slithyt update [--check]` | Self-update to the latest published version (`--check` only reports). |
| `slithyt --version` | Print the installed version. |

Common `generate` options: `--count`, `--min-len`, `--max-len`, `--ngram-size`,
`--matches-regex`, `--reject-regex`, `--dictionary`, `--blocklist`,
`--min-sentiment`, `--max-sentiment`, `--min-pronounceability`,
`--allow-corpus-words`.

## Rhyming and the model cache

Rhyme generation (`--rhymes-with`) needs a phonetic model and a transcription
model derived from a pronunciation dictionary. These are **built automatically
on first use** and cached under `~/.slithyt/data/`, so the first rhyme run takes
a few moments; later runs are instant. Run `slithyt build-cache` to precompute
them, or `slithyt build-cache --corpus <file>` to derive them from your own
pronunciation corpus (e.g. to reflect the sensibilities of another language
community).

## Development

```sh
uv run --extra dev python -m pytest -q     # run the test suite
uv build                                   # build the wheel + sdist into dist/
```

`slithyt.update` is unit-tested fully offline via injected network/subprocess
seams; the generation/validation/rhyming modules have their own tests under
`tests/`.

## Releasing

`scripts/release.py` cuts a release. It bumps the version in `pyproject.toml`,
runs the guardrails (clean tree, on `main`, in sync with `origin`, tests pass),
commits with a DCO sign-off, and pushes `main` plus an annotated `vX.Y.Z` tag.
The tag push triggers the [`release`](.github/workflows/release.yml) workflow,
which builds the wheel + sdist and publishes them to PyPI via trusted publishing
(OIDC — no stored token).

```sh
python3 scripts/release.py                       # patch bump, default message
python3 scripts/release.py --minor -m "..."      # minor / --major / --patch
python3 scripts/release.py --set 1.2.0 -m "..."  # explicit version
```

## License

MIT.
