__all__ = ["PlaybackCommand", "RecordCommand"]

from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Callable, Any, List

import commands2
import wpilib


class PlaybackCommand(commands2.CommandBase):
    """A Command that iterates over values in a file and calls a function with each iteration. Useful for recording
    and replaying autonomous routines. The Command finishes when the last value has been iterated over
    """

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
        self._steps = []
        try:
            # `.resolve()` changes the user-supplied relative path into an absolute path
            self._steps = parse_file(Path(file_path).resolve())
        except FileNotFoundError:
            wpilib.reportError(f"Recording file not found in PlaybackCommand!")

    def initialize(self):
        # Reset the step index. Like rewinding a video to the start
        self._index = 0

    def execute(self):
        # If there aren't any instructions in the list, don't execute.
        # A non-existent or empty file could lead to there being no steps in the list
        if not self._steps:
            return

        # Run the Callable and pass the current step as the first argument
        self._to_run(self._steps[self._index])

        # Increment the step count. Like hitting "play" on a video
        self._index += 1

    def isFinished(self) -> bool:
        # The Command is finished executing if all the steps have been "used up"
        # (i.e. the recording has reached its end)
        return self._index >= len(self._steps)


class RecordCommand(commands2.CommandBase):
    """A Command that records a set of values returned by a Callable.
    These values can be played back using a `PlaybackCommand`
    """

    # A list of ordered values to save to the file
    _steps = []

    def __init__(self, provider: Callable[[], str]):
        """Construct a `RecordCommand`

        :param provider: A Callable that returns a value when called. Each value will be recorded into a file
        """
        commands2.CommandBase.__init__(self)
        self._provider = provider

    def initialize(self):
        # Clear the list of recorded values
        self._steps = []

    def execute(self):
        # Call the provider function and obtain a value
        value = self._provider()

        # Add the value to the end of a list so that it will be saved when the Command ends
        self._steps.append(value)

    def end(self, interrupted: bool):
        # The folder where recording files should be saved
        # `.resolve()` changes a relative path into an absolute path
        path = Path("./recordings").resolve()

        # Create the folder if it doesn't exist
        path.mkdir(exist_ok=True)

        # Generate a filename based on the current time
        filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".txt"

        # Save the values to a file
        save_to_file(path / filename, self._steps)


def parse_file(path: PathLike) -> List[str]:
    """Parse a newline-seperated file into a list of values

    :param path: Absolute path to the file
    """
    # Open the file in 'read text' mode as a variable `f`
    with open(path, "rt") as f:
        # Read each line and the values into a list.
        # Remove the newline character from the end of each value
        values = [line.rstrip("\n") for line in f.readlines()]

        # Filter out any empty values
        values = [v for v in values if v != ""]

        return values


def save_to_file(path: PathLike, values: List[str]):
    """Write a list of values to a file

    :param path: Absolute path to the file
    :param values: The values to write
    """
    # Join each value together into a newline-seperated string
    text = "\n".join(values)

    # Open the file in 'write text' mode as a variable `f`
    with open(path, "wt") as f:
        # Write the string to a file
        f.write(text)
