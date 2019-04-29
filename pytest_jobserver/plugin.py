import argparse
import os
import shlex
from typing import Any, Iterator, NewType, Optional, Tuple

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item

from .filesystem import is_fifo, is_rw_ok
from .load_scheduler import JobserverLoadScheduling
from .metadata import VERSION

__version__ = VERSION

FileDescriptor = NewType("FileDescriptor", int)
# A 2-tuple of file descriptors, representing a read/write pair
FileDescriptorsRW = Tuple[FileDescriptor, FileDescriptor]


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("jobserver")
    group.addoption(
        "--jobserver",
        action="store",
        metavar="FILE",
        help="Named pipe to use as jobserver.",
    )


class JobserverPlugin(object):
    def __init__(self, fds: FileDescriptorsRW):
        self._fd_read, self._fd_write = fds

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item: Item) -> Iterator[Any]:
        token = os.read(self._fd_read, 1)
        yield
        os.write(self._fd_write, token)


class JobserverXdistPlugin(object):
    def __init__(self, fds: FileDescriptorsRW):
        self._fds = fds

    @pytest.hookimpl(tryfirst=True)
    def pytest_xdist_make_scheduler(self, config: Config, log):  # type: ignore
        """ return a node scheduler implementation """
        return JobserverLoadScheduling(config, log, self._fds)  # type: ignore


def jobserver_from_options(config: Config) -> Optional[FileDescriptorsRW]:
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

    fd_rw = FileDescriptor(os.open(jobserver_path, os.O_RDWR))
    return (fd_rw, fd_rw)


def jobserver_from_env() -> Optional[FileDescriptorsRW]:
    makeflags = (
        os.environ.get("CARGO_MAKEFLAGS")
        or os.environ.get("MAKEFLAGS")
        or os.environ.get("MFLAGS")
    )

    if makeflags is None:
        return None

    parser = argparse.ArgumentParser(prog="makeflags")
    parser.add_argument("--jobserver-fds", default=None)
    parser.add_argument("--jobserver-auth", default=None)
    args, _ = parser.parse_known_args(shlex.split(makeflags))

    fds = args.jobserver_fds or args.jobserver_auth
    if fds is None:
        return None

    fd_read, fd_write = tuple(FileDescriptor(int(fd)) for fd in fds.split(","))

    return (fd_read, fd_write)


def pytest_configure(config: Config) -> None:
    jobserver_fds = jobserver_from_options(config) or jobserver_from_env()
    if jobserver_fds:
        print("Configuring jobserver with fds: {}".format(jobserver_fds))
        if config.pluginmanager.hasplugin("xdist"):
            plugin: Any = JobserverXdistPlugin(jobserver_fds)
        else:
            plugin = JobserverPlugin(jobserver_fds)
        config.pluginmanager.register(plugin)
