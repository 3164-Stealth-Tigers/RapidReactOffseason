import typing

import wpilib.simulation
from pyfrc.physics import motor_cfgs
from pyfrc.physics.core import PhysicsInterface
from pyfrc.physics.tankmodel import TankModel
from pyfrc.physics.units import units

from util import FEET_TO_METRES
from map import DrivetrainConstants, ArmConstants

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
        self.l_encoder = robot.container.drivetrain._l_encoder.getSimCollection()
        self.r_encoder = robot.container.drivetrain._r_encoder.getSimCollection()

        # Simulate arm motors
        self.arm_motor = wpilib.simulation.PWMSim(ArmConstants.LEFT_MOTOR_PORT)

    def update_sim(self, now, tm_diff):
        # Simulate the drivetrain
        l_motor = self.l_motor.getSpeed()
        r_motor = self.r_motor.getSpeed()

        transform = self.drivetrain.calculate(l_motor, r_motor, tm_diff)
        self.physics_controller.move_robot(transform)

        # Simulate encoder readings

        # By setting the "raw position", any user calls to setPosition() are accounted for, and the simulated value
        # is modified accordingly.
        # Position needs to be supplied in encoder ticks, so first convert feet to metres, then metres to ticks.
        # The simulated encoder values are inverted according to whether they're inverted in the robot code.
        self.l_encoder.setRawPosition(
            -int(
                self.drivetrain.l_position
                * FEET_TO_METRES
                / DrivetrainConstants.ENCODER_DISTANCE_PER_CYCLE
            )
        )
        self.r_encoder.setRawPosition(
            int(
                self.drivetrain.r_position
                * FEET_TO_METRES
                / DrivetrainConstants.ENCODER_DISTANCE_PER_CYCLE
            )
        )

        # The velocity needs to be supplied in ticks/100ms. The velocity data is originally in feet/s, so change from
        # feet/s to m/s, then from m/s to ticks/s, then from ticks/s to ticks/100ms.
        self.l_encoder.setVelocity(
            -int(
                self.drivetrain.l_velocity
                * FEET_TO_METRES
                / DrivetrainConstants.ENCODER_DISTANCE_PER_CYCLE
                * 0.1
            )
        )
        self.r_encoder.setVelocity(
            int(
                self.drivetrain.r_velocity
                * FEET_TO_METRES
                / DrivetrainConstants.ENCODER_DISTANCE_PER_CYCLE
                * 0.1
            )
        )
