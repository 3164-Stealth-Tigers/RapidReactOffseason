from typing import Callable

import commands2
import ctre
import wpilib
import wpilib.drive

import dashboard
from map import DrivetrainConstants


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
        l_motors.setInverted(DrivetrainConstants.LEFT_SIDE_INVERTED)
        r_motors.setInverted(DrivetrainConstants.RIGHT_SIDE_INVERTED)

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
        self._l_encoder.configSensorDirection(DrivetrainConstants.LEFT_SIDE_INVERTED)
        self._r_encoder.configSensorDirection(DrivetrainConstants.RIGHT_SIDE_INVERTED)

        # Add subsystem info to Smart Dashboard
        dashboard.add_number("Average Distance", lambda: self.distance_traveled)
        dashboard.add_number("Left Velocity", self._l_encoder.getVelocity)
        dashboard.add_number("Right Velocity", self._r_encoder.getVelocity)

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
        self, forward: Callable[[], float], rotation: Callable[[], float]
    ):
        """A Command that drives the robot with joystick controls

        :param forward: A function that returns a number representing movement along the Y axis, from -1 to 1
        :param rotation: A function that returns a number representing rotation around the Z axis, from -1 to 1
        """
        # Constantly run the forward() and rotation() functions, getting new values from a joystick
        # Call the arcade_drive() method with these values to make the robot move
        # After the Command ends (i.e. end of the match), stop the motors
        return commands2.RunCommand(
            lambda: self.arcade_drive(forward(), rotation()), [self]
        ).andThen(self.stop)
