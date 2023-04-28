
(user_guide)=
# User guide

## Installation

To install, run:

```shell
python -m pip install simple-pid
```


## The basics

We already saw a minimal example in {ref}`welcome`:

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

This shows the basic structure of a PID loop. You construct a PID object and then in each loop iteration you feed it the current value of whatever system you want to control. The PID takes the error from the setpoint you want to achieve and outputs the value to feed back into the controlled system.

The `PID` class implements `__call__()`, which means that to compute a new output value, you simply call the object like this:

```python
output = pid(current_value)
```

The PID works best when it is updated at regular intervals. To achieve this, set `sample_time` to the amount of time there should be between each update and then call the PID every time in the program loop. A new output will only be calculated when `sample_time` seconds has passed:

```python
pid.sample_time = 0.01  # Update every 0.01 seconds

while True:
    output = pid(current_value)
```

To set the setpoint, ie. the value that the PID is trying to achieve, simply set it like this:

```python
pid.setpoint = 10
```

The tunings can be changed any time when the PID is running. They can either be set individually or all at once:

```python
pid.Ki = 1.0
pid.tunings = (1.0, 0.2, 0.4)
```

In order to get output values in a certain range, and also to avoid [integral windup](https://en.wikipedia.org/wiki/Integral_windup) (since the integral term will never be allowed to grow outside of these limits), the output can be limited to a range:

```python
pid.output_limits = (0, 10)    # Output value will be between 0 and 10
pid.output_limits = (0, None)  # Output will always be above 0, but with no upper bound
```


### Reverse mode

To use the PID in [reverse mode](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-direction/), meaning that an increase in the input leads to a decrease in the output (like when cooling for example), you can set the tunings to negative values:

```python
pid.tunings = (-1.0, -0.1, 0)
```

Note that all the tunings should have the same sign.


## Other features

### Auto mode

To disable the PID so that no new values are computed, set auto mode to `False`:

```python
pid.auto_mode = False  # No new values will be computed when pid is called
pid.auto_mode = True   # pid is enabled again
```

When disabling the PID and controlling a system manually, it might be useful to tell the PID controller where to start from when giving back control to it. This can be done by enabling auto mode like this:

```python
pid.set_auto_mode(True, last_output=8.0)
```

This will set the I-term to the value given to `last_output`, meaning that if the system that is being controlled was stable at that output value the PID will keep the system stable if started from that point, without any big bumps in the output when turning the PID back on.


### Observing separate components

When tuning the PID, it can be useful to see how each of the components contribute to the output. They can be seen like this:

```python
p, i, d = pid.components  # The separate terms are now in p, i, d
```


### Proportional on measurement

To eliminate overshoot in certain types of systems, you can calculate the [proportional term directly on the measurement](http://brettbeauregard.com/blog/2017/06/introducing-proportional-on-measurement/) instead of the error. This can be enabled like this:

```python
pid.proportional_on_measurement = True
```


### Differential on measurement

By default the [differential term is calculated on the measurement](http://brettbeauregard.com/blog/2011/04/improving-the-beginner%e2%80%99s-pid-derivative-kick/) instead of the error. This can be disabled like this:

```python
pid.differential_on_measurement = False
```


### Error mapping

To transform the error value to another domain before doing any computations on it, you can supply an `error_map` callback function to the PID. The callback function should take one argument which is the error from the setpoint. This can be used e.g. to get a degree value error in a yaw angle control with values between `[-pi, pi)`:

```python
import math

def pi_clip(angle):
    if angle > 0:
        if angle > math.pi:
            return angle - 2*math.pi
    else:
        if angle < -math.pi:
            return angle + 2*math.pi
    return angle

pid.error_map = pi_clip
```


### Overriding time function

By default, the PID uses `time.monotonic()` (or if not available, `time.time()` as fallback) to get the current time on each invocation. The time function can be overridden by setting `PID.time_fn` to whichever function you want to use. For example, to use the [MicroPython `time.ticks_us()`](https://docs.micropython.org/en/latest/library/time.html#time.ticks_us):

```python
import time
pid.time_fn = time.ticks_us
```
