"""A collection of utility methods used throughout the codebase."""

import wpilib

FEET_TO_METRES = 0.3048


def to_voltage(power: float) -> float:
    """Adjust a PWM value to the robot's current voltage. For example, passing a `power` of 0.5 while the robot is
    running at 12 volts would return 6, but passing a `power` of 0.5 while the robot is running at 9 volts would
    return 4.5.

    :param power: PWM power value, from -1 to 1
    :return: The adjusted voltage in volts, from -12 to 12 (with a 12v nominal battery)
    """
    return power * wpilib.DriverStation.getBatteryVoltage()
