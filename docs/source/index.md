
(welcome)=
# simple-pid

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

Keep reading in the {ref}`user_guide`.


```{toctree}
---
maxdepth: 2
hidden:
caption: Contents
---
self
user_guide
reference
```

```{toctree}
---
hidden:
caption: Project links
---
GitHub <https://github.com/m-lundberg/simple-pid>
PyPI <https://pypi.org/project/simple-pid/>
```
