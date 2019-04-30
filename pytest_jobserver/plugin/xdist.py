import os
from typing import Any, List

import pytest
from _pytest.config import Config
from _pytest.nodes import Node

from xdist.dsession import LoadScheduling

from ..filesystem import FileDescriptorsRW


class JobserverLoadScheduling(LoadScheduling):
    def __init__(self, config: Config, log: Any, fds: FileDescriptorsRW):
        super().__init__(config, log)
        self._fd_read, self._fd_write = fds
        self._tokens: List[bytes] = []

    def mark_test_complete(self, *args: Any, **kwargs: Any) -> None:
        # jobserver
        token = self._tokens.pop()
        os.write(self._fd_write, token)
        # jobserver
        super().mark_test_complete(*args, **kwargs)

    def _send_tests(self, node: Node, num: int) -> None:
        tests_per_node = self.pending[:num]
        if tests_per_node:
            del self.pending[:num]
            self.node2pending[node].extend(tests_per_node)
            # jobserver
            for _ in range(num):
                token = os.read(self._fd_read, 1)
                self._tokens.append(token)
            # jobserver
            node.send_runtest_some(tests_per_node)


class JobserverXdistPlugin(object):
    def __init__(self, fds: FileDescriptorsRW):
        self._fds = fds

    @pytest.hookimpl(tryfirst=True)
    def pytest_xdist_make_scheduler(self, config: Config, log: Any) -> object:
        """ return a node scheduler implementation """
        return JobserverLoadScheduling(config, log, self._fds)
