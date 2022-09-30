"""The OI (Operator Input) module contains `Action Sets` and `Control Schemes`.

An `Action Set` defines the inputs a controller should have. For example, a driver's controller needs to have an input
for driving forwards and backwards. These inputs can be either functions that return a value such as a float or bool,
or they can be Commands buttons. A button can be bound to run a command when pressed, held, etc.

A `Control Scheme` implements an `Action Set` and defines which physical buttons or joysticks on a controller perform
each action. For example, on an Xbox controller, the left joystick might be bound to forwards and backwards movement.
Any special logic (e.g. inverting the Y axis on a joystick) is also defined in a `Control Scheme`.
"""

from typing import Protocol
from abc import abstractmethod

import wpilib
from commands2.button import Button, POVButton


# Action Sets


class DriverActionSet(Protocol):
    @abstractmethod
    def forward(self) -> float:
        """Movement along the Y axis, from -1 to 1"""
        raise NotImplementedError

    @abstractmethod
    def turn(self) -> float:
        """Rotation around the Z axis, from -1 (counter-clockwise) to 1 (clockwise)"""
        raise NotImplementedError

    @abstractmethod
    def mod(self) -> bool:
        """Whether the robot's speed should be slowed down"""
        raise NotImplementedError


class OperatorActionSet(Protocol):
    @property
    @abstractmethod
    def wind_winch(self) -> Button:
        """Button to wind the winch (pull the robot up)"""
        raise NotImplementedError

    @property
    @abstractmethod
    def unwind_winch(self) -> Button:
        """Button to unwind the winch (lower the robot)"""
        raise NotImplementedError

    @abstractmethod
    def arm(self) -> float:
        """The amount of power to give the arm motor, from -1 to 1"""
        raise NotImplementedError


# Control schemes


class XboxDriver(DriverActionSet):
    """Drive the robot with an Xbox controller"""

    def __init__(self, port: int):
        """Construct an XboxDriver

        :param port: The port that the joystick is plugged into. Reported on the Driver Station
        """
        self.stick = wpilib.XboxController(port)

    def forward(self) -> float:
        """The robot's movement along the X axis, controlled by moving the left joystick up and down. From -1 to 1"""
        return -self.stick.getLeftY()

    def turn(self) -> float:
        """The robot's movement around the Z axis, controlled by moving the right joystick left and right.
        From -1 to 1
        """
        return self.stick.getRightX()

    def mod(self) -> bool:
        """If either the left or right bumper is pressed, the robot should move slowly"""
        return self.stick.getLeftBumper() or self.stick.getRightBumper()


class XboxOperator(OperatorActionSet):
    """Operate the arm and winch with an Xbox controller"""

    def __init__(self, port: int):
        """Construct an XboxOperator

        :param port: The port that the joystick is plugged into. Reported on the Driver Station
        """
        self.stick = wpilib.XboxController(port)

    @property
    def wind_winch(self) -> Button:
        """Button to wind the winch by holding up on the d-pad"""
        return POVButton(self.stick, angle=0, povNumber=0)

    @property
    def unwind_winch(self) -> Button:
        """Button to unwind the winch by holding down on the d-pad"""
        return POVButton(self.stick, angle=180, povNumber=0)

    def arm(self) -> float:
        """Control the arm motors' power by moving the left joystick up and down. From -1 to 1"""
        return -self.stick.getLeftY()
