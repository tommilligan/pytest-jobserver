import time
from typing import Any

from pytest_jobserver.configure import MAKEFLAGS_ENVIRONMENT_VARIABLES

from .jobserver import make_jobserver

TestDir = Any


# Actual tests


def test_help_message(testdir: TestDir) -> None:
    result = testdir.runpytest("--help")
    # Check our options have been registered
    result.stdout.fnmatch_lines(["jobserver:", "*--jobserver*"])


def test_noop(testdir: TestDir) -> None:
    """Test that if nothing is set, everything is fine."""
    testdir.makepyfile(
        """
        def test_pass(request):
            pass
    """
    )
    for makeflag_environment_variable in MAKEFLAGS_ENVIRONMENT_VARIABLES:
        testdir.monkeypatch.delenv(makeflag_environment_variable, raising=False)
    result = testdir.runpytest("-v")
    assert result.ret == 0


def test_config_options(testdir: TestDir) -> None:
    testdir.makepyfile(
        """
        def test_plugin_setup(request):
            assert 'jobserver_fifo' == request.config.getoption('jobserver')
    """
    )
    make_jobserver(testdir.tmpdir, "jobserver_fifo", 1)

    result = testdir.runpytest("-v", "--jobserver", "jobserver_fifo")

    result.stdout.fnmatch_lines(["*::test_plugin_setup PASSED*"])
    result.stdout.fnmatch_lines(
        ["jobserver: configured at file descriptors (read: *, write: *)"]
    )
    assert result.ret == 0


def test_config_env_pytest(testdir: TestDir) -> None:
    testdir.makepyfile(
        """
        def test_pass(request):
            pass
    """
    )
    make_jobserver(testdir.tmpdir, "jobserver_fifo", 1)
    testdir.monkeypatch.setenv("PYTEST_JOBSERVER", "jobserver_fifo")

    result = testdir.runpytest("-v")

    result.stdout.fnmatch_lines(["*::test_pass PASSED*"])
    result.stdout.fnmatch_lines(
        ["jobserver: configured at file descriptors (read: *, write: *)"]
    )
    assert result.ret == 0


def test_jobserver_token_fixture(testdir: TestDir) -> None:
    testdir.makepyfile(
        f"""
        def test_value(jobserver_token: int):
            assert jobserver_token == 88
    """
    )
    make_jobserver(testdir.tmpdir, "jobserver_fifo", 1)
    testdir.monkeypatch.setenv("PYTEST_JOBSERVER", "jobserver_fifo")

    result = testdir.runpytest("-v")
    assert result.ret == 0


def test_xdist_makeflags_fails(testdir: TestDir) -> None:
    """Check we error if we try to load jobserver from env, but xdist is active"""
    testdir.makepyfile(
        """
        def test_pass(request):
            pass
    """
    )
    testdir.monkeypatch.setenv("MAKEFLAGS", "w -j --jobserver-fds=7,8")
    result = testdir.runpytest("-v", "-n2")
    assert result.ret == 4, "Expected pytest would fail to run with MAKEFLAGS and xdist"
    result.stderr.fnmatch_lines(
        ["ERROR: pytest-jobserver does not support using pytest-xdist with MAKEFLAGS"]
    )


def test_server_xdist(testdir: TestDir) -> None:
    testdir.makepyfile(
        """
        from time import sleep

        def pause():
            sleep(1)

        def test_0(request):
            pause()

        def test_1(request):
            pause()

        def test_2(request):
            pause()

        def test_3(request):
            pause()

        def test_4(request):
            pause()

        def test_5(request):
            pause()
    """
    )

    make_jobserver(testdir.tmpdir, "jobserver_fifo_1", 1)
    make_jobserver(testdir.tmpdir, "jobserver_fifo_3", 3)
    xdist_parallelism = "-n3"

    start = time.time()
    result = testdir.runpytest(
        "-v", "--jobserver", "jobserver_fifo_3", xdist_parallelism
    )
    end = time.time()
    duration_3 = end - start
    assert result.ret == 0

    start = time.time()
    result = testdir.runpytest(
        "-v", "--jobserver", "jobserver_fifo_1", xdist_parallelism
    )
    end = time.time()
    duration_1 = end - start
    assert result.ret == 0

    assert duration_3 < (
        duration_1 / 2.0
    ), "Expected xdist to run at least 2x faster with 3x tokens"


def test_server_not_found(testdir: TestDir) -> None:
    testdir.makepyfile(
        """
        def test_pass(request):
            pass
    """
    )
    # Run our test
    result = testdir.runpytest("-v", "--jobserver", "non_existent_file")

    result.stderr.fnmatch_lines(["ERROR: jobserver doesn't exist: non_existent_file"])
    assert result.ret == 4


def test_server_not_fifo(testdir: TestDir) -> None:
    testdir.makefile(".txt", jobserver="X")
    testdir.makepyfile(
        """
        def test_pass(request):
            pass
    """
    )
    # Run our test
    result = testdir.runpytest("-v", "--jobserver", "jobserver.txt")

    result.stderr.fnmatch_lines(["ERROR: jobserver is not a fifo: jobserver.txt"])
    assert result.ret == 4
