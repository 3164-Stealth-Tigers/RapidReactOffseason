"""Wrapper around the SmartDashboard class that provides the ability to automatically update values on the dashboard
using a provider method for each value.

`update_dashboard()` should be run periodically to update the dashboard.
"""

import enum
from dataclasses import dataclass
from typing import Callable, List, Any, Dict

import wpilib


class _ValueType(enum.Enum):
    NUMBER = 1
    STRING = 2
    BOOLEAN = 3
    NUMBER_ARRAY = 4
    STRING_ARRAY = 5
    BOOLEAN_ARRAY = 6


@dataclass
class _TypedProvider:
    provider: Callable
    value_type: _ValueType


# A dictionary of provider Callables, each with its own unique "key."
# The key doubles as the value name in Smart Dashboard
providers: Dict[str, _TypedProvider] = dict()


def update_dashboard():
    """Query each key-value pair assigned to the dashboard and publish new values.
    Run periodically (every robot loop)
    """
    for key, value in providers.items():
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
        }[value.value_type]

        # Call the method to add the value to Smart Dashboard
        method(key, value.provider())


def _add_value(key: str, provider: Callable[[], Any], value_type: _ValueType):
    providers[key] = _TypedProvider(provider, value_type)


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


def delete_value(key: str):
    """Removes a value from Smart Dashboard and prevents it from automatically updating

    :param key: The unique name of the value to delete
    """
    # Remove the value from the dictionary. `del` actually removes the value, rather than just setting it to None
    del providers[key]

    # Remove the value from Smart Dashboard
    wpilib.SmartDashboard.delete(key)
