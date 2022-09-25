import os.path
from typing import Callable, Any, List

import commands2


class PlaybackCommand(commands2.CommandBase):
    """Streams a list of values from a file into a function, just like using an action replay for a video game"""

    # The number of iterations the command has gone through. Used to play the correct step in the recording
    _index = 0

    def __init__(
        self,
        file_path: str,
        to_run: Callable[[str], Any],
        requirements: List[commands2.Subsystem] = [],
    ):
        """Construct a `PlaybackCommand`

        :param file_path: A relative or absolute path to a new-line seperated text file of values to read
        :param to_run: A Callable to continuously run,
        with the next item from the file passed as an argument each iteration
        :param requirements: Subsystems required by this Command
        """
        commands2.CommandBase.__init__(self)
        self._to_run = to_run

        # Add subsystem requirements for this Command
        self.addRequirements(requirements)

        # Load each value from the recording file into a list
        self._steps = parse_file(os.path.abspath(file_path))

    def initialize(self):
        # Reset the step index, so that the replay starts at the beginning each time the Command is scheduled
        self._index = 0

    def execute(self):
        # Run the Callable with the next step as an argument
        self._to_run(self._steps[self._index])

        # Increment the step count
        self._index += 1

    def isFinished(self) -> bool:
        # The Command is finished executing if all the steps have been "used up"
        return self._index >= len(self._steps) - 1


class RecordCommand(commands2.CommandBase):
    """Records a list of values into a file. The file can be played back using a `PlaybackCommand`"""

    def __init__(self):
        commands2.CommandBase.__init__(self)


def parse_file(path: str) -> List[str]:
    """Parse a newline-seperated file into a list of values

    :param path: Absolute path to the file
    """
    # Open the file in 'read text' mode and store it as a variable `f`
    with open(path, "rt") as f:
        # Read each line and the values into a list.
        # Remove the newline character from the end of each value
        values = [line.rstrip("\n") for line in f.readlines()]

        # Filter out any empty values
        values = [v for v in values if v != ""]

        return values
