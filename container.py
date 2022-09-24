import wpilib

from subsystems import Drivetrain


class RobotContainer:
    def __init__(self):
        """Constructor method"""
        # Subsystems represent self-contained parts of the robot (e.g. the drivetrain, arm, winch)
        # Subsystems expose Commands that can be arranged to make the robot run
        self.drivetrain = Drivetrain()

        # Joysticks are plugged into the driver laptop and used during the teleop period to control the robot
        # Each joystick is plugged into a port, ranging from 0 to 5
        self.drive_stick = wpilib.XboxController(0)

        # Default commands run whenever no other commands are scheduled
        # This included the teleop period, so code for teleop control should be set as the defualt command
        self.drivetrain.setDefaultCommand(
            # Drive the robot forwards and backwards with the left stick on an Xbox controller
            # Turn left and right with the right stick
            self.drivetrain.get_default_command(
                # Y sticks report a value of -1 when the stick is pushed all the way up, so invert the value
                lambda: -self.drive_stick.getLeftY(),
                self.drive_stick.getRightX,
            )
        )
