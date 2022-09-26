import enum
from dataclasses import dataclass
from typing import Callable, List, Any

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


# A list of key-value pairs to query and publish to SmartDashboard
key_pairs: List[_KeyValuePair] = []


def update_dashboard():
    """Query each key-value pair assigned to the dashboard and publish new values.
    Run periodically (every robot loop)
    """
    for pair in key_pairs:
        # Different types need different methods to be added to Smart Dashboard.
        # Choose a method from a dictionary corresponding to the data type
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
    key_pairs.append(
        _KeyValuePair(key, provider, value_type)
    )


def add_number(key: str, provider: Callable[[], float]):
    _add_value(key, provider, _ValueType.NUMBER)


def add_string(key: str, provider: Callable[[], str]):
    _add_value(key, provider, _ValueType.STRING)


def add_boolean(key: str, provider: Callable[[], bool]):
    _add_value(key, provider, _ValueType.BOOLEAN)


def add_number_array(key: str, provider: Callable[[], List[float]]):
    _add_value(key, provider, _ValueType.NUMBER_ARRAY)


def add_string_array(key: str, provider: Callable[[], List[str]]):
    _add_value(key, provider, _ValueType.STRING_ARRAY)


def add_boolean_array(key: str, provider: Callable[[], List[bool]]):
    _add_value(key, provider, _ValueType.BOOLEAN_ARRAY)
