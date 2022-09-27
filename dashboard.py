"""Wrapper around the SmartDashboard class that provides the ability to automatically update values on the dashboard
using a provider method for each value.

`update_dashboard()` should be run periodically to update the dashboard.
"""

import enum
from dataclasses import dataclass
from typing import Callable, List, Any, Set

import wpilib


class _ValueType(enum.Enum):
    NUMBER = 1
    STRING = 2
    BOOLEAN = 3
    NUMBER_ARRAY = 4
    STRING_ARRAY = 5
    BOOLEAN_ARRAY = 6


@dataclass
class _KeyValuePair:
    key: str
    value: Callable
    value_type: _ValueType

    def __hash__(self):
        # A method used for determining whether a `_KeyValuePair` is identical to another inside a `set`
        return hash(self.key)


# A list of key-value pairs to query and publish to SmartDashboard
key_pairs: Set[_KeyValuePair] = set()


def update_dashboard():
    """Query each key-value pair assigned to the dashboard and publish new values.
    Run periodically (every robot loop)
    """
    for pair in key_pairs:
        # Different types need different methods to be added to Smart Dashboard.
        # Using the value type as an index, choose the correct methods from a dictionary.
        # This works because functions are considered objects in Python, and therefore can be stored as values in dicts
        method = {
            _ValueType.NUMBER: wpilib.SmartDashboard.putNumber,
            _ValueType.STRING: wpilib.SmartDashboard.putString,
            _ValueType.BOOLEAN: wpilib.SmartDashboard.putBoolean,
            _ValueType.NUMBER_ARRAY: wpilib.SmartDashboard.putNumberArray,
            _ValueType.STRING_ARRAY: wpilib.SmartDashboard.putStringArray,
            _ValueType.BOOLEAN_ARRAY: wpilib.SmartDashboard.putBooleanArray,
        }[pair.value_type]

        # Call the method to add the value to Smart Dashboard
        method(pair.key, pair.value())


def _add_value(key: str, provider: Callable[[], Any], value_type: _ValueType):
    key_pairs.add(_KeyValuePair(key, provider, value_type))


def add_number(key: str, provider: Callable[[], float]):
    """Add a floating-point numeric value to Smart Dashboard which will be updated periodically

    :param key: The unique name of the value
    :param provider: Function that provides an up-to-date value every time the dashboard is updated
    """
    _add_value(key, provider, _ValueType.NUMBER)


def add_string(key: str, provider: Callable[[], str]):
    """Add a string value to Smart Dashboard which will be updated periodically

    :param key: The unique name of the value
    :param provider: Function that provides an up-to-date value every time the dashboard is updated
    """
    _add_value(key, provider, _ValueType.STRING)


def add_boolean(key: str, provider: Callable[[], bool]):
    """Add a boolean value to Smart Dashboard which will be updated periodically

    :param key: The unique name of the value
    :param provider: Function that provides an up-to-date value every time the dashboard is updated
    """
    _add_value(key, provider, _ValueType.BOOLEAN)


def add_number_array(key: str, provider: Callable[[], List[float]]):
    """Add an array of floating-point numbers to Smart Dashboard which will be updated periodically

    :param key: The unique name of the value
    :param provider: Function that provides an up-to-date value every time the dashboard is updated
    """
    _add_value(key, provider, _ValueType.NUMBER_ARRAY)


def add_string_array(key: str, provider: Callable[[], List[str]]):
    """Add an array of strings to Smart Dashboard which will be updated periodically

    :param key: The unique name of the value
    :param provider: Function that provides an up-to-date value every time the dashboard is updated
    """
    _add_value(key, provider, _ValueType.STRING_ARRAY)


def add_boolean_array(key: str, provider: Callable[[], List[bool]]):
    """Add an array of booleans to Smart Dashboard which will be updated periodically

    :param key: The unique name of the value
    :param provider: Function that provides an up-to-date value every time the dashboard is updated
    """
    _add_value(key, provider, _ValueType.BOOLEAN_ARRAY)
