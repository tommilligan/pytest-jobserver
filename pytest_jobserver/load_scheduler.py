import os

from xdist.dsession import LoadScheduling


class JobserverLoadScheduling(LoadScheduling):
    def __init__(self, config, log, fds):  # type: ignore
        super().__init__(config, log)
        self._fd_read, self._fd_write = fds
        self._tokens = []

    def mark_test_complete(self, *args, **kwargs):  # type: ignore
        # jobserver
        token = self._tokens.pop()
        os.write(self._fd_write, token)
        # jobserver
        super().mark_test_complete(*args, **kwargs)

    def _send_tests(self, node, num):  # type: ignore
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
