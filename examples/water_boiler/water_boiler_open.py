import utime
from machine import Timer


class WaterBoiler:
    """
    Simple simulation of a water boiler which can heat up water
    and where the heat dissipates slowly over time
    """

    def __init__(self, dissipation=0.2):
        self.water_temp = 20
        self.ambient = 20
        self.dissipation = dissipation
        self._last_time = utime.ticks_ms()

    def update(self, boiler_power):
    	now = utime.ticks_ms()
    	dt = utime.ticks_diff(now,self._last_time) if (utime.ticks_diff(now,self._last_time)) else 1e-16
        if boiler_power > 0:
        	# Boiler can only produce heat, not cold
        	self.water_temp += 1 * boiler_power * dt / 1000

        # Some heat dissipation
        self.water_temp -= (self.water_temp - self.ambient) * self.dissipation * dt

        self._last_time = now
        return self.water_temp

boiler = WaterBoiler(0.001)
water_temp = boiler.water_temp
step = 40

#Timer Function Callback
def timerFunc0(t):
    global water_temp
    # step of 20
    water_temp = boiler.update(step)

def timerFunc1(t):
    global water_temp
    print(boiler._last_time,",",water_temp)

def timerFunc2(t):
    tim0.deinit()
    tim1.deinit()


tim0=Timer(0)
tim0.init(period=100, mode=Timer.PERIODIC, callback=timerFunc0)
tim1=Timer(1)
tim1.init(period=200, mode=Timer.PERIODIC, callback=timerFunc1)
tim2=Timer(2)
tim2.init(period=10000, mode=Timer.ONE_SHOT, callback=timerFunc2)

