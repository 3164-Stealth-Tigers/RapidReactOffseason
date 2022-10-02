__all__ = ["InterruptableRunCommand", "RepeatingCommand"]

from typing import Callable, Any

import commands2


class InterruptableRunCommand(commands2.RunCommand):
    """A Command that runs a Callable continuously. When the Command ends, a second Callable is run"""

    def __init__(self, to_run: Callable[[], Any], on_end: Callable[[], Any]):
        """Constructor method

        :param to_run: A Callable that runs continuously
        :param on_end: A Callable that runs when the command ends
        """
        commands2.RunCommand.__init__(self, to_run)
        self.on_end = on_end

    def end(self, interrupted: bool):
        # end() is called whenever a Command finishes or is cancelled.
        # Run a user-supplied method when the Command ends
        self.on_end()


class RepeatingCommand(commands2.CommandBase):
    """A Command that runs another Command in a loop indefinitely. The `end` and `initialize` functions will run
    as they normally would and may run multiple times.
    """

    def __init__(self, command: commands2.Command):
        """Construct a RepeatingCommand

        :param command: The command to repeat indefinitely
        """
        commands2.CommandBase.__init__(self)

        if command.isGrouped():
            raise ValueError("Commands cannot be added to more than one CommandGroup")

        command.setGrouped(True)
        self.addRequirements(command.getRequirements())
        self._command = command

    def initialize(self) -> None:
        self._command.initialize()

    def execute(self) -> None:
        # Reset the command's state at the end of each iteration
        if self._command.isFinished():
            self._command.end(False)
            self._command.initialize()
            return

        self._command.execute()

    def end(self, interrupted: bool) -> None:
        self._command.end(interrupted)

    def runsWhenDisabled(self) -> bool:
        return self._command.runsWhenDisabled()
