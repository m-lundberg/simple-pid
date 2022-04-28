import sys
import time
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

    assert round(pid(0)) == 10.0  # Make sure we are close to expected value
    time.sleep(0.1)

    assert round(pid(0)) == 20.0


def test_I_negative_setpoint():
    pid = PID(0, 10, 0, setpoint=-10, sample_time=0.1)
    time.sleep(0.1)

    assert round(pid(0)) == -10.0
    time.sleep(0.1)

    assert round(pid(0)) == -20.0


def test_D():
    pid = PID(0, 0, 0.1, setpoint=10, sample_time=0.1)

    # Should not compute derivative when there is no previous input (don't assume 0 as first input)
    assert pid(0) == 0
    time.sleep(0.1)

    # Derivative is 0 when input is the same
    assert pid(0) == 0
    assert pid(0) == 0
    time.sleep(0.1)

    assert round(pid(5)) == -5
    time.sleep(0.1)
    assert round(pid(15)) == -10


def test_D_negative_setpoint():
    pid = PID(0, 0, 0.1, setpoint=-10, sample_time=0.1)
    time.sleep(0.1)

    # Should not compute derivative when there is no previous input (don't assume 0 as first input)
    assert pid(0) == 0
    time.sleep(0.1)

    # Derivative is 0 when input is the same
    assert pid(0) == 0
    assert pid(0) == 0
    time.sleep(0.1)

    assert round(pid(5)) == -5
    time.sleep(0.1)
    assert round(pid(-5)) == 10
    time.sleep(0.1)
    assert round(pid(-15)) == 10


def test_desired_state():
    pid = PID(10, 5, 2, setpoint=10, sample_time=None)

    # Should not make any adjustment when setpoint is achieved
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

    # Last value should be returned again
    assert pid(100) == control


def test_monotonic():
    from simple_pid.pid import _current_time

    if sys.version_info < (3, 3):
        assert _current_time == time.time
    else:
        assert _current_time == time.monotonic


def test_auto_mode():
    pid = PID(1, 0, 0, setpoint=10, sample_time=None)

    # Ensure updates happen by default
    assert pid(0) == 10
    assert pid(5) == 5

    # Ensure no new updates happen when auto mode is off
    pid.auto_mode = False
    assert pid(1) == 5
    assert pid(7) == 5

    # Should reset when reactivating
    pid.auto_mode = True
    assert pid._last_input is None
    assert pid._integral == 0
    assert pid(8) == 2

    # Last update time should be reset to avoid huge dt
    from simple_pid.pid import _current_time

    pid.auto_mode = False
    time.sleep(1)
    pid.auto_mode = True
    assert _current_time() - pid._last_time < 0.01

    # Check that setting last_output works
    pid.auto_mode = False
    pid.set_auto_mode(True, last_output=10)
    assert pid._integral == 10


def test_separate_components():
    pid = PID(1, 0, 1, setpoint=10, sample_time=0.1)

    assert pid(0) == 10
    assert pid.components == (10, 0, 0)
    time.sleep(0.1)

    assert round(pid(5)) == -45
    assert tuple(round(term) for term in pid.components) == (5, 0, -50)


def test_clamp():
    from simple_pid.pid import _clamp

    assert _clamp(None, (None, None)) is None
    assert _clamp(None, (-10, 10)) is None

    # No limits
    assert _clamp(0, (None, None)) == 0
    assert _clamp(100, (None, None)) == 100
    assert _clamp(-100, (None, None)) == -100

    # Only lower limit
    assert _clamp(0, (0, None)) == 0
    assert _clamp(100, (0, None)) == 100
    assert _clamp(-100, (0, None)) == 0

    # Only upper limit
    assert _clamp(0, (None, 0)) == 0
    assert _clamp(100, (None, 0)) == 0
    assert _clamp(-100, (None, 0)) == -100

    # Both limits
    assert _clamp(0, (-10, 10)) == 0
    assert _clamp(-10, (-10, 10)) == -10
    assert _clamp(10, (-10, 10)) == 10
    assert _clamp(-100, (-10, 10)) == -10
    assert _clamp(100, (-10, 10)) == 10


def test_repr():
    pid = PID(1, 2, 3, setpoint=10)
    new_pid = eval(repr(pid))

    assert new_pid.Kp == 1
    assert new_pid.Ki == 2
    assert new_pid.Kd == 3
    assert new_pid.setpoint == 10


def test_converge_system():
    pid = PID(1, 0.8, 0.04, setpoint=5, output_limits=(-5, 5))
    pv = 0  # Process variable

    def update_system(c, dt):
        # Calculate a simple system model
        return pv + c * dt - 1 * dt

    start_time = time.time()
    last_time = start_time

    while time.time() - start_time < 120:
        c = pid(pv)
        pv = update_system(c, time.time() - last_time)

        last_time = time.time()

    # Check if system has converged
    assert abs(pv - 5) < 0.1


def test_error_map():
    import math

    def pi_clip(angle):
        """Transform the angle value to a [-pi, pi) range."""
        if angle > 0:
            if angle > math.pi:
                return angle - 2 * math.pi
        else:
            if angle < -math.pi:
                return angle + 2 * math.pi
        return angle

    sp = 0.0  # Setpoint
    pv = 5.0  # Process variable
    pid = PID(1, 0, 0, setpoint=0.0, sample_time=0.1, error_map=pi_clip)

    # Check if error value is mapped by the function
    assert pid(pv) == pi_clip(sp - pv)
