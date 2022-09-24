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
