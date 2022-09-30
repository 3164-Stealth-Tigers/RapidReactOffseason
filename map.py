from math import pi


class DriveProfile:
    """Information about how the robot should drive (i.e. speeds)"""

    FULL_DRIVE_SPEED = 1
    MOD_DRIVE_SPEED = 0.5

    FULL_TURN_SPEED = 1
    MOD_TURN_SPEED = 0.6


class DrivetrainConstants:
    FRONT_LEFT_MOTOR_PORT = 2
    BACK_LEFT_MOTOR_PORT = 3
    FRONT_RIGHT_MOTOR_PORT = 0
    BACK_RIGHT_MOTOR_PORT = 1

    LEFT_SIDE_INVERTED = True
    RIGHT_SIDE_INVERTED = False

    LEFT_ENCODER_PORT = 1
    RIGHT_ENCODER_PORT = 2

    ENCODER_CPR = 4096
    WHEEL_DIAMETER = 0.1524  # Metres
    ENCODER_DISTANCE_PER_CYCLE = WHEEL_DIAMETER * pi / ENCODER_CPR


class ArmConstants:
    LEFT_MOTOR_PORT = 4
    RIGHT_MOTOR_PORT = 5


class WinchConstants:
    MOTOR_PORT = 6

    INVERTED = True
