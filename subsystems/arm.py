from typing import Callable

import commands2
import wpilib

from map import ArmConstants


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
        # If this commands is set as a default command, it will repeat forever
        return commands2.SequentialCommandGroup(
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
