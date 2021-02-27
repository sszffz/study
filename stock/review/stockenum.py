"""
enum type for stock
"""
from enum import Enum


class ViewMode(Enum):
    """
    View mode for history data.
    For example: Daily means get the daily history data.
    """
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    YEARLY = 4
    AVERAGE_FIVE = 5
    AVERAGE_TEN = 6
    AVERAGE_TWENTY = 7


class HistoryDataFailureType(Enum):
    """
    Failure type when extract history type
    """
    SUCCESS = (0, "Success")
    NONE_DATA = (1, "None data")
    NOT_DICT_DATA = (2, "Not dict data")
    NOT_INCLUDE_SYMBOL = (3, "symbol is not in dict")
    NONE_HISTORY_INFO = (4, "no history information")
    NO_PRICES_ENTRY = (5, "no price entry")
    NO_RECORD = (6, "records are None")
    NOT_LIST_RECORD = (7, "records are not a list")
    EMPTY_RECORD = (8, "empty record")
    UNSPECIFIED = (9, "unspecified error")

    def __str__(self):
        return self.value[1]


