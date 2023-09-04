# simple-pid

[![Tests](https://github.com/m-lundberg/simple-pid/actions/workflows/run-tests.yml/badge.svg)](https://github.com/m-lundberg/simple-pid/actions?query=workflow%3Atests)
[![PyPI](https://img.shields.io/pypi/v/simple-pid.svg)](https://pypi.org/project/simple-pid/)
[![Read the Docs](https://img.shields.io/readthedocs/simple-pid.svg)](https://simple-pid.readthedocs.io/)
[![License](https://img.shields.io/github/license/m-lundberg/simple-pid.svg)](https://github.com/m-lundberg/simple-pid/blob/master/LICENSE.md)
[![Downloads](https://static.pepy.tech/badge/simple-pid/month)](https://pepy.tech/project/simple-pid)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A simple and easy to use PID controller in Python. If you want a PID controller without external dependencies that just works, this is for you! The PID was designed to be robust with help from [Brett Beauregards guide](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/).

Usage is very simple:

```python
from simple_pid import PID
pid = PID(1, 0.1, 0.05, setpoint=1)

# Assume we have a system we want to control in controlled_system
v = controlled_system.update(0)

while True:
    # Compute new output from the PID according to the systems current value
    control = pid(v)
    
    # Feed the PID output to the system and get its current value
    v = controlled_system.update(control)
```


## Installation
To install, run:

```
python -m pip install simple-pid
```


## Documentation
Documentation, including a user guide and complete API reference, can be found [here](https://simple-pid.readthedocs.io/).


## Tests
This project has a test suite using [`pytest`](https://docs.pytest.org/). To run the tests, install `pytest` and run:

```
pytest -v
```


## License
Licensed under the [MIT License](https://github.com/m-lundberg/simple-pid/blob/master/LICENSE.md).
