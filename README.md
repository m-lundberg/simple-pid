# simple-pid

A simple and easy to use PID controller in Python. If you want a PID controller without external dependencies that just works, this is for you! The PID was designed to be robust with help from [Brett Beauregards guide](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/).

Usage is very simple:

```python
from simple_pid import PID
pid = PID(1, 0.1, 0.05, setpoint=1)

# assume we have a system we want to control in controlled_system
v = controlled_system.update(0)

while True:
    # compute new ouput from the PID according to the systems current value
    control = pid(v)
    
    # feed the PID output to the system and get its current value
    v = controlled_system.update(control)
```

Complete API documentation can be found [here](https://simple-pid.readthedocs.io/en/latest/simple_pid.html#module-simple_pid.PID).

## Installation
To install, run:
```
pip install simple-pid
```

## License
Licensed under the [MIT License](https://github.com/m-lundberg/simple-pid/blob/master/LICENSE.md).
