from typing import Callable
import commands2
import wpilib

from commands import RepeatingCommand
from map import ArmConstants
from util import to_voltage


class Arm(commands2.SubsystemBase):
    """The arm is used for lifting balls into the Low Goal and hooking onto the pull-up bar"""

    def __init__(self):
        commands2.SubsystemBase.__init__(self)

        # The arm runs on two motors geared together (functioning as one motor).
        # Create an object representing the motor pair
        self._motors = wpilib.MotorControllerGroup(
            wpilib.Spark(ArmConstants.LEFT_MOTOR_PORT),
            wpilib.Spark(ArmConstants.RIGHT_MOTOR_PORT),
        )

    # Public methods

    def set_power(self, power: float):
        """Power the arm motors

        :param power: Power applied to the arm motors. From -1 to 1
        """
        self._motors.set(power)

    def set_voltage(self, volts: float):
        """Power the arm motors, adjusting for battery voltage sag. Useful for when consistency is required, such as
        during autonomous routines.

        This method changes the supplied `volts` to a PWM value under the hood by dividing by the current battery
        voltage. If 6 volts are supplied while the battery is running at 12 volts, the resulting PWM value will be 0.5.
        If the same 6 volts are supplied while the battery is running at 9 volts, the PWM value will be 0.67.
        This method can not create power out of thin air! For example, a battery running at 9 volts can not supply
        12 volts.

        :param volts: The voltage to apply to the arm motors. From -12 to 12 (on a 12v nominal battery)
        """
        self._motors.setVoltage(volts)

    # Properties

    @property
    def power(self) -> float:
        """The power supplied to the arm motors. From -1 to 1"""
        return self._motors.get()

    # Command factories

    def get_default_command(self, input_: Callable[[], float]):
        """A Command that powers the arm with a joystick, before slowly dropping it

        :param input_: A function that returns a number representing the motors' power, from -1 to 1
        """

        def input_detected() -> bool:
            """Evaluate the `input_` function, and return whether the result is greater than a small deadband value"""
            return input_() > 0.08

        def power() -> float:
            """
            Modify the range of the joystick input and add a small amount of power to the output,
            so the arm never falls
            """
            # Change the range of input values from [0, 1] to [0, 0.8].
            # Then, add 0.2 to the input value, resulting in the final power value.
            # Do this so there's always a little power on the motors, and the arm doesn't fall if the input value
            # drops quickly
            return input_() * 0.8 + 0.2

        # Run multiple commands in order.
        # Wait until input is detected, power the arm, drop the arm slowly, then stop the motor.
        # Repeat this command forever.
        return RepeatingCommand(
            commands2.SequentialCommandGroup(
                # Wait until joystick input is detected
                commands2.WaitUntilCommand(input_detected),
                # Power the arm with the joystick input, until the input is close to zero
                # fmt: off
                commands2.RunCommand(
                    lambda: self.set_power(power())
                ).until(
                    lambda: not input_detected()
                ),
                # fmt: on
                # Apply a small amount of power (0.2%) for 1.75 seconds so that the arm falls slowly.
                # Interrupt slow falling and return control to the user if input is detected.
                commands2.RunCommand(lambda: self.set_power(0.2))
                .withTimeout(1.75)
                .withInterrupt(input_detected),
            ).andThen(lambda: self.set_power(0), [self])
        )

    def get_hold_position_command(self):
        """A Command that holds the arm at its current height"""
        return _HoldPositionCommand(self)


class _HoldPositionCommand(commands2.CommandBase):
    """A Command that holds the arm at its current height"""

    _power: float

    def __init__(self, arm: Arm):
        """Construct a HoldPositionCommand

        :param arm: An instance of the `Arm` subsystem
        """
        commands2.CommandBase.__init__(self)
        self.addRequirements([arm])
        self._arm = arm

    def initialize(self) -> None:
        # Convert the current power to a voltage as a reference point. When `set_voltage` is called later, this value
        # will be converted back into a PWM value while maintaining the same arm height.
        self._power = to_voltage(self._arm.power)

    def execute(self) -> None:
        self._arm.set_voltage(self._power)

    def end(self, interrupted: bool) -> None:
        self._arm.set_power(0)
