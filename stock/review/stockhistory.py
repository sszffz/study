"""
get the stock history
"""
import os
import sys
from bisect import bisect_left, bisect_right
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
# import fix_yahoo_finance as yf
from yahoofinancials import YahooFinancials

from security.config import config
from stock.review.historyutils import datetime_to_str, str_to_datetime, get_delta_days
from stock.review.stockenum import ViewMode, HistoryDataFailureType, PriceType
from utils.log import log


class StockHistory:

    __DATE = "Date"

    # The earliest day to extract history if there is no record for a stock
    EARLIEST_HISTORY_DATE = "1980-01-01"

    # If no prices for the last n days, we still consider the extracting success
    __MAX_EMPTY_RECORD_DAYS = 14

    def __init__(self, symbol: str):
        self.__symbol: str = symbol
        self.__init_history()

    def __default_data_file_path(self) -> str:
        """
        get the default database file path
        :return:
        """
        file_name = self.symbol + ".csv"
        return os.path.join(config.path.stock_history_folder_path, file_name[0], file_name)

    def __init_history(self):
        """
        initialize history from a file.
        Until 02/08/2021, only csv file is supported
        If the file does not exist, we create one.
        :return:
        """
        self.__database_file_path: str = self.__default_data_file_path()
        if not os.path.isfile(self.__database_file_path):
            self.__log("history file does not exist. create an empty one")
            with open(self.__database_file_path, "w") as fp:
                fp.write("{},{},{},{},{},{},{}\n".format(self.__DATE,
                                                         str(PriceType.OPEN),
                                                         str(PriceType.HIGH),
                                                         str(PriceType.LOW),
                                                         str(PriceType.CLOSE),
                                                         str(PriceType.ADJ_CLOSE),
                                                         str(PriceType.VOLUME)))

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
        if self.__history is None or self.size == 0:
            return None

        return [self.date[0], self.date[self.size-1]]

    @property
    def last_record_date(self):
        """
        get last update date
        :return:
        """
        return None if self.date_range is None else self.date_range[1]

    def __get_state_date_for_update(self) -> str:
        """
        Get the next day for update. It checks the range. If the range does not
        exist, download from 1980-12-30
        :return:
        """
        if self.date_range is None:
            return "1980-12-30"

        last_date = str_to_datetime(self.date_range[1])
        update_date = last_date + timedelta(days=1)
        return datetime_to_str(update_date)

    def print(self):
        print(self.__history)

    def is_history_empty(self):
        """
        check whether history is empty
        :return:
        """
        return self.__history is None or self.__history.shape[0] == 0

    @staticmethod
    def __calc_rate(array: np.array) -> np.array:
        """
        Given a np array, calculate the increase/decrease
        :param array:
        :return:
        """
        if len(array) < 2:
            return np.array([])

        return (array[1:] - array[0:-1])/array[0:-1]

    def history(self, price_type: PriceType = PriceType.OPEN, view_mode: ViewMode = ViewMode.DAILY, start_date=None,
                end_date=None):
        """
        get the histogram for one column. The column data is processed based on
        how to average the past data

        :param price_type:
        :param view_mode:
        :param start_date:
        :param end_date:
        :return:
        """
        value = self.__history[str(price_type)]
        value = np.array(value)
        return self.__slice(value, view_mode, start_date, end_date)

    def history_rate(self, price_type: PriceType = PriceType.OPEN, view_mode: ViewMode = ViewMode.DAILY,
                     start_date=None, end_date=None):
        """
        get the rate change
        :param price_type:
        :param view_mode:
        :param start_date:
        :param end_date:
        :return:
        """
        return self.__calc_rate(self.history(price_type, view_mode, start_date, end_date))

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

        last_date = str_to_datetime(self.date_range[1])
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

    def __is_history_data_valid(self, history_data) -> HistoryDataFailureType:
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
        if history_data is None:
            return HistoryDataFailureType.NONE_DATA

        if not isinstance(history_data, dict):
            return HistoryDataFailureType.NOT_DICT_DATA

        if self.symbol not in history_data:
            return HistoryDataFailureType.NOT_INCLUDE_SYMBOL

        history_info = history_data[self.symbol]
        if history_info is None:
            return HistoryDataFailureType.NONE_HISTORY_INFO

        if "prices" not in history_info:
            return HistoryDataFailureType.NO_PRICES_ENTRY

        info_list = history_info["prices"]
        if info_list is None:
            return HistoryDataFailureType.NO_RECORD

        if not isinstance(info_list, list):
            return HistoryDataFailureType.NOT_LIST_RECORD

        if len(info_list) == 0:
            return HistoryDataFailureType.EMPTY_RECORD

        return HistoryDataFailureType.SUCCESS

    def __extract_history_data(self, history_data, update_database: bool = True, update_memory: bool = True):
        """
        format history data to a csv format
        :param history_data:
        :return:
        """
        entry_list = history_data[self.__symbol]["prices"]

        # we only update the history that are later than the last history record
        date_range = self.date_range
        if date_range is None:
            last_record_date = self.EARLIEST_HISTORY_DATE
        else:
            last_record_date = date_range[1]

        history_list = []
        for entry in entry_list:
            if entry["formatted_date"] <= last_record_date:
                continue

            history_list.append({StockHistory.__DATE: entry["formatted_date"],
                                 str(PriceType.OPEN): entry["open"],
                                 str(PriceType.CLOSE): entry["close"],
                                 str(PriceType.HIGH): entry["high"],
                                 str(PriceType.LOW): entry["low"],
                                 str(PriceType.ADJ_CLOSE): entry["adjclose"],
                                 str(PriceType.VOLUME): entry["volume"]})

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
            self.__log("Error: database file path is not specified")
            return

        if not os.path.isfile(self.__database_file_path):
            self.__log("Error: database file - {} - does not exist".format(self.__database_file_path))
            return

        if history is None or len(history) == 0:
            self.__log("Info: no history data is retrieved.")
            return

        with open(self.__database_file_path, "a") as fp:
            for entry in history:
                fp.write("{},{},{},{},{},{},{}\n".format(entry[self.__DATE],
                                                         entry[str(PriceType.OPEN)],
                                                         entry[str(PriceType.HIGH)],
                                                         entry[str(PriceType.LOW)],
                                                         entry[str(PriceType.CLOSE)],
                                                         entry[str(PriceType.ADJ_CLOSE)],
                                                         entry[str(PriceType.VOLUME)]))

        self.__log("Info: the record in database was updated from {} to {}".format(history[0][self.__DATE],
                                                                                   history[-1][self.__DATE]))

    def __update_history(self, history):
        """
        update history in memory
        :param history:
        :return:
        """
        if history:
            self.__history = self.__history.append(history, ignore_index=True)

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

    # noinspection PyBroadException
    def update(self, update_database: bool = True, update_memory: bool = True) -> HistoryDataFailureType:
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
            self.__log("Info: already update-to-date")
            return HistoryDataFailureType.SUCCESS

        try:
            self.__log("Info: downloading")
            start_date = self.__get_state_date_for_update()
            end_date = datetime_to_str(datetime.now())
            financial = YahooFinancials(self.symbol)
            history_data = financial.get_historical_price_data(start_date, end_date, "daily")
            return self.update_history_from_server_data(history_data, start_date, end_date, update_database,
                                                        update_memory)
        except:
            e = sys.exc_info()[0]
            self.__log("Error: {}".format(str(e)))
            return HistoryDataFailureType.UNSPECIFIED

    def update_history_from_server_data(self, history_data, start_date: str, end_date: str,
                                        update_database: bool = True,
                                        update_memory: bool = True) -> HistoryDataFailureType:
        """
        Given the data acquired from server, update history
        :param update_memory:
        :param update_database:
        :param end_date:
        :param start_date:
        :param history_data:
        :return:
        """
        delta_days = get_delta_days(start_date, end_date)

        failure_type = self.__is_history_data_valid(history_data)
        if failure_type != HistoryDataFailureType.SUCCESS:
            if failure_type == HistoryDataFailureType.EMPTY_RECORD and \
                    delta_days < self.__MAX_EMPTY_RECORD_DAYS:
                # if there is no record for two weeks, we still consider it is
                # a successful extraction with regard to holiday and weekends
                self.__log("no prices for {} days, less than the threshold {}. "
                           "still success".format(delta_days,
                                                  self.__MAX_EMPTY_RECORD_DAYS))
                return HistoryDataFailureType.SUCCESS
            else:
                self.__log("Warn: fail to extract history data due to " + str(failure_type))
                return failure_type

        if self.__has_splits(history_data):
            # if there is a split, get all history again
            self.__log("Info: split occurs during updating. back up old history and rebuild database")
            financial = YahooFinancials(self.symbol)
            history_data = financial.get_historical_price_data(self.EARLIEST_HISTORY_DATE,
                                                               datetime_to_str(datetime.now()),
                                                               "daily")
            del self.__history
            self.__back_database_file()
            self.__init_history()
            self.__extract_history_data(history_data, update_database, update_memory)
        else:
            self.__extract_history_data(history_data, update_database, update_memory)

        return HistoryDataFailureType.SUCCESS

    def __log(self, info: str):
        """
        log information
        :param info:
        :return:
        """
        log("{}: {}".format(self.symbol, info))
