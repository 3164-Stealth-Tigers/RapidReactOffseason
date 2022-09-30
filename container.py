import commands2.button
import wpilib

from oi import XboxDriver, XboxOperator
from subsystems import Drivetrain, Arm, Winch


class RobotContainer:
    def __init__(self):
        """Constructor method"""
        # Configure the Driver Station not to report errors when a joystick isn't plugged in
        wpilib.DriverStation.silenceJoystickConnectionWarning(silence=True)

        # Subsystems represent self-contained parts of the robot (e.g. the drivetrain, arm, winch)
        # Subsystems expose Commands that can be arranged to make the robot run
        self.drivetrain = Drivetrain()
        self.arm = Arm()
        self.winch = Winch()

        # Joysticks are plugged into the driver laptop and used during the teleop period to control the robot
        # Each joystick is plugged into a port, ranging from 0 to 5

        # The drive joystick controls the drivetrain (i.e. movement)
        self.drive_stick = XboxDriver(0)

        # The operator joystick controls the arm and winch
        self.operator_stick = XboxOperator(1)

        # Default commands run whenever no other commands are scheduled
        # This included the teleop period, so code for teleop control should be set as the default command
        self.drivetrain.setDefaultCommand(
            # Drive the robot forwards and backwards with the left stick on an Xbox controller
            # Turn left and right with the right stick
            # Hold either bumper to move slowly
            self.drivetrain.get_default_command(
                self.drive_stick.forward,
                self.drive_stick.turn,
                self.drive_stick.mod,
            )
        )

        self.arm.setDefaultCommand(
            # Control the arm motors' turning power with the left stick on an Xbox controller.
            # Releasing the joystick causes the arm to fall slowly
            self.arm.get_default_command(self.operator_stick.arm)
        )

        # Bind buttons to Commands
        self.configure_button_bindings()

        # Autonomous chooser component
        # Adds a dropdown menu to the Driver Station that allows users to pick which autonomous routine (Command group)
        # to run
        self.chooser = wpilib.SendableChooser()
        self.add_autonomous_routines()

        # Put the chooser on Smart Dashboard
        wpilib.SmartDashboard.putData(self.chooser)

    def configure_button_bindings(self):
        """Bind buttons on the Xbox controllers to run Commands"""

        # Wind the winch while holding "up" on the d-pad
        self.operator_stick.wind_winch.whenHeld(self.winch.get_wind_command())

        # Unwind the winch while holding "down" on the d-pad
        self.operator_stick.unwind_winch.whenHeld(self.winch.get_unwind_command())

    def get_autonomous_command(self) -> commands2.Command:
        return self.chooser.getSelected()

    def add_autonomous_routines(self):
        """Add routines to the autonomous picker"""
        pass
