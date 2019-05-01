import os


def make_jobserver(dir_: str, name: str, size: int) -> str:
    """Create a fifo with the given name and directory. Return the absolute file path.

    :param str dir_: Directory to create jobserver fifo in.
    :param str name: Name of fifo.
    :param int size: Number of tokens to preload into the jobserver.
    """
    # Create our fifo
    fifo_path = os.path.join(dir_, name)
    os.mkfifo(fifo_path)

    # Open it as nonblocking, so we can write tokens into it straight away
    fifo = os.open(fifo_path, os.O_RDWR | os.O_NONBLOCK)

    # Write some tokens into it
    tokens = b"X" * size
    os.write(fifo, tokens)

    return fifo_path
