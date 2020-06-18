#!/usr/bin/env python

import time
import matplotlib.pyplot as plt
from simple_pid import PID
import random

class WaterBoiler:
    """
    Simple simulation of a water boiler which can heat up water
    and where the heat dissipates slowly over time
    """

    def __init__(self):
        self.water_temp = 20

    def update(self, boiler_power, dt):
        if boiler_power > 0:
            # boiler can only produce heat, not cold
            self.water_temp += 1 * boiler_power * dt

        # some heat dissipation
        self.water_temp -= 0.02 * dt
        return self.water_temp

class CrazyBoiler:
    """
    it randoms me CRAZY
    """

    def __init__(self):
        self.water_temp = 20

    def update(self, boiler_power, dt):
        if boiler_power > 0:
            # boiler can only produce heat, not cold
            self.water_temp += 1 * boiler_power * dt

        # some heat dissipation
        self.water_temp -= self.water_temp * dt * random.random()
        return self.water_temp


if __name__ == '__main__':
    boiler = WaterBoiler()
    # boiler = CrazyBoiler()
    water_temp = boiler.water_temp

    pid = PID(5, 0.01, 0.1, setpoint=water_temp)
    # pid = PID(20, 0.9, 1.9, setpoint=water_temp)
    pid.output_limits = (0, 100)

    start_time = time.time()
    last_time = start_time

    # keep track of values for plotting
    setpoint, y, x = [], [], []

    while time.time() - start_time < 10:
        current_time = time.time()
        dt = current_time - last_time

        power = pid(water_temp)
        water_temp = boiler.update(power, dt)

        x += [round(current_time - start_time, 3)]
        y += [round(water_temp, 2)]
        setpoint += [pid.setpoint]

        if current_time - start_time > 1:
            pid.setpoint = 100

        last_time = current_time
        time.sleep(0.1)
        # time.sleep(0.01)

    # print(f"{list(zip(x, y))}")
    print(y)
    plt.plot(x, y, label='measured')
    plt.plot(x, setpoint, label='target')
    plt.xlabel('time')
    plt.ylabel('temperature')
    plt.legend()
    plt.show()
