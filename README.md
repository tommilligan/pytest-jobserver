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

The plugin can also listen for an existing jobserver as created by another tool. Currently the environment variables it supports are:

- `CARGO_MAKEFLAGS`
- `MAKEFLAGS`
- `MFLAGS`

The environment variables will only be checked when the cli flag is not set.

**Please note:** it is not supported to use both make environment variables and use `xdist`. The `execnet` protocol used by `xdist` does not support passing file descriptors to remote child processes.

## Implementation

This plugin [wraps pytest's call to `pytest_runtest_protocol`](https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_protocol), which is called to actually run a collected item on the worker node.

## Development

See the top level `Makefile` and `.circleci/config.yml` for the development flow. But in essence:

- `make dev` to install deps
- `make lint` to lint code (will change files)
- `make test` to run lint/unit tests
- `make integrate` to run integration tests

## Changelog

### 0.2.2

#### Bugfixes

- move jobserver status on startup to official `pytest_report_header` hook

### 0.2.1

#### Bugfixes

- remove `pytest-xdist` from runtime dependencies

### 0.2.0

#### Features

- can run against a jobserver specified with `make` environment variables
  - note that this will deliberately not work when also using `pytest-xdist`

### 0.1.1

#### Bugfixes

- fix setup.py package metadata

### 0.1.0

#### Features

- can run against a jobserver specified at the cli

## TODO

- [x] run against cli jobserver
- [x] integrate with Make jobserver from environment variables
- [ ] factor out creation of jobservers to seperate python package
