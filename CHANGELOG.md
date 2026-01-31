# Changelog

## v1.1.0

This feature release fixes several minor issues, and increases support for
jobserver implementations.

Thanks to [mgorny](https://github.com/mgorny) for driving these changes!

### Added

- Support for fifo-based jobservers via MAKEFLAGS (https://github.com/tommilligan/pytest-jobserver/pull/147)
- Obtain job tokens for test collection too (https://github.com/tommilligan/pytest-jobserver/pull/150)

### Fixed

- No longer require files to be fifo (https://github.com/tommilligan/pytest-jobserver/pull/149)
- Do not acquire a job token for gw0 worker (https://github.com/tommilligan/pytest-jobserver/pull/154)

## 1.0.0

### Added

- jobserver token `int` value can be accessed within a test using the `jobserver_token` fixture
- bump to `1.0.0` as the plugin is now stable, and in use by other projects

## 0.3.1

### Fixed

- fix package installation with pip

## 0.3.0

### Added

- a jobserver filepath can also be configured by the `PYTEST_JOBSERVER` environment variable

## 0.2.2

### Fixed

- move jobserver status on startup to official `pytest_report_header` hook

## 0.2.1

### Fixed

- remove `pytest-xdist` from runtime dependencies

## 0.2.0

### Added

- can run against a jobserver specified with `make` environment variables
  - note that this will deliberately not work when also using `pytest-xdist`

## 0.1.1

### Fixed

- fix setup.py package metadata

## 0.1.0

### Added

- can run against a jobserver specified at the cli

