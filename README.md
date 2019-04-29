# pytest-jobserver

[![PyPI version](https://img.shields.io/pypi/v/pytest-jobserver.svg)](https://pypi.org/project/pytest-jobserver)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-jobserver.svg)](https://pypi.org/project/pytest-jobserver)
[![Code coverage](https://codecov.io/gh/tommilligan/pytest-jobserver/branch/master/graph/badge.svg)](https://codecov.io/gh/tommilligan/pytest-jobserver/branch/master)
[![Build status](https://img.shields.io/circleci/project/github/tommilligan/pytest-jobserver/master.svg)](https://circleci.com/gh/tommilligan/pytest-jobserver)

Parellise tests with posix jobserver.

## Installation

Install with pip:

```bash
pip install pytest-jobserver
```

The plugin officially supports Python `>= 3.6` on a Linux OS.
You may find other Python 3 versions/MacOS work as well.

## Usage

The plugin uses a [POSIX jobserver](https://www.gnu.org/software/make/manual/html_node/POSIX-Jobserver.html) to manage parallel test loading.

Pass the `--jobserver` argument with a path, where this path points to a named pipe acting as a Jobserver.
You should probably also use `pytest-xdist` to enable parallelism in the first place:

```bash
pytest -n4 --jobserver /opt/jobserver
```

## Implementation

This plugin [wraps pytest's call to `pytest_runtest_protocol`](https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_protocol), which is called to actually run a collected item on the worker node.

## Changelog

### 0.1.0

#### Features

- can run against a jobserver specified at the cli

## TODO

- [x] run against cli jobserver
- [ ] integrate with Make jobserver from environment variables
- [ ] factor out creation of jobservers to seperate python package
