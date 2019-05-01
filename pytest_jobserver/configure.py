import argparse
import os
import shlex
from typing import Optional

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser

from .filesystem import FileDescriptor, FileDescriptorsRW, is_fifo, is_rw_ok
from .metadata import VERSION
from .plugin import JobserverPlugin

__version__ = VERSION


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("jobserver")
    group.addoption(
        "--jobserver",
        action="store",
        metavar="FILE",
        help="Named pipe to use as jobserver. If xdist is active, this is the filepath as seen by the worker nodes.",
    )


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


def jobserver_from_env(config: Config) -> Optional[FileDescriptorsRW]:
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

    if config.pluginmanager.hasplugin("xdist"):
        raise pytest.UsageError(
            "pytest-jobserver does not support using pytest-xdist with MAKEFLAGS"
        )

    fd_read, fd_write = tuple(FileDescriptor(int(fd)) for fd in fds.split(","))

    return (fd_read, fd_write)


def pytest_configure(config: Config) -> None:
    jobserver_fds = jobserver_from_options(config)
    if jobserver_fds is None:
        jobserver_fds = jobserver_from_env(config)

    if jobserver_fds:
        print("Configuring jobserver with fds: {}".format(jobserver_fds))
        plugin = JobserverPlugin(jobserver_fds)
        config.pluginmanager.register(plugin)
