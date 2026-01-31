# pytest-jobserver

[![PyPI version](https://img.shields.io/pypi/v/pytest-jobserver.svg)](https://pypi.org/project/pytest-jobserver)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-jobserver.svg)](https://pypi.org/project/pytest-jobserver)
[![Code coverage](https://codecov.io/gh/tommilligan/pytest-jobserver/branch/master/graph/badge.svg)](https://codecov.io/gh/tommilligan/pytest-jobserver/branch/master)
[![Build status](https://img.shields.io/circleci/project/github/tommilligan/pytest-jobserver/master.svg)](https://circleci.com/gh/tommilligan/pytest-jobserver)

Limit parallel tests with posix jobserver.

## Installation

Install with pip:

```bash
pip install pytest-jobserver
```

The plugin officially supports Python `>= 3.6` on a Linux OS.
You may find other Python 3 versions/MacOS work as well.

## Usage

The plugin uses a [POSIX jobserver](https://www.gnu.org/software/make/manual/html_node/POSIX-Jobserver.html) to manage parallel test loading.

Pass the `--jobserver` argument with a path, where this path points to a named pipe acting as a jobserver.
You should probably also use `pytest-xdist` to enable parallelism in the first place:

```bash
pytest -n4 --jobserver /opt/jobserver
```

You can also pass this filepath via the `PYTEST_JOBSERVER` environment variable.

### `make`

The plugin can also listen for an existing jobserver as created by `make`.
If a jobserver is not configured by filepath, `pytest-jobserver` will check the following environment variables in order:

- `CARGO_MAKEFLAGS`
- `MAKEFLAGS`
- `MFLAGS`

**Please note:** it is not possible to use one of these environment variables with `pytest-xdist`. The `execnet` protocol used by `xdist` does not support passing file descriptors to remote child processes.

## Implementation

This plugin [wraps pytest's call to `pytest_runtest_protocol`](https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_protocol), which is called to actually run a collected item on the worker node.

## Development

See the top level `Makefile` and `.circleci/config.yml` for the development flow. But in essence:

- `make dev` to install deps
- `make lint` to lint code (will change files)
- `make test` to run lint/unit tests
- `make integrate` to run integration tests

### Release

Maintainers can cut a new release by pushing a `vX.Y.Z` tag to the repo.
