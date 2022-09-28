import typing

import wpilib.simulation
from pyfrc.physics import motor_cfgs
from pyfrc.physics.core import PhysicsInterface
from pyfrc.physics.tankmodel import TankModel
from pyfrc.physics.units import units

from map import DrivetrainConstants, ArmConstants

FEET_TO_METRES = 0.3048

if typing.TYPE_CHECKING:
    from robot import Robot


class PhysicsEngine:
    def __init__(self, physics_controller: PhysicsInterface, robot: "Robot"):
        self.physics_controller = physics_controller

        # Simulate drive motors. Tank drive robots generally have 4 or more physical motors, but 2 is acceptable for
        # simulation purposes because of how the physical motors are chained together
        self.l_motor = wpilib.simulation.PWMSim(
            DrivetrainConstants.FRONT_LEFT_MOTOR_PORT
        )
        self.r_motor = wpilib.simulation.PWMSim(
            DrivetrainConstants.FRONT_RIGHT_MOTOR_PORT
        )

        # A mathematical model of the drivetrain used in simulation. Arbitrarily picked values are used here,
        # but they should be replaced by measured values
        self.drivetrain = TankModel.theory(
            # The drivetrain uses CIM motors: a type of PWM-controlled motor
            motor_cfgs.MOTOR_CFG_CIM,
            # The robot weighs 90 pounds
            robot_mass=90 * units.lbs,
            # The drive motors have a gear ratio of 10.71:1.
            # This means the motor has to fully rotate 10.71 times for the wheel to rotate once
            gearing=10.71,
            # 2 motors per side (4 motors total)
            nmotors=2,
            # Distance between the centers of the front and rear wheels
            x_wheelbase=21.865 * units.inch,
            # Diameter of one wheel
            wheel_diameter=6 * units.inch,
        )

        # Simulated encoders
        # Each encoder is represented by a name and index (port number), here `CANEncoder:CANCoder[x]`
        l_encoder = wpilib.simulation.SimDeviceSim(
            f"CANEncoder:CANCoder[{DrivetrainConstants.LEFT_ENCODER_PORT}]"
        )
        self.l_position = l_encoder.getDouble("position")
        self.l_velocity = l_encoder.getDouble("velocity")

        r_encoder = wpilib.simulation.SimDeviceSim(
            f"CANEncoder:CANCoder[{DrivetrainConstants.RIGHT_ENCODER_PORT}]"
        )
        self.r_position = r_encoder.getDouble("position")
        self.r_velocity = r_encoder.getDouble("velocity")

        # Simulate arm motors
        self.arm_motor = wpilib.simulation.PWMSim(ArmConstants.LEFT_MOTOR_PORT)

    def update_sim(self, now, tm_diff):
        # Simulate the drivetrain
        # Invert the speed values to match the behavior of the real robot
        l_motor = -self.l_motor.getSpeed()
        r_motor = -self.r_motor.getSpeed()

        transform = self.drivetrain.calculate(l_motor, r_motor, tm_diff)
        self.physics_controller.move_robot(transform)

        # Simulate encoder readings
        self.l_position.set(self.drivetrain.l_position * FEET_TO_METRES)
        self.l_velocity.set(self.drivetrain.l_velocity * FEET_TO_METRES)
        self.r_position.set(self.drivetrain.r_position * FEET_TO_METRES)
        self.r_velocity.set(self.drivetrain.r_velocity * FEET_TO_METRES)
