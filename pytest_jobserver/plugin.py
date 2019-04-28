import os
import stat
from typing import Any, Iterator

import pytest

from .metadata import VERSION

__version__ = VERSION


def pytest_addoption(parser: Any) -> None:
    group = parser.getgroup("jobserver")
    group.addoption(
        "--jobserver",
        action="store",
        metavar="FILE",
        help="Named pipe to use as jobserver.",
    )


class JobserverPlugin(object):
    def __init__(self, file: str):
        self.jobserver = open(file, "r+b", 0)

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item: Any) -> Iterator[Any]:
        token = self.jobserver.read(1)
        yield
        self.jobserver.write(token)


def is_fifo(path: str) -> bool:
    return stat.S_ISFIFO(os.stat(path).st_mode)


def is_rw_ok(path: str) -> bool:
    return os.access(path, os.R_OK | os.W_OK)


def pytest_configure(config: Any) -> None:
    jobserver_path = config.getoption("jobserver", default=None)
    if jobserver_path:
        if os.path.exists(jobserver_path) is False:
            raise pytest.UsageError(
                "jobserver doesn't exist: {}".format(jobserver_path)
            )

        if is_fifo(jobserver_path) is False:
            raise pytest.UsageError(
                "jobserver is not a fifo: {}".format(jobserver_path)
            )

        if is_rw_ok(jobserver_path) is False:
            raise pytest.UsageError(
                "jobserver is not read/writeable to current user: {}".format(
                    jobserver_path
                )
            )

        config.pluginmanager.register(JobserverPlugin(jobserver_path))
