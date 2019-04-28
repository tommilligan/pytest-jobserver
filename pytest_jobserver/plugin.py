import os
import stat

import pytest


def pytest_addoption(parser):
    group = parser.getgroup("jobserver")
    group.addoption(
        "--jobserver",
        action="store",
        metavar="FILE",
        help="Named pipe to use as jobserver.",
    )


class JobserverPlugin(object):
    def __init__(self, file):
        self.jobserver = open(file, "r+b", 0)

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item):
        token = self.jobserver.read(1)
        yield
        self.jobserver.write(token)


def is_fifo(path):
    return stat.S_ISFIFO(os.stat(path).st_mode)


def is_rw_ok(path):
    return os.access(path, os.R_OK | os.W_OK)


def pytest_configure(config):
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
