import sys
import time
import pytest
from simple_pid import PID


def test_zero():
    pid = PID(1, 1, 1, setpoint=0)
    assert pid(0) == 0


def test_P():
    pid = PID(1, 0, 0, setpoint=10, sample_time=None)
    assert pid(0) == 10
    assert pid(5) == 5
    assert pid(-5) == 15


def test_P_negative_setpoint():
    pid = PID(1, 0, 0, setpoint=-10, sample_time=None)
    assert pid(0) == -10
    assert pid(5) == -15
    assert pid(-5) == -5
    assert pid(-15) == 5


def test_I():
    pid = PID(0, 10, 0, setpoint=10, sample_time=0.1)
    time.sleep(0.1)

    assert round(pid(0)) == 10.0  # make sure we are close to expected value
    time.sleep(0.1)
    
    assert round(pid(0)) == 20.0


def test_I_negative_setpoint():
    pid = PID(0, 10, 0, setpoint=-10, sample_time=0.1)
    time.sleep(0.1)

    assert round(pid(0)) == -10.0
    time.sleep(0.1)

    assert round(pid(0)) == -20.0


def test_D():
    pid = PID(0, 0, 1, setpoint=10, sample_time=None)

    # should not compute derivate when there is no previous input (don't assume 0 as first input)
    assert pid(0) == 0

    # derivate is 0 when input is the same
    assert pid(0) == 0
    assert pid(0) == 0

    assert pid(5) == -5
    assert pid(20) == -15


def test_D_negative_setpoint():
    pid = PID(0, 0, 1, setpoint=-10, sample_time=None)

    # should not compute derivate when there is no previous input (don't assume 0 as first input)
    assert pid(0) == 0

    # derivate is 0 when input is the same
    assert pid(0) == 0
    assert pid(0) == 0

    assert pid(5) == -5
    assert pid(-5) == 10
    assert pid(-30) == 25


def test_desired_state():
    pid = PID(10, 5, 2, setpoint=10, sample_time=None)

    # should not make any adjustment when setpoint is achieved
    assert pid(10) == 0


def test_output_limits():
    pid = PID(100, 20, 40, setpoint=10, output_limits=(0, 100), sample_time=None)
    time.sleep(0.1)

    assert 0 <= pid(0) <= 100
    time.sleep(0.1)

    assert 0 <= pid(-100) <= 100


def test_sample_time():
    pid = PID(setpoint=10, sample_time=10)

    control = pid(0)

    # last value should be returned again
    assert pid(100) == control


def test_monotonic():
    from simple_pid.PID import _current_time
    
    if sys.version_info < (3, 3):
        assert _current_time == time.time
    else:
        assert _current_time == time.monotonic


def test_clamp():
    from simple_pid.PID import _clamp

    assert _clamp(None, (None, None)) == None
    assert _clamp(None, (-10, 10)) == None

    # no limits
    assert _clamp(0, (None, None)) == 0
    assert _clamp(100, (None, None)) == 100
    assert _clamp(-100, (None, None)) == -100

    # only lower limit
    assert _clamp(0, (0, None)) == 0
    assert _clamp(100, (0, None)) == 100
    assert _clamp(-100, (0, None)) == 0

    # only upper limit
    assert _clamp(0, (None, 0)) == 0
    assert _clamp(100, (None, 0)) == 0
    assert _clamp(-100, (None, 0)) == -100

    # both limits
    assert _clamp(0, (-10, 10)) == 0
    assert _clamp(-10, (-10, 10)) == -10
    assert _clamp(10, (-10, 10)) == 10
    assert _clamp(-100, (-10, 10)) == -10
    assert _clamp(100, (-10, 10)) == 10


def test_converge_system():
    pid = PID(1, 0.8, 4, setpoint=5, output_limits=(-5, 5))
    PV = 0  # process variable
    
    def update_system(C, dt):
        # calculate a simple system model
        return PV + C*dt - 1*dt

    start_time = time.time()
    last_time = start_time

    while time.time() - start_time < 120:
        C = pid(PV)
        PV = update_system(C, time.time()-last_time)

        last_time = time.time()

    # check if system has converged
    assert abs(PV - 5) < 0.1
