import typing

import commands2
import wpilib

import dashboard
from container import RobotContainer


class Robot(commands2.TimedCommandRobot):
    autonomous_command: typing.Optional[commands2.Command] = None

    def robotInit(self) -> None:
        self.container = RobotContainer()
        self.scheduler = commands2.CommandScheduler.getInstance()

    def autonomousInit(self) -> None:
        self.autonomous_command = self.container.get_autonomous_command()

        if self.autonomous_command:
            self.autonomous_command.schedule()

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
