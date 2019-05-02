import os
from typing import Any, Callable, Iterator, NewType, TypeVar

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item

from .configure import jobserver_from_env, jobserver_from_options
from .metadata import VERSION
from .system import FileDescriptorsRW

__version__ = VERSION

Token = NewType("Token", bytes)
_T = TypeVar("_T")


class JobserverError(Exception):
    pass


def _wrap_jobserver_error(
    message: str
) -> Callable[[Callable[..., _T]], Callable[..., _T]]:
    def outer(function: Callable[..., _T]) -> Callable[..., _T]:
        def inner(*args: Any, **kwargs: Any) -> _T:
            try:
                return function(*args, **kwargs)
            except Exception as error:
                raise JobserverError(message) from error

        return inner

    return outer


class JobserverPlugin(object):
    def __init__(self, fds: FileDescriptorsRW):
        self._fd_read, self._fd_write = fds

    @_wrap_jobserver_error("Failed to read token from jobserver")
    def _token_read(self) -> Token:
        os.fstat(self._fd_read)
        return Token(os.read(self._fd_read, 1))

    @_wrap_jobserver_error("Failed to write token to jobserver")
    def _token_write(self, token: Token) -> None:
        os.write(self._fd_write, token)

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item: Item) -> Iterator[Any]:
        """Get a token, run the test, return the token."""
        token = self._token_read()
        yield
        self._token_write(token)

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
    jobserver_fds = jobserver_from_options(config) or jobserver_from_env(config)
    if jobserver_fds:
        plugin = JobserverPlugin(jobserver_fds)
        config.pluginmanager.register(plugin)
