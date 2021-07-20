import utime
from PID import PID
from machine import Timer


class WaterBoiler:
    """
    Simple simulation of a water boiler which can heat up water
    and where the heat dissipates slowly over time
    """

    def __init__(self):
        self.water_temp = 20

    def update(self, boiler_power, dt):
        if boiler_power > 0:
        	# Boiler can only produce heat, not cold
        	self.water_temp += 1 * boiler_power * dt / 1000  # just to convert from miliseconds to seconds

        # Some heat dissipation
        self.water_temp -= 0.2 * dt
        return self.water_temp

interval1 = 100
boiler = WaterBoiler()
water_temp = boiler.water_temp
pid = PID(1, 0, 0, setpoint=20, sample_time=interval1, scale='ms')
pid.output_limits = (0, 100)

#Timer Function Callback
def timerFunc0(t):
    global power
    global water_temp
    power = pid(water_temp)
    water_temp = boiler.update(power, interval1)
    print(pid._last_time,",",water_temp,",",pid.setpoint,",",power)

#Timer Function Callback
def timerFunc1(t):
    global pid
    pid.setpoint = 100


tim0=Timer(0)
tim0.init(period=100, mode=Timer.PERIODIC, callback=timerFunc0)
tim1=Timer(1)
tim1.init(period=5000, mode=Timer.PERIODIC, callback=timerFunc1)

