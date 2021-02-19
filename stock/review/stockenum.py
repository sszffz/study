"""
enum type for stock
"""
from enum import Enum


class ViewMode(Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    YEARLY = 4
    AVERAGE_FIVE = 5
    AVERAGE_TEN = 6
    AVERAGE_TWENTY = 7
