"""
Utilities for history of stocks
"""
import os

from security.config import config


def get_stock_history_file_path(code: str) -> str:
    """
    get the file path for a specified code
    :param code:
    :return:
    """
    database_path = config.path.stock_history_folder_path
    if not database_path or not os.path.isdir(database_path):
        raise Exception("database path does not exist")

    stock_file_name = code + ".csv"
    stock_file_path = os.path.join(database_path, stock_file_name)
    if os.path.isfile(stock_file_path):
        stock_file_name = None

    return stock_file_name


def has_stock(code: str) -> bool:
    """
    check whether there is history for specified stock. It checks the database
    and get the corresponding file.
    :param code:
    :return:
    """
    stock_file_path = get_stock_history_file_path()
    return stock_file_path is not None


def get_stock_history(code: str):
    """
    get all history for a specified stock
    :param code:
    :return:
    """
    stock_file_path = get_stock_history_file_path()