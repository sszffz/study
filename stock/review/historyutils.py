"""
Utilities for history of stocks
"""
import os
from datetime import datetime


def str_to_datetime(time: str):
    """
    convert a string to a datetime. The format of the string is like "1980-12-30"
    :param time:
    :return:
    """
    return datetime.strptime(time, "%Y-%m-%d")


def datetime_to_str(time):
    """
    convert a date time to string
    :param time:
    :return:
    """
    return time.strftime("%Y-%m-%d")


def get_delta_days(start_date: str, end_date: str) -> int:
    """
    count how many days from start date to end date
    :param start_date:
    :param end_date:
    :return:
    """
    start = str_to_datetime(start_date)
    end = str_to_datetime(end_date)
    delta = (end - start)
    return delta.days
