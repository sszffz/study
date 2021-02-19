"""
get the stock history
"""
import os
from bisect import bisect_left, bisect_right
from typing import List

import numpy as np
import pandas as pd

from stock.review.stockenum import ViewMode


class StockHistory:

    def __init__(self, code: str, *args, **kwargs):
        self.__code: str = code
        self.__history: pd.DataFrame = pd.DataFrame()
        self.__init_history(**kwargs)

    def __init_history(self, **kwargs):
        if "from_file" in kwargs:
            self.__init_history_from_file(kwargs["from_file"])

    def __init_history_from_file(self, file_path: str):
        """
        initialize history from a file.
        Until 02/08/2021, only csv file is supported
        :param file_path:
        :return:
        """
        self.load_from_csv_file(file_path)

    def load_from_csv_file(self, file_path: str):
        """
        load history from a csv file
        :param file_path:
        :return:
        """
        if file_path is None or not os.path.isfile(file_path):
            raise Exception("Input file is empty")

        if not file_path.endswith(".csv"):
            raise Exception("Invalid history file: " + file_path)

        self.__history = pd.read_csv(file_path)

    @property
    def size(self):
        if self.__history is None:
            return 0

        return self.__history.shape[0]

    @property
    def code(self):
        return self.__code

    def print(self):
        print(self.__history)

    def is_history_empty(self):
        """
        check whether history is empty
        :return:
        """
        return self.__history is None

    def __history_column(self, column: str, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        value = self.__history[column]
        value = np.array(value)
        return self.__slice(value, view_mode, start_date, end_date)

    def open(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        return self.__history_column("Open", view_mode, start_date, end_date)

    def close(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        return self.__history_column("Close", view_mode, start_date, end_date)

    def high(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        return self.__history_column("High", view_mode, start_date, end_date)

    def low(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        return self.__history_column("Low", view_mode, start_date, end_date)

    def adj_close(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        return self.__history_column("Adj Close", view_mode, start_date, end_date)

    def volume(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        return self.__history_column("Volume", view_mode, start_date, end_date)

    def __slice(self, value, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        if view_mode == ViewMode.DAILY:
            return self.__slice_daily(value, start_date, end_date)
        elif view_mode == ViewMode.WEEKLY:
            return self.__slice_weekly(value, start_date, end_date)
        elif view_mode == ViewMode.MONTHLY:
            return self.__slice_monthly(value, start_date, end_date)
        elif view_mode == ViewMode.YEARLY:
            return self.__slice_yearly(value, start_date, end_date)
        elif view_mode == ViewMode.AVERAGE_FIVE:
            return self.__slice_avg(value, 5, start_date, end_date)
        elif view_mode == ViewMode.AVERAGE_TEN:
            return self.__slice_avg(value, 10, start_date, end_date)
        elif view_mode == ViewMode.AVERAGE_TWENTY:
            return self.__slice_avg(value, 20, start_date, end_date)
        else:
            raise Exception("Un-support slice way: " + str(view_mode))

    def __slice_daily(self, value, start_date=None, end_date=None):
        start_index = 0
        end_index = self.size
        if start_date is not None:
            start_index = bisect_left(self.date, start_date)
        if end_date is not None:
            end_index = bisect_right(self.date, end_date)
        return value[start_index:end_index]

    def __slice_avg(self, value, num_avg_day: int, start_date=None, end_date=None):
        start_index = 0
        end_index = self.size
        if start_date is not None:
            start_index = bisect_left(self.date, start_date)
        if end_date is not None:
            end_index = bisect_right(self.date, end_date)

        num = end_index - start_index
        avg = np.zeros(num)

        sum_value = np.add.accumulate(value)

        prev_index = start_index - num_avg_day
        if prev_index <= 0:
            heading_num = -prev_index
            for i in range(heading_num):
                avg[i] = sum_value[start_index + i]/(start_index + i + 1)
            for i in range(heading_num, num):
                avg[i] = (sum_value[start_index + i] - sum_value[start_index + i - num_avg_day])/num_avg_day
        else:
            for i in range(num):
                avg[i] = (sum_value[start_index + i] - sum_value[start_index + i - num_avg_day])/num_avg_day

        return avg

    def __slice_weekly(self, value, start_date=None, end_date=None):
        return self.__slice_avg(value, 5, start_date, end_date)

    def __slice_monthly(self, value, start_date=None, end_date=None):
        return self.__slice_avg(value, 20, start_date, end_date)

    def __slice_yearly(self, value, start_date=None, end_date=None):
        raise Exception("unimplemented yet")

    @property
    def date(self):
        return self.__history["Date"]

