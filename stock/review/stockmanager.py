"""
manage all stocks
"""
import abc

import urllib.request
from datetime import datetime

from stock.review.historyutils import datetime_to_str
from stock.review.stockenum import HistoryDataFailureType
from stock.review.stockhistory import StockHistory
from utils.log import log


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

    __INVALID_FILE_NAME = {"CON", "PRN", "NULL"}

    # if fail more than five times, we may set the stock inactive
    __MAX_ATTEMPTS_NUM = 5

    # if fail to get the record for the past 14 days, we may set the stock inactive
    __MAX_INACTIVE_DAYS = 14

    __DELIMITER: str = ","

    # After every 20 stocks, we check the server is accessible
    __SERVER_TEST_FREQ = 20

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
    def update_attempts(self, symbol: str, attempts: int, update_date: str):
        """
        update attempts and the update date
        :param symbol:
        :param attempts:
        :param update_date:
        :return:
        """
        raise NotImplementedError("Implement it in concrete class")

    @abc.abstractmethod
    def increase_attempts(self, symbol: str):
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

    def update_all_history(self, update_database: bool = True, update_memory: bool = False,
                           update_inactive: bool = False, batch_size: int = 100):
        """
        update all history
        :param batch_size:
        :param update_database:
        :param update_memory:
        :param update_inactive:
            whether update inactive stocks
        :return:
        """
        stock_num = self.company_size
        for index, symbol in enumerate(self.symbols):
            log("Info: updating the history for {} {}/{}".format(symbol, index+1, stock_num))

            if (index+1) % batch_size == 0:
                self._handle_after_update_batch()

            if not update_inactive and not self.is_active(symbol):
                continue

            if not self._is_valid_symbol(symbol):
                continue

            if not update_inactive and not self.is_active(symbol):
                continue

            # test whether server is accessible. if not, quit
            test_accessible = (index % self.__SERVER_TEST_FREQ == 0)
            failure_type = self.__update_individual(symbol, update_database, update_memory, test_accessible)
            if failure_type == HistoryDataFailureType.SUCCESS:
                self.update_attempts(symbol, 0, datetime_to_str(datetime.now()))
            else:
                self.increase_attempts(symbol)

        self._handle_after_update_all()

    def __update_individual(self, symbol: str, update_database: bool = True, update_memory: bool = False,
                            test_access: bool = False) -> HistoryDataFailureType:
        """
        update the history for
        :param update_memory:
        :param update_database:
        :param test_access:
        :param symbol:
        :return:
        """
        # test whether server is accessible. if not, quit
        if test_access and not self.is_server_accessible():
            log("Warn: Server is not accessible. Stop updating")
            return HistoryDataFailureType.INTERNET_NOT_ACCESSIBLE

        history = StockHistory(symbol)
        return history.update(update_database, update_memory)
