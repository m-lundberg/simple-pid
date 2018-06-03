
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
    

def test_control():
    pid = PID(2, 1, 1, setpoint=10)
    PV = 0
    
    def update_system(C, dt):
        return PV + C*dt - 1*dt

    start_time = time.time()
    last_time = start_time

    while time.time() - start_time < 10:
        C = pid(PV)
        PV = update_system(C, time.time()-last_time)

        last_time = time.time()

    # check if system has converged
    assert abs(PV - 10) < 0.1
