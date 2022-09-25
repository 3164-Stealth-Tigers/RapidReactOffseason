import commands2
import wpilib

import commands
from map import WinchConstants


class Winch(commands2.SubsystemBase):
    """A winch winds a string around a rotating drum, in order to pull or push a mechanism. The winch on this robot
    pulls the arm downwards, causing the robot to pull itself up on a bar
    """

    def __init__(self):
        commands2.SubsystemBase.__init__(self)

        # Winch motor
        self._motor = wpilib.Spark(WinchConstants.MOTOR_PORT)

        # Invert the direction the motor turns when positive voltage is applied
        self._motor.setInverted(WinchConstants.INVERTED)

    # Public methods

    def set_power(self, power: float):
        """Power the winch motor, causing the robot to pull down/let up the arm

        :param power: Power applied to the winch motor. From -1 to 1.
        A positive value will coil the string, pulling the arm down
        """

        self._motor.set(power)

    # Command factories

    def get_wind_command(self):
        """A Command that winds the winch up for as long as the Command is running"""
        # Run the winch motor at 100% power, then stop the motor when the Command ends
        return commands.InterruptableRunCommand(
            to_run=lambda: self.set_power(1),
            on_end=lambda: self.set_power(0),
        )

    def get_unwind_command(self):
        """A Command that unwinds the winch up for as long as the Command is running"""
        # Run the winch motor backwards at 100% power, then stop the motor when the Command ends
        return commands.InterruptableRunCommand(
            to_run=lambda: self.set_power(-1),
            on_end=lambda: self.set_power(0),
        )
