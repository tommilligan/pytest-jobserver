import os
from typing import Any, Iterator

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item

from .configure import jobserver_from_env, jobserver_from_options
from .system import FileDescriptorsRW


class JobserverPlugin(object):
    def __init__(self, fds: FileDescriptorsRW):
        self._fd_read, self._fd_write = fds

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item: Item) -> Iterator[Any]:
        token = os.read(self._fd_read, 1)
        yield
        os.write(self._fd_write, token)


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("jobserver")
    group.addoption(
        "--jobserver",
        action="store",
        metavar="FILE",
        help="Named pipe to use as jobserver. If xdist is active, this is the filepath as seen by the worker nodes.",
    )


def pytest_configure(config: Config) -> None:
    jobserver_fds = jobserver_from_options(config)
    if jobserver_fds is None:
        jobserver_fds = jobserver_from_env(config)

    if jobserver_fds:
        print("jobserver configured with file descriptors: {}".format(jobserver_fds))
        plugin = JobserverPlugin(jobserver_fds)
        config.pluginmanager.register(plugin)
