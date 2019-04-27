import pytest


def pytest_addoption(parser):
    group = parser.getgroup("jobserver")
    group.addoption(
        "--jobserver",
        action="store",
        metavar="FILE",
        help="Named pipe to use as jobserver.",
    )

    parser.addini("jobserver", "Named pipe to use as jobserver.")


class JobserverPlugin(object):
    """Simple plugin to defer pytest-xdist hook functions."""

    def __init__(self, file):
        self.jobserver = open(file, "r+b", 0)

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_protocol(self, item):
        token = self.jobserver.read(1)
        yield
        self.jobserver.write(b"I")


def pytest_configure(config):
    jobserver_file = config.getoption("jobserver", default=None)
    if jobserver_file:
        config.pluginmanager.register(JobserverPlugin(jobserver_file))
