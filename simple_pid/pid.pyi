from typing import Callable, Optional

import typing_extensions

_Limits: typing_extensions.TypeAlias = tuple[float | None, float | None]
_Components: typing_extensions.TypeAlias = tuple[float, float, float]
_Tunings: typing_extensions.TypeAlias = tuple[float, float, float]

def _clamp(value: float | None, limits: _Limits) -> float | None: ...

class PID:
    Kp: float
    Ki: float
    Kd: float
    setpoint: float
    sample_time: float | None
    proportional_on_measurement: bool
    differential_on_measurement: bool
    error_map: Callable[[float], float] | None
    time_fn: Callable[[], float]
    def __init__(
        self,
        Kp: float = ...,
        Ki: float = ...,
        Kd: float = ...,
        setpoint: float = ...,
        sample_time: float | None = ...,
        output_limits: _Limits = ...,
        auto_mode: bool = ...,
        proportional_on_measurement: bool = ...,
        differential_on_measurement: bool = ...,
        error_map: Callable[[float], float] | None = ...,
        time_fn: Callable[[], float] | None = ...,
        starting_output: float = ...,
    ) -> None: ...
    def __call__(self, input_: float, dt: float | None = ...) -> float | None: ...
    def __repr__(self) -> str: ...
    @property
    def components(self) -> _Components: ...
    @property
    def tunings(self) -> _Tunings: ...
    @tunings.setter
    def tunings(self, tunings: _Tunings) -> None: ...
    @property
    def auto_mode(self) -> bool: ...
    @auto_mode.setter
    def auto_mode(self, enabled: bool) -> None: ...
    def set_auto_mode(self, enabled: bool, last_output: float | None = ...) -> None: ...
    @property
    def output_limits(self) -> _Limits: ...
    @output_limits.setter
    def output_limits(self, limits: _Limits) -> None: ...
    def reset(self) -> None: ...
