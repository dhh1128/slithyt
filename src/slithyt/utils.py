import gzip
from importlib.resources import files


def data_path(name: str) -> str:
    """Return the filesystem path to a bundled data file (corpus, dictionary,
    blocklist) shipped under ``slithyt/data/``.

    Uses ``importlib.resources`` rather than ``__file__`` arithmetic so it
    resolves correctly regardless of how the package was installed.
    """
    return str(files("slithyt") / "data" / name)


def open_any(file_path: str):
    """
    Opens a file, transparently handling whether it is gzipped or plain text
    by checking for the gzip magic number.

    Args:
        file_path: The path to the file to open.

    Returns:
        A file handle ready for reading in text mode.
    """
    with open(file_path, 'rb') as f:
        is_gzipped = (f.read(2) == b'\x1f\x8b')
    
    # Return the correct file handle based on the check
    if is_gzipped:
        return gzip.open(file_path, 'rt', encoding="utf-8")
    else:
        return open(file_path, 'r', encoding="utf-8")