import commands2
import ctre
import wpilib
import wpilib.drive

from map import DrivetrainConstants

class Drivetrain(commands2.SubsystemBase):

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
        self._l_encoder = ctre.CANCoder(DrivetrainConstants.LEFT_ENCODER_PORT)
        self._r_encoder = ctre.CANCoder(DrivetrainConstants.RIGHT_ENCODER_PORT)

        # By multiplying the wheel's circumference by the encoder's CPR (Cycles per Revolution), the wheel's distance travelled can be calculated.
        # CPR is the number of ticks (an arbitrary unit) reported by the encoder in one revolution (360 degrees rotation)
        self._l_encoder.configFeedbackCoefficient(DrivetrainConstants.ENCODER_DISTANCE_PER_CYCLE, "metres", ctre.SensorTimeBase.PerSecond)
        self._r_encoder.configFeedbackCoefficient(DrivetrainConstants.ENCODER_DISTANCE_PER_CYCLE, "metres", ctre.SensorTimeBase.PerSecond)

        # Encoders need to be inverted according to motor inversion
        self._l_encoder.configSensorDirection(DrivetrainConstants.LEFT_SIDE_INVERTED)
        self._r_encoder.configSensorDirection(DrivetrainConstants.RIGHT_SIDE_INVERTED)
    
    # Public methods can be accessed by Commands

    def arcade_drive(self, forward: float, rotation: float):
        self._drive.arcadeDrive(forward, rotation, False)

    