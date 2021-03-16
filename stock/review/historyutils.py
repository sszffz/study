"""
Utilities for history of stocks
"""
import os
from datetime import datetime, timedelta
from shutil import copyfile


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


def increase_datetime(date_str: str, days: int) -> str:
    """
    Increase the given dates by a number of days
    :param date_str:
    :param days:
    :return:
    """
    old_date = str_to_datetime(date_str)
    new_date = old_date + timedelta(days=days)
    return datetime_to_str(new_date)


def reorganize_history_files(root_path: str):
    """
    reorganize history file to avoid that there are two many files in one folder.
    :param root_path:
    :return:
    """
    first_letter_set = [file_name[0] for file_name in os.listdir(root_path)]
    for first_letter in first_letter_set:
        dst_path = os.path.join(root_path, first_letter)
        if not os.path.isdir(dst_path):
            os.mkdir(dst_path)

    for file_name in os.listdir(root_path):
        file_path = os.path.join(root_path, file_name)
        if not os.path.isfile(file_path):
            continue

        dst_path = os.path.join(root_path, file_name[0], file_name)
        copyfile(file_path, dst_path)

