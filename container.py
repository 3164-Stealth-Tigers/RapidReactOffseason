from pathlib import Path

import commands2.button
import wpilib

from map import AutoConstants
from oi import XboxDriver, XboxOperator
from replay import PlaybackCommand
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

        # Enable the camera feed
        wpilib.CameraServer.launch()

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
        # Drive Out of Tarmac auto
        # Drive backwards out of the tarmac. The Command will end after 4 seconds in case the encoders fail.
        exit_tarmac_auto = self.drivetrain.get_drive_distance_command(
            AutoConstants.DRIVE_AWAY_FROM_HUB_DISTANCE,
            AutoConstants.DRIVE_AWAY_FROM_HUB_SPEED,
        ).withTimeout(3)
        # Add the routine to the autonomous chooser
        self.chooser.addOption("Exit Tarmac", exit_tarmac_auto)

        # Old 1-Ball Preloaded auto
        one_ball_auto = commands2.SequentialCommandGroup(
            # Play back a sequence that lifts the arm to the low goal. The arm initially needs a large amount of power
            # to get moving, then requires a smaller amount of power to hold at a certain height.
            PlaybackCommand(
                # The file path relative to this script's folder
                Path(__file__).parent / "resources" / "1_ball_auto_arm.txt",
                # Continuously update the arm's power with values from the above file.
                lambda power: self.arm.set_power(float(power)),
            ),
            # A ParallelCommandGroup runs both the supplied Commands at the same time.
            commands2.ParallelCommandGroup(
                # Hold the arm at the low goal.
                self.arm.get_hold_position_command(),
                # Ram the robot into the hub
                commands2.RunCommand(lambda: self.drivetrain.arcade_drive(1, 0)),
            )
            # After 0.5 seconds, stop moving the robot
            .withTimeout(0.5).andThen(lambda: self.drivetrain.arcade_drive(0, 0)),
            # Slowly drop the arm for 1.75 seconds
            commands2.RunCommand(lambda: self.arm.set_power(0.2))
            .withTimeout(1.75)
            .andThen(lambda: self.arm.set_power(0)),
            # Drive out of the tarmac
            self.drivetrain.get_drive_distance_command(
                AutoConstants.DRIVE_AWAY_FROM_HUB_DISTANCE,
                AutoConstants.DRIVE_AWAY_FROM_HUB_SPEED,
            ).withTimeout(3),
        )
        # This routine requires both the drivetrain and arm subsystems
        one_ball_auto.addRequirements([self.drivetrain, self.arm])
        # Add the routine to the autonomous chooser as the default option
        self.chooser.setDefaultOption("1-Ball Preloaded", one_ball_auto)
