import math
import typing

import commands2
import wpilib

import dashboard
from container import RobotContainer
from util import CountdownTimer


class Robot(commands2.TimedCommandRobot):
    autonomous_command: typing.Optional[commands2.Command] = None

    def robotInit(self) -> None:
        self.container = RobotContainer()
        self.scheduler = commands2.CommandScheduler.getInstance()

        # A timer to countdown remaining match time, starting from 2:30
        self.countdown = CountdownTimer(2.5 * 60)
        dashboard.add_number("Time Remaining", lambda: math.floor(self.countdown.get()))

    def autonomousInit(self) -> None:
        self.autonomous_command = self.container.get_autonomous_command()

        if self.autonomous_command:
            self.autonomous_command.schedule()

        # Start the countdown timer if competing in a real match
        if wpilib.DriverStation.isFMSAttached():
            self.countdown.reset()
            self.countdown.start()

    def teleopInit(self) -> None:
        if self.autonomous_command:
            self.autonomous_command.cancel()

    def testInit(self) -> None:
        self.scheduler.cancelAll()

    def robotPeriodic(self) -> None:
        commands2.TimedCommandRobot.robotPeriodic(self)

        # Periodically update all registered values on the Smart Dashboard
        dashboard.update_dashboard()


if __name__ == "__main__":
    wpilib.run(Robot)
