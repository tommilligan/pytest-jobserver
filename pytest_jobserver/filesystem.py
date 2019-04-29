import os
import stat


def is_fifo(path: str) -> bool:
    return stat.S_ISFIFO(os.stat(path).st_mode)


def is_rw_ok(path: str) -> bool:
    return os.access(path, os.R_OK | os.W_OK)
