"""
manage all stocks
"""
import abc

import urllib.request
from concurrent import futures
from datetime import datetime
from typing import List

from yahoofinancials import YahooFinancials

from stock.review.historyutils import datetime_to_str, increase_datetime
from stock.review.stockenum import HistoryDataFailureType
from stock.review.stockhistory import StockHistory
from utils.log import log
from utils.misc.miscutils import split_list


class StockManager:

    __metaclass__ = abc.ABCMeta

    _SYMBOL = "Symbol"
    _TICKER = "Ticker"
    _NAME = "Name"
    _LAST_SALE = "LastSale"
    _MARKET_CAP = "MarketCap"
    _ADR_TSO = "ADRTSO"
    _IPO_YEAR = "IPOyear"
    _SECTOR = "Sector"
    _INDUSTRY = "Industry"
    _SUMMARY_QUOTA = "SummaryQuote"
    _STATE = "State"
    _EXCHANGE = "Exchange"
    _EXCHANGE_DISPLAY = "ExchangeDisplay"
    _TYPE = "Type"
    _TYPE_DISPLAY = "TypeDisplay"
    _HISTORY_START_DATE = "HistoryStartDate"
    _HISTORY_END_DATE = "HistoryEndDate"

    __INVALID_FILE_NAME = {"CON", "PRN", "NULL"}

    # if fail more than five times, we may set the stock inactive
    __MAX_ATTEMPTS_NUM = 1

    # if fail to get the record for the past 14 days, we may set the stock inactive
    __MAX_INACTIVE_DAYS = 14

    __DELIMITER: str = ","

    # After every 200 stocks, we check the server is accessible
    __SERVER_TEST_FREQ = 200

    def __init__(self):
        super().__init__()

    @property
    @abc.abstractmethod
    def company_size(self) -> int:
        """
        Get the number of company in the database
        """
        raise NotImplementedError("Implement it in concrete class")

    @property
    @abc.abstractmethod
    def sectors(self) -> set:
        """
        Get all sectors in the database
        """
        raise NotImplementedError("Implement it in concrete class")

    @property
    @abc.abstractmethod
    def industries(self) -> set:
        """
        Get all industries in the database
        """
        raise NotImplementedError("Implement it in concrete class")

    @property
    @abc.abstractmethod
    def symbols(self) -> set:
        """
        get all symbols
        """
        raise NotImplementedError("Implement it in concrete class")

    @abc.abstractmethod
    def update_attempts(self, symbol: str, attempts: int, update_date: str, date_range: [List, None]):
        """
        update attempts and the update date
        :param date_range:
        :param symbol:
        :param attempts:
        :param update_date:
        :return:
        """
        raise NotImplementedError("Implement it in concrete class")

    @abc.abstractmethod
    def increase_attempts(self, symbol: str, date_range: [List, None]):
        """
        Increase the attempts by 1.
        :return:
        """
        raise NotImplementedError("Implement it in concrete class")

    def is_active(self, symbol: str) -> bool:
        """
        test whether a stock is still active or not
        """
        attempts = self._get_attempts(symbol)
        return attempts is None or attempts < self.__MAX_ATTEMPTS_NUM

    @abc.abstractmethod
    def _get_attempts(self, symbol: str):
        """
        get attempts
        :param symbol:
        :return:
        """
        raise NotImplementedError("Implement it in concrete class")

    def _is_valid_symbol(self, symbol: str) -> bool:
        """
        if symbol cannot be used as a file name, the symbol is invalid
        :param symbol:
        :return:
        """
        return symbol not in self.__INVALID_FILE_NAME

    @staticmethod
    def is_server_accessible():
        """
        Check whether financial server is accessible
        :return:
        """
        return urllib.request.urlopen("https://finance.yahoo.com/quote/AAPL").getcode() == 200

    def _handle_after_update_all(self):
        """
        post process after update all history. Default do nothing
        :return:
        """
        pass

    def _handle_after_update_batch(self):
        """
        post process after update a batch of stock. Default do nothing
        :return:
        """
        pass

    def update_all_history(self, update_database: bool = True, update_memory: bool = True,
                           update_inactive: bool = False, batch_size: int = 100):
        """
        update all history
        :param update_database:
        :param update_memory:
        :param update_inactive:
        :param batch_size:
        :return:
        """
        if not self.is_server_accessible():
            print("server is not accessible")
            return

        stock_num = self.company_size
        symbol_list = []
        for index, symbol in enumerate(self.symbols):
            log("Info: updating the history for {} {}/{}".format(symbol, index+1, stock_num))

            if not update_inactive and not self.is_active(symbol):
                continue

            if not self._is_valid_symbol(symbol):
                continue

            if not update_inactive and not self.is_active(symbol):
                continue

            symbol_list.append(symbol)

        with futures.ThreadPoolExecutor(max_workers=20) as executor:
            to_do = []
            for batch in split_list(symbol_list, batch_size):
                to_do.append(executor.submit(self.acquire_history_from_server, batch))

            completed_counter = 0
            for future in futures.as_completed(to_do):
                result = future.result()
                if result is not None:
                    symbol_batch, history_data, history_map, start_date, end_date = result
                    self._update_database_for_batch(symbol_batch, history_data, history_map, start_date, end_date,
                                                    update_database, update_memory)
                    self._handle_after_update_batch()
                    completed_counter += len(symbol_batch)
                    print("complete: ", completed_counter)

        self._handle_after_update_all()

    def _update_database_for_batch(self, symbol_batch, history_data, history_map, start_date, end_date,
                                   update_database, update_memory):
        """
        update database for a batch from history data acquired from server.
        It will update mySQL server and stock history data file (cvs files)
        :return:
        """
        for symbol in symbol_batch:
            history = history_map[symbol]
            failure_type = history.update_history_from_server_data(history_data, start_date, end_date,
                                                                   update_database, update_memory)
            if failure_type == HistoryDataFailureType.SUCCESS:
                self.update_attempts(symbol, 0, datetime_to_str(datetime.now()), history.date_range)
            else:
                self.increase_attempts(symbol, history.date_range)

    # def update_all_history(self, update_database: bool = True, update_memory: bool = True,
    #                        update_inactive: bool = False, batch_size: int = 100):
    #     """
    #     update all history
    #     :param batch_size:
    #     :param update_database:
    #     :param update_memory:
    #     :param update_inactive:
    #         whether update inactive stocks
    #     :return:
    #     """
    #     stock_num = self.company_size
    #     symbol_batch = []
    #     for index, symbol in enumerate(self.symbols):
    #         log("Info: updating the history for {} {}/{}".format(symbol, index+1, stock_num))
    #
    #         if not update_inactive and not self.is_active(symbol):
    #             continue
    #
    #         if not self._is_valid_symbol(symbol):
    #             continue
    #
    #         if not update_inactive and not self.is_active(symbol):
    #             continue
    #
    #         # test whether server is accessible. if not, quit
    #         test_accessible = (index % self.__SERVER_TEST_FREQ == 0)
    #         if test_accessible and not self.is_server_accessible():
    #             log("Warn: Server is not accessible. Stop updating")
    #             continue
    #
    #         symbol_batch.append(symbol)
    #         if len(symbol_batch) >= batch_size:
    #             self._update_batch_history(symbol_batch, update_database, update_memory)
    #             self._handle_after_update_batch()
    #             symbol_batch.clear()
    #
    #     if symbol_batch:
    #         self._update_batch_history(symbol_batch, update_database, update_memory)
    #         self._handle_after_update_batch()
    #
    #     self._handle_after_update_all()
    #

    def acquire_history_from_server(self, symbol_batch: List[str]):
        """
        update the history for a batch of symbols
        :param symbol_batch:
        :return:
        """
        history_map = dict()
        end_date = datetime_to_str(datetime.now())
        start_date = end_date
        for symbol in symbol_batch:
            history = StockHistory(symbol)
            history_map[symbol] = history
            date_range = history.date_range
            if date_range is None:
                new_start_date = StockHistory.EARLIEST_HISTORY_DATE
            else:
                new_start_date = increase_datetime(date_range[1], 1)

            if new_start_date < start_date:
                start_date = new_start_date

        if start_date >= end_date:
            log("cannot update because it is too short from last update")
            return

        financial = YahooFinancials(symbol_batch)
        history_data = financial.get_historical_price_data(start_date, end_date, "daily")

        return symbol_batch, history_data, history_map, start_date, end_date
