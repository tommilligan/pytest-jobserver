from typing import Any

from pytest_jobserver.filesystem import is_fifo, is_rw_ok

from .jobserver import make_jobserver

TestDir = Any


def test_is_fifo(testdir: TestDir) -> None:
    fifo_path = make_jobserver(testdir.tmpdir, "jobserver_fifo", 0)
    assert is_fifo(fifo_path) is True

    not_fifo_path = testdir.makefile(".txt", jobserver="X")
    assert is_fifo(not_fifo_path) is False


def test_is_rw_ok(testdir: TestDir) -> None:
    fifo_path = make_jobserver(testdir.tmpdir, "jobserver_fifo", 0)
    assert is_rw_ok(fifo_path) is True

    assert is_rw_ok("/") is False
