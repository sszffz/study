"""
manage all stocks
"""
import abc

import urllib.request


class StockManager:

    __metaclass__ = abc.ABCMeta

    __SYMBOL = "Symbol"
    __NAME = "Name"
    __LAST_SALE = "LastSale"
    __MARKET_CAP = "MarketCap"
    __ADR_TSO = "ADR TSO"
    __IOP_YEAR = "IPOyear"
    __SECTOR = "Sector"
    __INDUSTRY = "Industry"
    __SUMMARY_QUOTA = "Summary Quote"
    __STATE = "State"

    # __INVALID_FILE_NAME = {"CON", "PRN", "NULL"}

    # if fail more than five times, we may set the stock inactive
    __MAX_ATTEMPTS_NUM = 5

    # if fail to get the record for the past 14 days, we may set the stock inactive
    __MAX_INACTIVE_DAYS = 14

    __DELIMITER: str = ","

    # After every 20 stocks, we check the server is accessible
    __SERVER_TEST_FREQ = 20

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    @property
    def company_size(self) -> int:
        """
        Get the number of company in the database
        """

    @abc.abstractmethod
    @property
    def sectors(self) -> set:
        """
        Get all sectors in the database
        """

    @abc.abstractmethod
    @property
    def industries(self) -> set:
        """
        Get all industries in the database
        """

    @abc.abstractmethod
    @property
    def symbols(self) -> set:
        """
        get all symbols
        """

    @abc.abstractmethod
    def is_active(self, symbol: str) -> bool:
        """
        test whether a stock is still active or not
        """

    @staticmethod
    def is_server_accessible():
        """
        Check whether financial server is accessible
        :return:
        """
        return urllib.request.urlopen("https://finance.yahoo.com/quote/AAPL").getcode() == 200

    @abc.abstractmethod
    def update_all_history(self, update_database: bool = True, update_memory: bool = False,
                           update_inactive: bool = False):
        """
        update all history
        :param update_database:
        :param update_memory:
        :param update_inactive:
            whether update inactive stocks
        """
