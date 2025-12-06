from typing import Any, Optional

import pytest

from pytest_jobserver.system import environ_get_first, is_rw_ok

from .jobserver import make_jobserver

TestDir = Any


@pytest.mark.parametrize(
    "env_a,env_b,env_expected",
    [("x", "y", "x"), ("x", None, "x"), (None, "y", "y"), (None, None, None)],
)
def test_environ_get_first(
    testdir: TestDir, env_a: str, env_b: str, env_expected: Optional[str]
) -> None:
    def setenv_if_not_none(key: str, value: Optional[str]) -> None:
        if value is not None:
            testdir.monkeypatch.setenv(key, value)

    setenv_if_not_none("A", env_a)
    setenv_if_not_none("B", env_b)
    assert environ_get_first(("A", "B")) == env_expected


def test_is_rw_ok(testdir: TestDir) -> None:
    fifo_path = make_jobserver(testdir.tmpdir, "jobserver_fifo", 0)
    assert is_rw_ok(fifo_path) is True

    assert is_rw_ok("/") is False
