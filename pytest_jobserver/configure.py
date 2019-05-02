import argparse
import os
import shlex
from typing import Optional

import pytest
from _pytest.config import Config

from .system import (
    FileDescriptor,
    FileDescriptorsRW,
    environ_get_first,
    is_fifo,
    is_rw_ok,
)

MAKEFLAGS_ENVIRONMENT_VARIABLES = ("CARGO_MAKEFLAGS", "MAKEFLAGS", "MFLAGS")


def path_to_file_descriptors(jobserver_path: str) -> Optional[FileDescriptorsRW]:
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


def jobserver_from_options(config: Config) -> Optional[FileDescriptorsRW]:
    jobserver_path = config.getoption("jobserver", default=None)
    return path_to_file_descriptors(jobserver_path) if jobserver_path else None


def jobserver_from_env_pytest() -> Optional[FileDescriptorsRW]:
    jobserver_path = os.environ.get("PYTEST_JOBSERVER")
    return path_to_file_descriptors(jobserver_path) if jobserver_path else None


def jobserver_from_env_make(config: Config) -> Optional[FileDescriptorsRW]:
    makeflags = environ_get_first(MAKEFLAGS_ENVIRONMENT_VARIABLES)
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
