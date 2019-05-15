import os
import threading
from typing import Any, Iterator

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item

from .configure import (
    jobserver_from_env_make,
    jobserver_from_env_pytest,
    jobserver_from_options,
)
from .metadata import VERSION
from .system import FileDescriptorsRW

__version__ = VERSION


class JobserverPlugin(object):
    def __init__(self, fds: FileDescriptorsRW):
        self._fd_read, self._fd_write = fds
        self._thread_locals = threading.local()

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item: Item) -> Iterator[Any]:
        token = os.read(self._fd_read, 1)
        self._thread_locals.token = ord(token)
        yield
        os.write(self._fd_write, token)

    @pytest.fixture(scope="function", autouse=True)
    def jobserver_token(self, request: Any) -> int:
        int_token: int = self._thread_locals.token
        return int_token

    def pytest_report_header(self, config: Config) -> str:
        return "jobserver: configured at file descriptors (read: {}, write: {})".format(
            self._fd_read, self._fd_write
        )


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("jobserver")
    group.addoption(
        "--jobserver",
        action="store",
        metavar="FILE",
        help="Named pipe to use as jobserver. If xdist is active, this is the filepath as seen by the worker nodes.",
    )


def pytest_configure(config: Config) -> None:
    jobserver_fds = (
        jobserver_from_options(config)
        or jobserver_from_env_pytest()
        or jobserver_from_env_make(config)
    )
    if jobserver_fds:
        plugin = JobserverPlugin(jobserver_fds)
        config.pluginmanager.register(plugin)
