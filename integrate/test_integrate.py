import math
import os
import subprocess
import tempfile
import time
from typing import Iterable, List, Sequence

import pytest

from pytest_jobserver.test.jobserver import make_jobserver


def jobserver_path(name, tokens):
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield make_jobserver(tmpdirname, name, tokens)


@pytest.fixture(scope="function")
def jobserver_path_1():
    yield from jobserver_path("jobserver_1", 1)


@pytest.fixture(scope="function")
def jobserver_path_4():
    yield from jobserver_path("jobserver_4", 4)


def time_subprocesses(name: str, subprocesses_args: Iterable[Sequence[str]]) -> float:
    """Time several suprocesses running in parallel.

    If `check` is set, expect the given exit code (default 0).
    """
    print()
    print("> Running: {}".format(name))
    start = time.time()
    subprocesses = []
    for subprocess_args in subprocesses_args:
        subprocesses.append(subprocess.Popen(subprocess_args))
    for subprocess_ in subprocesses:
        retcode = subprocess_.wait()
        assert retcode == 0
    end = time.time()
    duration = end - start
    print("> Completed: {}, duration: {}".format(name, duration))
    print()
    return duration


# Named pipe tests - jobserver spawned manually by us. pytest-xdist compatible


def pytest_xdist_jobserver_args(path: str) -> List[str]:
    return ["pytest", "-s", "-n4", "--jobserver", path, "test_long.py"]


def test_xdist_single(jobserver_path_1, jobserver_path_4):
    """More tokens should run tests in parallel in a file"""

    time_single_1 = time_subprocesses(
        "Single (1 tokens)", [pytest_xdist_jobserver_args(jobserver_path_1)]
    )
    time_single_4 = time_subprocesses(
        "Single (4 tokens)", [pytest_xdist_jobserver_args(jobserver_path_4)]
    )
    assert (
        time_single_4 < 4.0 < time_single_1
    ), "Expected xdist to run test cases in parallel with multiple tokens"


def test_xdist_double(jobserver_path_1, jobserver_path_4):
    """More tokens should run tests in parallel across master nodes"""

    time_double_1_tokens = time_subprocesses(
        "Double (1 tokens)",
        [
            pytest_xdist_jobserver_args(jobserver_path_1),
            pytest_xdist_jobserver_args(jobserver_path_1),
        ],
    )
    time_double_4_tokens = time_subprocesses(
        "Double (4 tokens)",
        [
            pytest_xdist_jobserver_args(jobserver_path_4),
            pytest_xdist_jobserver_args(jobserver_path_4),
        ],
    )
    assert (
        time_double_4_tokens < 8.0 < time_double_1_tokens
    ), "Expected xdist to run test master nodes in parallel with multiple tokens"
    assert time_double_4_tokens < (
        time_double_1_tokens / 2.0
    ), "Expected xdist to run at least 2x faster with 4x tokens"


def test_xdist_oserror(jobserver_path_1):
    """Test suite should fail if the jobserver is removed"""

    subprocess_ = subprocess.Popen(
        pytest_xdist_jobserver_args(jobserver_path_1),
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    time.sleep(0.5)
    os.remove(jobserver_path_1)
    retcode = subprocess_.wait()
    stdout, stderr = subprocess_.communicate()
    print(stdout)
    print(stderr)
    assert retcode == 1


# Makefile tests - jobserver spawned automatically by make. Plain pytest only.


def test_make():
    # Single test master
    # Sequential
    time_single = time_subprocesses("Single", [["make", "test"]])

    # Two test masters, linked by the jobserver
    # Sequential
    time_double = time_subprocesses("Double", [["make", "test2"]])
    # Parallel, limited by tokens
    time_double_1_tokens = time_subprocesses(
        "Double (1 tokens)", [["make", "test2", "-j", "1"]]
    )
    # Parallel, unlimited by tokens
    # TODO: not sure why we need 4 tokens here. make tasks themselves taking tokens?
    time_double_4_tokens = time_subprocesses(
        "Double (4 tokens)", [["make", "test2", "-j", "4"]]
    )

    assert (
        time_double_4_tokens < time_double
    ), "Expected double test run in parallel to be faster"
    assert (
        time_double_4_tokens < time_double_1_tokens
    ), "Expected double test run with more tokens to be faster"
    assert (
        time_single < time_double_1_tokens
    ), "Expected single test to be faster than token-limited double run"
    assert (
        math.fabs(time_single - time_double_4_tokens) < 1.0
    ), "Expected single test to be about the same as token-unlimited double run"
