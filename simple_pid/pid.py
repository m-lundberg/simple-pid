import math


def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    elif (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value


class PID(object):
    """A simple PID controller."""

    def __init__(
        self,
        Kp=1.0,
        Ki=0.0,
        Kd=0.0,
        setpoint=0,
        sample_time=0.01,
        output_limits=(None, None),
        auto_mode=True,
        man_in=None,
        tracking_mode=False,
        Tt=None,
        proportional_on_measurement=False,
        differential_on_measurement=True,
        error_map=None,
        time_fn=None,
        starting_output=0.0,
    ):
        """
        Initialize a new PID controller.

        :param Kp: The value for the proportional gain Kp
        :param Ki: The value for the integral gain Ki
        :param Kd: The value for the derivative gain Kd
        :param setpoint: The initial setpoint that the PID will try to achieve
        :param sample_time: The time in seconds which the controller should wait before generating
            a new output value. The PID works best when it is constantly called (eg. during a
            loop), but with a sample time set so that the time difference between each update is
            (close to) constant. If set to None, the PID will compute a new output value every time
            it is called.
        :param output_limits: The initial output limits to use, given as an iterable with 2
            elements, for example: (lower, upper). The output will never go below the lower limit
            or above the upper limit. Either of the limits can also be set to None to have no limit
            in that direction. Setting output limits also avoids integral windup, since the
            integral term will never be allowed to grow outside of the limits.
        :param auto_mode: Whether the controller should be enabled (auto mode) or not (manual mode)
        :param man_in: Manual input. When not in auto mode, this value, clamped to the output
            limits, is returned as the output. If None, the last output is returned instead.
        :param tracking_mode: Whether the controller should track the value given as track_in_
            when calling it, which should be the output actually applied to the manipulated
            variable (MV). This is back-calculation anti-windup.
        :param Tt: The tracking time constant, in the same time unit as dt, or None when not
            set. Setting it to zero, a negative number or NaN raises ValueError. Tracking mode
            needs it set. Keep Tt above dt / 2: below that the tracking step is unstable
        :param proportional_on_measurement: Whether the proportional term should be calculated on
            the input directly rather than on the error (which is the traditional way). Using
            proportional-on-measurement avoids overshoot for some types of systems.
        :param differential_on_measurement: Whether the differential term should be calculated on
            the input directly rather than on the error (which is the traditional way).
        :param error_map: Function to transform the error value in another constrained value.
        :param time_fn: The function to use for getting the current time, or None to use the
            default. This should be a function taking no arguments and returning a number
            representing the current time. The default is to use time.monotonic() if available,
            otherwise time.time().
        :param starting_output: The starting point for the PID's output. If you start controlling
            a system that is already at the setpoint, you can set this to your best guess at what
            output the PID should give when first calling it to avoid the PID outputting zero and
            moving the system away from the setpoint.
        """
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.setpoint = setpoint
        self.sample_time = sample_time
        self.man_in = man_in
        self.Tt = Tt

        self._min_output, self._max_output = None, None
        self._auto_mode = auto_mode
        self._tracking_mode = tracking_mode
        self.proportional_on_measurement = proportional_on_measurement
        self.differential_on_measurement = differential_on_measurement
        self.error_map = error_map

        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._last_time = None
        self._last_output_clamped = None
        self._last_output_not_clamped = 0.0
        self._last_error = None
        self._last_input = None

        if time_fn is not None:
            # Use the user supplied time function
            self.time_fn = time_fn
        else:
            import time

            try:
                # Get monotonic time to ensure that time deltas are always positive
                self.time_fn = time.monotonic
            except AttributeError:
                # time.monotonic() not available (using python < 3.3), fallback to time.time()
                self.time_fn = time.time

        self.output_limits = output_limits
        self.reset()

        # Set initial state of the controller
        if tracking_mode:
            self._integral = starting_output
        else:
            self._integral = _clamp(starting_output, output_limits)

    def __call__(self, input_, dt=None, track_in_=None):
        """
        Update the PID controller.

        Call the PID controller with *input_* and calculate and return a control output if
        sample_time seconds has passed since the last update. If no new output is calculated,
        return the previous output instead (or None if no value has been calculated yet).

        The output is never NaN or infinite. A step that would give one - a NaN or infinite
        input, setpoint, track_in_, gain or dt, or terms that overflow - holds instead: it
        returns the previous output (None if there is none yet), changes no internal state,
        and sets `holding` to True. So a bad value is not kept in the integral, and the next
        good step carries on from the state before it. The same goes for a man_in that is
        not a number in manual mode.

        :param dt: If set, uses this value for timestep instead of real time. This can be used in
            simulations when simulation time is different from real time.
        :param track_in_: The output actually applied to the manipulated variable (MV), for
            example after the actuator, a selector or an override. Required in tracking mode,
            ignored otherwise.
        """
        if not self.auto_mode:
            if self.man_in is None:
                # No manual value given: keep returning the last output
                self._holding = False
                return self._last_output_clamped
            output_manual = _clamp(self.man_in, self.output_limits)
            if not math.isfinite(output_manual):
                self._holding = True
                return self._last_output_clamped
            self._holding = False
            self._last_output_clamped = output_manual
            return self._last_output_clamped

        now = self.time_fn()
        if dt is None:
            dt = now - self._last_time if (now - self._last_time) else 1e-16
        elif dt <= 0:
            raise ValueError('dt has negative value {}, must be positive'.format(dt))

        if (
            self.sample_time is not None
            and dt < self.sample_time
            and self._last_output_clamped is not None
        ):
            # Only update every sample_time seconds
            return self._last_output_clamped

        if self.tracking_mode and self.Tt is None:
            raise ValueError(
                'Tt is not set but tracking mode is active. It should be the '
                'tracking time constant, a positive time'
            )

        if self.tracking_mode and track_in_ is None:
            raise ValueError(
                'track_in_ has no value but tracking mode is active. It should be the '
                'output actually applied to the manipulated variable (MV)'
            )

        # Compute error terms
        error = self.setpoint - input_
        d_input = input_ - (self._last_input if (self._last_input is not None) else input_)
        d_error = error - (self._last_error if (self._last_error is not None) else error)

        if self.tracking_mode:
            e_track = track_in_ - self._last_output_not_clamped
        # Check if must map the error
        if self.error_map is not None:
            error = self.error_map(error)

        # The terms are worked out in locals and kept only if the output is a
        # number, so a bad value never gets into the state - see the hold below.

        # Compute the proportional term
        if not self.proportional_on_measurement:
            # Regular proportional-on-error, simply set the proportional term
            proportional = self.Kp * error
        else:
            # Add the proportional error on measurement to error_sum
            proportional = self._proportional - self.Kp * d_input

        # Compute integral and derivative terms
        #
        # Tracking is dI/dt = e_track / Tt, with Tt a time constant, taken as
        # one forward Euler step: the back-calculation of Astrom & Hagglund,
        # with ar = dt/Tt. At the limit it multiplies the integral's distance
        # from its resting point by (1 - dt/Tt). It swings past that point once
        # dt > Tt, and each swing is bigger than the last once dt >= 2*Tt. The
        # caller keeps Tt above dt / 2; should it not, the growing integral
        # overflows, and the hold below catches it before the output is NaN.
        if self.tracking_mode:
            integral = self._integral + self.Ki * error * dt + e_track * dt / self.Tt
        else:
            integral = self._integral + self.Ki * error * dt
            integral = _clamp(integral, self.output_limits)  # Avoid integral windup

        if self.differential_on_measurement:
            derivative = -self.Kd * d_input / dt
        else:
            derivative = self.Kd * d_error / dt

        # Compute final output
        output_auto = proportional + integral + derivative

        # Hold. A NaN or infinite term makes the sum NaN or infinite too, so
        # this one check covers them all. _clamp would pass a NaN straight
        # through: NaN compares False against both limits. Nothing is kept,
        # not even the time, so the next good step's dt and derivative run
        # from the last good step.
        if not math.isfinite(output_auto):
            self._holding = True
            return self._last_output_clamped
        self._holding = False

        output_auto_clamped = _clamp(output_auto, self.output_limits)

        # Keep track of state
        self._proportional = proportional
        self._integral = integral
        self._derivative = derivative
        self._last_output_clamped = output_auto_clamped
        self._last_output_not_clamped = output_auto
        self._last_input = input_
        self._last_error = error
        self._last_time = now

        return output_auto_clamped

    def __repr__(self):
        return (
            '{self.__class__.__name__}('
            'Kp={self.Kp!r}, Ki={self.Ki!r}, Kd={self.Kd!r}, '
            'setpoint={self.setpoint!r}, sample_time={self.sample_time!r}, '
            'output_limits={self.output_limits!r}, auto_mode={self.auto_mode!r}, '
            'tracking_mode={self.tracking_mode!r}, Tt={self.Tt!r}, '
            'proportional_on_measurement={self.proportional_on_measurement!r}, '
            'differential_on_measurement={self.differential_on_measurement!r}, '
            'error_map={self.error_map!r}'
            ')'
        ).format(self=self)

    @property
    def components(self):
        """
        The P-, I- and D-terms from the last computation as separate components as a tuple. Useful
        for visualizing what the controller is doing or when tuning hard-to-tune systems.
        """
        return self._proportional, self._integral, self._derivative

    @property
    def holding(self):
        """Whether the last call held its output because the step was not a number.

        See __call__. It goes back to False on the next call that gives a number.
        """
        return self._holding

    @property
    def tunings(self):
        """The tunings used by the controller as a tuple: (Kp, Ki, Kd)."""
        return self.Kp, self.Ki, self.Kd

    @property
    def Tt(self):
        """The tracking time constant, or None when it is not set."""
        return self._Tt

    @Tt.setter
    def Tt(self, Tt):
        """Set the tracking time constant. Zero, negative or NaN raises ValueError."""
        # `not Tt > 0` is also true for NaN, which `Tt <= 0` would let through.
        if Tt is not None and not Tt > 0:
            raise ValueError(f'Tt must be a positive time, got {Tt}')
        self._Tt = Tt

    @property
    def tracking_tuning(self):
        """The time constant used in the tracking feedback loop (Tt)"""
        return self.Tt

    @tracking_tuning.setter
    def tracking_tuning(self, Tt):
        """Set the tracking time constant (Tt)."""
        self.Tt = Tt

    @tunings.setter
    def tunings(self, tunings):
        """Set the PID tunings."""
        self.Kp, self.Ki, self.Kd = tunings

    @property
    def auto_mode(self):
        """Whether the controller is currently enabled (in auto mode) or not."""
        return self._auto_mode

    @property
    def tracking_mode(self):
        """Whether the controller is currently in tracking mode or not."""
        return self._tracking_mode

    @auto_mode.setter
    def auto_mode(self, enabled):
        """Enable or disable the PID controller."""
        self.set_auto_mode(enabled)

    @tracking_mode.setter
    def tracking_mode(self, enabled):
        """Enable or disable tracking mode."""
        self.set_tracking_mode(enabled)

    def set_tracking_mode(self, enabled):
        """
        Enable or disable tracking mode.

        In tracking mode, each call needs track_in_ and Tt must be set. The integral is not
        clamped to the output limits; the tracking term keeps it consistent with the applied
        output instead.
        """
        self._tracking_mode = enabled

    def set_auto_mode(self, enabled, last_output=None):
        """
        Enable or disable the PID controller, optionally setting the last output value.

        This is useful if some system has been manually controlled and if the PID should take over.
        In that case, disable the PID by setting auto mode to False and later when the PID should
        be turned back on, pass the last output variable (the control variable) and it will be set
        as the starting I-term when the PID is set to auto mode.

        :param enabled: Whether auto mode should be enabled, True or False
        :param last_output: The last output, or the control variable, that the PID should start
            from when going from manual mode to auto mode. Has no effect if the PID is already in
            auto mode.
        """
        if enabled and not self._auto_mode:
            # Switching from manual mode to auto, reset
            self.reset()

            self._integral = last_output if (last_output is not None) else 0
            if not self.tracking_mode:
                self._integral = _clamp(self._integral, self.output_limits)
            # Tracking compares what was applied with the last unclamped output.
            # reset() leaves 0 there, so the first step would read the whole
            # applied value as a tracking error and kick the integral by it.
            # The output the controller starts from is the integral just set.
            self._last_output_not_clamped = self._integral

        self._auto_mode = enabled

    @property
    def output_limits(self):
        """
        The current output limits as a 2-tuple: (lower, upper).

        See also the *output_limits* parameter in :meth:`PID.__init__`.
        """
        return self._min_output, self._max_output

    @output_limits.setter
    def output_limits(self, limits):
        """Set the output limits."""
        if limits is None:
            self._min_output, self._max_output = None, None
            return

        min_output, max_output = limits

        if (None not in limits) and (max_output < min_output):
            raise ValueError('lower limit must be less than upper limit')

        self._min_output = min_output
        self._max_output = max_output
        if not self.tracking_mode:
            self._integral = _clamp(self._integral, self.output_limits)
        self._last_output_clamped = _clamp(self._last_output_clamped, self.output_limits)

    def reset(self):
        """
        Reset the PID controller internals.

        This sets each term to 0 as well as clearing the integral, the last output and the last
        input (derivative calculation).
        """
        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._integral = _clamp(self._integral, self.output_limits)

        self._last_time = self.time_fn()
        self._last_output_clamped = None
        self._last_output_not_clamped = 0.0
        self._last_input = None
        self._last_error = None
        self._holding = False
