from math import pi

from util import FEET_TO_METRES


class AutoConstants:
    DRIVE_AWAY_FROM_HUB_DISTANCE = 7.5 * FEET_TO_METRES
    DRIVE_AWAY_FROM_HUB_SPEED = -0.5


class DriveProfile:
    """Information about how the robot should drive (i.e. speeds)"""

    FULL_DRIVE_SPEED = 1
    MOD_DRIVE_SPEED = 0.5

    FULL_TURN_SPEED = 1
    MOD_TURN_SPEED = 0.6


class DrivetrainConstants:
    # Motor positions are from the perspective of behind the back of the robot, facing the front.
    # The back of the robot is the side closest to the electrical board, and the front side
    # is closest to the arm.
    FRONT_LEFT_MOTOR_PORT = 0
    BACK_LEFT_MOTOR_PORT = 1
    FRONT_RIGHT_MOTOR_PORT = 2
    BACK_RIGHT_MOTOR_PORT = 3

    LEFT_MOTOR_INVERTED = False
    RIGHT_MOTOR_INVERTED = True

    LEFT_ENCODER_PORT = 1
    RIGHT_ENCODER_PORT = 2

    LEFT_ENCODER_INVERTED = True
    RIGHT_ENCODER_INVERTED = False

    ENCODER_CPR = 4096
    WHEEL_DIAMETER = 0.1524  # Metres
    ENCODER_DISTANCE_PER_CYCLE = WHEEL_DIAMETER * pi / ENCODER_CPR


class ArmConstants:
    LEFT_MOTOR_PORT = 4
    RIGHT_MOTOR_PORT = 5


class WinchConstants:
    MOTOR_PORT = 6

    INVERTED = True
