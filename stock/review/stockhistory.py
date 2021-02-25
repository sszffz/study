"""
get the stock history
"""
import os
from bisect import bisect_left, bisect_right
from datetime import datetime, timedelta
from typing import List

import numpy as np
import pandas as pd
# import fix_yahoo_finance as yf
from yahoofinancials import YahooFinancials

from security.config import config
from stock.review.stockenum import ViewMode
from utils.log import log


class StockHistory:

    __DATE = "Date"
    __OPEN = "Open"
    __HIGH = "High"
    __LOW = "Low"
    __CLOSE = "Close"
    __ADJ_CLOSE = "Adj Close"
    __VOLUME = "Volume"

    __EARLIEST_HISTORY_DATE = "1980-01-01"

    def __init__(self, symbol: str):
        self.__symbol: str = symbol
        self.__init_history()

    def __default_data_file_path(self) -> str:
        """
        get the default database file path
        :return:
        """
        file_name = self.symbol + ".csv"
        return os.path.join(config.path.stock_history_folder_path, file_name)

    def __init_history(self):
        """
        initialize history from a file.
        Until 02/08/2021, only csv file is supported
        If the file does not exist, we create one.
        :return:
        """
        self.__database_file_path: str = self.__default_data_file_path()
        if not os.path.isfile(self.__database_file_path):
            log("history file does not exist for {}. create an empty one".format(self.symbol))
            with open(self.__database_file_path, "w") as fp:
                fp.write("{},{},{},{},{},{},{}\n".format(self.__DATE,
                                                         self.__OPEN,
                                                         self.__HIGH,
                                                         self.__LOW,
                                                         self.__CLOSE,
                                                         self.__ADJ_CLOSE,
                                                         self.__VOLUME))

        self.__history: pd.DataFrame = pd.read_csv(self.__database_file_path)

    @property
    def size(self):
        """
        return the recode of history. The number of trading days in history
        :return:
        """
        if self.__history is None:
            return 0

        return self.__history.shape[0]

    @property
    def symbol(self):
        """
        return the code
        :return:
        """
        return self.__symbol

    @property
    def date(self):
        """
        list the all data
        :return:
        """
        if self.is_history_empty():
            return None

        return self.__history[self.__DATE]

    @property
    def date_range(self):
        """
        Get the history range
        :return:
        """
        if self.__history is None:
            return None

        return [self.date[0], self.date[self.size-1]]

    def __get_state_date_for_update(self) -> str:
        """
        Get the next day for update. It checks the range. If the range does not
        exist, download from 1980-12-30
        :return:
        """
        if self.date_range is None:
            return "1980-12-30"

        last_date = self.str_to_datetime(self.date_range[1])
        update_date = last_date + timedelta(days=1)
        return self.datetime_to_str(update_date)

    @staticmethod
    def datetime_to_str(time):
        """
        convert a date time to string
        :param time:
        :return:
        """
        return time.strftime("%Y-%m-%d")

    @staticmethod
    def str_to_datetime(time: str):
        """
        convert a string to a datetime. The format of the string is like "1980-12-30"
        :param time:
        :return:
        """
        return datetime.strptime(time, "%Y-%m-%d")

    def print(self):
        print(self.__history)

    def is_history_empty(self):
        """
        check whether history is empty
        :return:
        """
        return self.__history is None or self.__history.shape[0] == 0

    def __history_column(self, column: str, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        """
        get the histogram for one column. The column data is processed based on
        how to average the past data

        :param column:
        :param view_mode:
        :param start_date:
        :param end_date:
        :return:
        """
        value = self.__history[column]
        value = np.array(value)
        return self.__slice(value, view_mode, start_date, end_date)

    def open(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        """
        Get the history of open value in a trading day
        :param view_mode:
        :param start_date:
        :param end_date:
        :return:
        """
        return self.__history_column(self.__OPEN, view_mode, start_date, end_date)

    def close(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        """
        Get the history of close value in a trading day
        :param view_mode:
        :param start_date:
        :param end_date:
        :return:
        """
        return self.__history_column(self.__CLOSE, view_mode, start_date, end_date)

    def high(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        """
        Get the history of the highest value in a trading day
        :param view_mode:
        :param start_date:
        :param end_date:
        :return:
        """
        return self.__history_column(self.__HIGH, view_mode, start_date, end_date)

    def low(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        """
        Get the history of the lowest value in a trading day
        :param view_mode:
        :param start_date:
        :param end_date:
        :return:
        """
        return self.__history_column(self.__LOW, view_mode, start_date, end_date)

    def adj_close(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        """
        Get the history of adjusted close value in a trading day
        :param view_mode:
        :param start_date:
        :param end_date:
        :return:
        """
        return self.__history_column(self.__ADJ_CLOSE, view_mode, start_date, end_date)

    def volume(self, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        """
        Get the history of volume in a trading day
        :param view_mode:
        :param start_date:
        :param end_date:
        :return:
        """
        return self.__history_column(self.__VOLUME, view_mode, start_date, end_date)

    def __slice(self, value, view_mode: ViewMode = ViewMode.DAILY, start_date=None, end_date=None):
        """
        Slice the input data based on input start date and end date.
        If start date is not specified, the start date is from the earliest day.
        If end date is not specified, the end date is the last day in database.
        :param value:
        :param view_mode:
        :param start_date:
        :param end_date:
        :return:
        """
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
        """
        slice value on daily base
        :param value:
        :param start_date:
        :param end_date:
        :return:
        """
        start_index = 0
        end_index = self.size
        if start_date is not None:
            start_index = bisect_left(self.date, start_date)
        if end_date is not None:
            end_index = bisect_right(self.date, end_date)
        return value[start_index:end_index]

    def __slice_avg(self, value, num_avg_day: int, start_date=None, end_date=None):
        """
        slice value on average
        :param value:
        :param num_avg_day:
        :param start_date:
        :param end_date:
        :return:
        """
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
        """
        Slice value on weekly base. It calculates the averaged value in the last five days
        :param value:
        :param start_date:
        :param end_date:
        :return:
        """
        return self.__slice_avg(value, 5, start_date, end_date)

    def __slice_monthly(self, value, start_date=None, end_date=None):
        """
        Slice value on monthly base. It calculates the averaged value in the last twenty days
        :param value:
        :param start_date:
        :param end_date:
        :return:
        """
        return self.__slice_avg(value, 20, start_date, end_date)

    def __slice_yearly(self, value, start_date=None, end_date=None):
        raise Exception("unimplemented yet")

    def is_update_to_date(self):
        """
        Check whether the history is update to date
        :return:
        """
        if self.date_range is None:
            return False

        last_date = self.str_to_datetime(self.date_range[1])
        curr_date = datetime.now()
        time_delta = curr_date - last_date
        return time_delta.days <= 1

    def __has_splits(self, history_data):
        """
        check whether there is splits during the history data
        The format of splits is
         'splits': {'2020-08-31': {'date': 1598880600,
                   'numerator': 4,
                   'denominator': 1,
                   'splitRatio': '4:1',
                   'formatted_date': '2020-08-31'}}}

        :param history_data:
        :return:
        """
        history_info = history_data[self.symbol]
        if "eventsData" in history_info:
            events_data = history_info["eventsData"]
            if events_data is not None and "splits" in events_data:
                splits = events_data["splits"]
                if splits:
                    for split in splits.values():
                        if split is not None and "numerator" in split and "denominator" in split:
                            if split["numerator"] != 1 or split["denominator"] != 1:
                                return True

        return False

    def __is_history_data_valid(self, history_data):
        """
        Check whether download history data is valid
        the format of history data is like the follows:
        history_data: {code : info}
            info:  {'eventsData': event,
                    'firstTradeDate': firstTradeDate,
                    'currency': currency,
                    'instrumentType': instrumentType,
                    'timeZone': timeZone,
                    'prices': prices}

                prices: list of dictionary
                    [data1, data2, ..., datan]
                    Example of one data
                     {'date': 1600056000,
                      'high': 115.93000030517578,
                      'low': 112.80000305175781,
                      'open': 114.72000122070312,
                      'close': 115.36000061035156,
                      'volume': 140150100,
                      'adjclose': 114.98948669433594,
                      'formatted_date': '2020-09-14'}]

        :param history_data:
        :return:
        """
        if history_data is None or \
                not isinstance(history_data, dict) or \
                self.symbol not in history_data:
            return False

        history_info = history_data[self.symbol]
        if history_info is None or \
                "prices" not in history_info:
            return False

        info_list = history_info["prices"]
        if info_list is None or \
                not isinstance(info_list, list) or \
                len(info_list) == 0:
            return False

        return True

    def __extract_history_data(self, history_data, update_database: bool = True, update_memory: bool = True):
        """
        format history data to a csv format
        :param history_data:
        :return:
        """
        entry_list = history_data[self.__symbol]["prices"]

        history_list = []
        for entry in entry_list:
            history_list.append({StockHistory.__DATE: entry["formatted_date"],
                                 StockHistory.__OPEN: entry["open"],
                                 StockHistory.__CLOSE: entry["close"],
                                 StockHistory.__HIGH: entry["high"],
                                 StockHistory.__LOW: entry["low"],
                                 StockHistory.__ADJ_CLOSE: entry["adjclose"],
                                 StockHistory.__VOLUME: entry["volume"]})

        if update_database:
            self.__update_database(history_list)

        if update_memory:
            self.__update_history(history_list)

    def __update_database(self, history):
        """
        update data history
        :param history:
        :return:
        """
        if self.__database_file_path is None:
            self.log("Error: database file path is not specified")
            return

        if not os.path.isfile(self.__database_file_path):
            self.log("Error: database file - {} - does not exist".format(self.__database_file_path))
            return

        if history is None or len(history) == 0:
            self.log("Info: no history data is retrieved.")
            return

        with open(self.__database_file_path, "a") as fp:
            for entry in history:
                fp.write("{},{},{},{},{},{},{}\n".format(entry[self.__DATE],
                                                         entry[self.__OPEN],
                                                         entry[self.__HIGH],
                                                         entry[self.__LOW],
                                                         entry[self.__CLOSE],
                                                         entry[self.__ADJ_CLOSE],
                                                         entry[self.__VOLUME]))

        self.log("Info: the record in database was updated from {} to {}".format(history[0][self.__DATE],
                                                                                 history[-1][self.__DATE]))

    def __update_history(self, history):
        """
        update history in memory
        :param history:
        :return:
        """
        old_history = self.__history
        self.__history = self.__history.append(history, ignore_index=True)
        del old_history

    def __back_database_file(self):
        """
        backup current database file
        :return:
        """
        if not os.path.isfile(self.__database_file_path):
            return

        index = 0
        while True:
            dst_file = self.__database_file_path + "_" + str(index)
            if not os.path.isfile(dst_file):
                break
            index = index + 1

        os.rename(self.__database_file_path, dst_file)

    def update(self, update_database: bool = True, update_memory: bool = True):
        """
        update the database to update-to-date.
        The supported time interval for download is "daily", "weekly", "monthly"
        :param update_database:
            update database file
        :param update_memory:
            update history in memory
        :return:
        """
        if self.is_update_to_date():
            self.log("Info: already update-to-date")
            return

        self.log("Info: downloading")
        start_date = self.__get_state_date_for_update()
        end_date = self.datetime_to_str(datetime.now())
        financial = YahooFinancials(self.symbol)
        history_data = financial.get_historical_price_data(start_date, end_date, "daily")

        if not self.__is_history_data_valid(history_data):
            self.log("Warn: fail to extract history data")
            return

        if self.__has_splits(history_data):
            self.log("Info: split occurs during updating. back up old history and rebuild database")
            history_data = financial.get_historical_price_data(self.__EARLIEST_HISTORY_DATE,
                                                               self.datetime_to_str(datetime.now()),
                                                               "daily")
            del self.__history
            self.__back_database_file()
            self.__init_history()
            self.__extract_history_data(history_data, update_database, update_memory)
        else:
            self.__extract_history_data(history_data, update_database, update_memory)

    def log(self, info: str):
        """
        log information
        :param info:
        :return:
        """
        log("{}: {}".format(self.symbol, info))