from typing import Callable

import commands2
import ctre
import wpilib
import wpilib.drive

import dashboard
from map import DrivetrainConstants, DriveProfile


class Drivetrain(commands2.SubsystemBase):
    """The Drivetrain subsystem. Contains the motors and encoders on the drive base, as well as Commands that
    interact with those components. There should be one instance of this class created in the `RobotContainer`
    """

    def __init__(self):
        commands2.SubsystemBase.__init__(self)

        # Create motor objects to interact with the physical robot
        fl_motor = wpilib.Spark(DrivetrainConstants.FRONT_LEFT_MOTOR_PORT)
        bl_motor = wpilib.Spark(DrivetrainConstants.BACK_LEFT_MOTOR_PORT)
        l_motors = wpilib.MotorControllerGroup(fl_motor, bl_motor)

        fr_motor = wpilib.Spark(DrivetrainConstants.FRONT_RIGHT_MOTOR_PORT)
        br_motor = wpilib.Spark(DrivetrainConstants.BACK_RIGHT_MOTOR_PORT)
        r_motors = wpilib.MotorControllerGroup(fr_motor, br_motor)

        # Depending on the mechanical robot configuation, either the left or the right side may
        # need to be inverted (i.e. when positive voltage is applied, a motor turns backwards rather than forwards)
        l_motors.setInverted(DrivetrainConstants.LEFT_MOTOR_INVERTED)
        r_motors.setInverted(DrivetrainConstants.RIGHT_MOTOR_INVERTED)

        # The motors are setup in a "differential drive" configuartion.
        # In this config, all the motors on each side of the drivetrain are chained together.
        # To turn, one side applies more power than the other
        self._drive = wpilib.drive.DifferentialDrive(l_motors, r_motors)

        # Encoders report how fast (velocity) and how far (distance) motors are turning.
        self._l_encoder = ctre.WPI_CANCoder(DrivetrainConstants.LEFT_ENCODER_PORT)
        self._r_encoder = ctre.WPI_CANCoder(DrivetrainConstants.RIGHT_ENCODER_PORT)

        # By multiplying the wheel's circumference by the encoder's CPR (Cycles per Revolution), the wheel's distance
        # travelled can be calculated. CPR is the number of ticks (an arbitrary unit) reported by the encoder in one
        # revolution (360 degrees rotation)
        self._l_encoder.configFeedbackCoefficient(
            DrivetrainConstants.ENCODER_DISTANCE_PER_CYCLE,
            "metres",
            ctre.SensorTimeBase.PerSecond,
        )
        self._r_encoder.configFeedbackCoefficient(
            DrivetrainConstants.ENCODER_DISTANCE_PER_CYCLE,
            "metres",
            ctre.SensorTimeBase.PerSecond,
        )

        # Encoders need to be inverted according to motor inversion
        self._l_encoder.configSensorDirection(
            DrivetrainConstants.LEFT_ENCODER_INVERTED,
        )
        self._r_encoder.configSensorDirection(
            DrivetrainConstants.RIGHT_ENCODER_INVERTED,
        )

        # Add subsystem info to Smart Dashboard
        dashboard.add_number("Average Distance", lambda: self.distance_traveled)
        dashboard.add_number("Left Velocity", self._l_encoder.getVelocity)
        dashboard.add_number("Right Velocity", self._r_encoder.getVelocity)
        dashboard.add_number("Left Position", self._l_encoder.getPosition)
        dashboard.add_number("Right Position", self._r_encoder.getPosition)

    # Public methods can be accessed by Commands

    def arcade_drive(self, forward: float, rotation: float):
        """Drive the robot with joystick controls

        :param forward: Movement along the Y axis. From -1 to 1
        :param rotation: Movement around the Z axis. From -1 to 1
        """
        self._drive.arcadeDrive(forward, rotation, False)

    def stop(self):
        """Stop the drive motors"""
        self._drive.arcadeDrive(0, 0)

    def zero_encoders(self):
        """Reset the encoders' recorded position to zero"""
        self._l_encoder.setPosition(0)
        self._r_encoder.setPosition(0)

    # Properties report information about the subsystem, usually from sensors

    @property
    def distance_traveled(self) -> float:
        """The average distance travelled by the robot's wheels in metres"""
        return (self._l_encoder.getPosition() + self._r_encoder.getPosition()) / 2

    # Command factories
    # When these methods are called, they return a Command that can be scheduled and run

    def get_default_command(
        self,
        forward: Callable[[], float],
        rotation: Callable[[], float],
        mod: Callable[[], bool],
    ):
        """A Command that drives the robot with joystick controls

        :param forward: A function that returns a number representing movement along the Y axis, from -1 to 1
        :param rotation: A function that returns a number representing rotation around the Z axis, from -1 to 1
        :param mod: A function that returns whether the robot should be slowed down to allow finer control.
        """

        def drive_speed():
            """The robot's movement along the Y axis."""
            # If the modifier button isn't pressed, move full speed. If it is pressed, move at a slower speed.
            # Call the forward() function to get the operator's joystick input, then multiply it by the full or slow
            # speed modifier.
            # fmt: off
            return forward() * (
                DriveProfile.FULL_DRIVE_SPEED
                if not mod()
                else DriveProfile.MOD_DRIVE_SPEED
            )
            # fmt: on

        def turn_speed():
            """The robot's movement around the Z axis."""
            # If the modifier button isn't pressed, turn full speed. If it is pressed, turn at a slower speed
            # fmt: off
            return rotation() * (
                DriveProfile.FULL_TURN_SPEED
                if not mod()
                else DriveProfile.MOD_TURN_SPEED
            )
            # fmt: on

        # Constantly run the drive_speed() and turn_speed() functions, getting new values from a joystick
        # Call the arcade_drive() method with these values to make the robot move
        # After the Command ends (i.e. end of the match), stop the motors
        return commands2.RunCommand(
            lambda: self.arcade_drive(drive_speed(), turn_speed()),
            self,
        ).andThen(self.stop)

    def get_drive_distance_command(self, distance: float, speed: float):
        """A Command that drives the robot a certain distance using its encoders

        :param distance: The distance the robot should drive in metres. Can be a positive or negative number
        :param speed: The speed and direction the robot should move, from -1 to 1. A positive number indicates driving
        """
        return _DriveDistanceCommand(distance, speed, self)


class _DriveDistanceCommand(commands2.CommandBase):
    """A Command that drives the robot a certain distance using its encoders"""

    def __init__(self, distance: float, speed: float, drivetrain: Drivetrain):
        """Construct a DriveDistanceCommand

        :param distance: The distance the robot should drive in metres. Can be a positive or negative number
        :param speed: The speed and direction the robot should move, from -1 to 1. A positive number indicates driving
        forwards and a negative number indicates driving backwards.
        :param drivetrain: An instance of the `Drivetrain` subsystem
        """
        commands2.CommandBase.__init__(self)
        self._goal = abs(distance)
        self._speed = speed
        self._drivetrain = drivetrain

    def initialize(self) -> None:
        # Reset the measured encoder distance
        self._drivetrain.zero_encoders()

    def execute(self) -> None:
        self._drivetrain.arcade_drive(self._speed, 0)

    def end(self, interrupted: bool) -> None:
        # Stop moving the robot
        self._drivetrain.stop()

    def isFinished(self) -> bool:
        # The Command is finished when the amount of distance traveled by the robot is greater than or equal to
        # the goal distance
        return abs(self._drivetrain.distance_traveled) >= self._goal
