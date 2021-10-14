import utime
import math
from control import PID
from machine import Timer

class DCMotor:

    def __init__ (
    	self,
    	Ra=0.52,
    	La=0.000036,
    	B=0.00001,
    	J=0.000012,
    	Kbemf=0.0137,
    	STATIC_FRICTION=0.01,
    	FRICTION_S=0.01
    ):
        self.bemf = 0.0
        # omega = rpm ( w )
        self.omega = 0.0

        # theta = electrical angle normalized to 2*pi
        self.theta = 0.0

        self.ia, self.va = 0.0, 0.0

        self.Pelec, self.Te, self.Tl = 0.0, 0.0, 0.0

        # La here is La subtracted by mutual inductance M.
        self.Ra, self.La, self.B, self.J = Ra, La, B, J
        self.Kbemf = Kbemf
        self.STATIC_FRICTION, self.FRICTION_S = STATIC_FRICTION, FRICTION_S

        self._last_time = 0.0


    # The simulator
    def sim( self, load, va, dt):
        now = utime.ticks_us()

        # Set the load
        sign = math.copysign( 1, self.omega )
        self.Tl = sign * load
        self.va = va

        # Calculate bemf
        self.bemf = self.Kbemf * self.omega

        # Calculate change in current per di/dt
        dot_ia = (1.0 / self.La) * ( self.va - (self.Ra * self.ia) - self.bemf )

        # Apply changes to current in phases
        self.ia += dot_ia * dt

        # Electrical torque. Since omega can be null, cannot derive from P/w
        self.Te = self.Kbemf * self.ia

        # Electrical power
        self.Pelec = self.bemf * self.ia


        # Mechanical torque.
        # mtorque = ((etorque * (p->m->NbPoles / 2)) - (p->m->damping * sv->omega) - p->pv->torque);
        self.Tm = ((self.Te) - (sign * self.B * abs(self.omega)) - self.Tl)

        # Friction calculations
        if abs(self.omega) < 1.0:
            if abs(self.Te) < self.STATIC_FRICTION:
                self.Tm = 0.0
            else:
                self.Tm -= self.STATIC_FRICTION
        else:
           self.Tm = self.Tm - sign * ( self.STATIC_FRICTION * math.exp( -5 * abs( self.omega )) + self.FRICTION_S )

        # J is the moment of inertia
        dotOmega = (self.Tm / self.J)
        self.omega = self.omega + dotOmega * dt


        self.theta += self.omega * dt
        self.theta = self.theta % ( 2.0 * math.pi )

        self._last_time += dt
        return self.omega

    def variables( self ):
        ret = {}
        ret[ "va" ] = self.va
        ret[ "ia" ] = self.ia
        ret[ "omega" ] = self.omega
        ret[ "theta" ] = self.theta
        ret[ "bemf" ] = self.bemf
        ret[ "torque" ] = self.Te
        ret[ "loadtorque" ] = self.Tl
        return ret


dcmotor = DCMotor()
omega = dcmotor.omega
load = 0.3
step = 230
# how much time do you spend simulating
sim_time=10
#how much elapsed simulated time do you want to keep
print_interval=500e-6
power = 0
last_time=0

pid = PID(1.0634, 0.0082041, 0, setpoint=step)

deadline4 = utime.ticks_add(utime.time(), sim_time)
while utime.ticks_diff(deadline4, utime.time()) > 0:
    omega = dcmotor.sim(load, power, 32e-6)
    power = pid(omega, 32e-6)
    if ((dcmotor._last_time - last_time) > print_interval):
    	print(dcmotor._last_time,

timestep = 1e-7
voltage = 0
omega = 0
last_time = 0
pid0 = PID(33, 113675, 0.002322, setpoint=30)
# Compute until 0.001 seconds (not realtime).
while (dcmotor0._last_time) < 0.001:
  omega = dcmotor0.sim(0.3,voltage,timestep)
  voltage = pid0(omega,timestep)
  # Print every 50 time steps.
  if (dcmotor0._last_time) - last_time > 50 * timestep:
    print(''.join([str(x) for x in [dcmotor0._last_time, ',', pid0.setpoint, ',', voltage, ',', omega]]))
    last_time = dcmotor0._last_time
