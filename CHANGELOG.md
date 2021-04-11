# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [1.0.1] - 2021-04-11

### Fixed

- Added type information for public instance variables to typing stub

## [1.0.0] - 2021-03-20

### Added

- Function to map the error value to a different domain

- Typing information through a stub file so that users of the library can use e.g.
  [mypy](https://github.com/python/mypy) to type check their code

- This project now uses the [Black code style](https://github.com/psf/black)

- The PID class now has a `__repr__()` method, meaning that objects of this type can be printed
  directly for use during development
  
- MANIFEST.in file to ensure all necessary files are included in the source distribution

### Fixed

- Formatting errors in the documentation due to poorly formatted docstrings

## [0.2.4] - 2019-10-08

### Added

- Added optional argument to manually set dt (useful e.g. when running in a simulation)

## [0.2.3] - 2019-08-26

### Added

- A reset method to reset the internal state of the PID controller

## [0.2.2] - 2019-07-04

### Changed

- Don't limit the proportional term to the output bounds when using `proportional_on_measurement`

## [0.2.1] - 2019-03-01

### Fixed

- `ZeroDivisionError` on systems with limited precision time.

## [0.2.0] - 2019-02-26

### Added

- Allow the proportional term to be monitored properly through the components-property when
  _proportional on measurement_ is enabled.

### Fixed

- Bump in output when re-enabling _auto mode_ after running in _manual mode_.

## [0.1.5] - 2019-01-31

### Added

- The ability to see the contributions of the separate terms in the PID

### Fixed

- D term not being divided by delta time, leading to wrong output values

## [0.1.4] - 2018-10-03

### Fixed

- Use monotonic time to prevent errors that may be difficult to diagnose when the system time is
  modified. Thanks [@deniz195](https://github.com/m-lundberg/simple-pid/issues/1)

### Added

- Initial implementation

[Unreleased]: https://github.com/m-lundberg/simple-pid/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/m-lundberg/simple-pid/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/m-lundberg/simple-pid/compare/v0.2.4...v1.0.0
[0.2.4]: https://github.com/m-lundberg/simple-pid/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/m-lundberg/simple-pid/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/m-lundberg/simple-pid/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/m-lundberg/simple-pid/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/m-lundberg/simple-pid/compare/v0.1.5...v0.2.0
[0.1.5]: https://github.com/m-lundberg/simple-pid/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/m-lundberg/simple-pid/releases/tag/v0.1.4
