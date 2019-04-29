import os
from typing import Any, Iterator, NewType, Optional

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item

from .filesystem import is_fifo, is_rw_ok
from .metadata import VERSION

__version__ = VERSION

FileDescriptor = NewType("FileDescriptor", int)


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("jobserver")
    group.addoption(
        "--jobserver",
        action="store",
        metavar="FILE",
        help="Named pipe to use as jobserver.",
    )


class JobserverPlugin(object):
    def __init__(self, fd: FileDescriptor):
        self._fifo = fd

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item: Item) -> Iterator[Any]:
        token = os.read(self._fifo, 1)
        yield
        os.write(self._fifo, token)


def jobserver_from_options(config: Config) -> Optional[FileDescriptor]:
    jobserver_path = config.getoption("jobserver", default=None)
    if jobserver_path is None:
        return None

    if os.path.exists(jobserver_path) is False:
        raise pytest.UsageError("jobserver doesn't exist: {}".format(jobserver_path))

    if is_fifo(jobserver_path) is False:
        raise pytest.UsageError("jobserver is not a fifo: {}".format(jobserver_path))

    if is_rw_ok(jobserver_path) is False:
        raise pytest.UsageError(
            "jobserver is not read/writeable to current user: {}".format(jobserver_path)
        )

    return FileDescriptor(os.open(jobserver_path, os.O_RDWR))


def pytest_configure(config: Config) -> None:
    jobserver_fd = jobserver_from_options(config)
    if jobserver_fd:
        config.pluginmanager.register(JobserverPlugin(jobserver_fd))
