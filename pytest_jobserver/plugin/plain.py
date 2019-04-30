import os
from typing import Any, Iterator

import pytest
from _pytest.nodes import Item

from ..filesystem import FileDescriptorsRW


class JobserverPlugin(object):
    def __init__(self, fds: FileDescriptorsRW):
        self._fd_read, self._fd_write = fds

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item: Item) -> Iterator[Any]:
        token = os.read(self._fd_read, 1)
        yield
        os.write(self._fd_write, token)
