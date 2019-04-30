import os
import stat
from typing import NewType, Tuple

FileDescriptor = NewType("FileDescriptor", int)
# A 2-tuple of file descriptors, representing a read/write pair
FileDescriptorsRW = Tuple[FileDescriptor, FileDescriptor]


def is_fifo(path: str) -> bool:
    return stat.S_ISFIFO(os.stat(path).st_mode)


def is_rw_ok(path: str) -> bool:
    return os.access(path, os.R_OK | os.W_OK)
