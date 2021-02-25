"""
manage all stocks
"""
import os

import pandas as pd

from security.config import config
from stock.review.stockhistory import StockHistory


class StockManager:

    __SYMBOL = "Symbol"
    __NAME = "Name"
    __LAST_SALE = "LastSale"
    __MARKET_CAP = "MarketCap"
    __ADR_TSO = "ADR TSO"
    __IOP_YEAR = "IPOyear"
    __SECTOR = "Sector"
    __INDUSTRY = "Industry"
    __SUMMARY_QUOTA = "Summary Quote"

    def __init__(self):
        self.__init_company_list()

    def __init_company_list(self):
        """
        initialize the company list from a csv file. It the file does not exist,
        create an empty one.
        :return:
        """
        self.__company_list_file_path: str = config.path.company_list_file_path
        if not os.path.isfile(self.__company_list_file_path):
            print("company list file does not exist. create an empty one")
            with open(self.__company_list_file_path, "w") as fp:
                fp.write("{},{},{},{},{},{},{},{},{}\n".format(self.__SYMBOL,
                                                               self.__NAME,
                                                               self.__LAST_SALE,
                                                               self.__MARKET_CAP,
                                                               self.__ADR_TSO,
                                                               self.__IOP_YEAR,
                                                               self.__SECTOR,
                                                               self.__INDUSTRY,
                                                               self.__SUMMARY_QUOTA))

        self.__company_list: pd.DataFrame = pd.read_csv(self.__company_list_file_path)

    @property
    def company_size(self):
        """
        Get the number of company in the database
        :return:
        """
        return self.__company_list.shape[0]

    @property
    def sectors(self):
        """
        Get all sectors in the database
        :return:
        """
        return set(self.__company_list[self.__SECTOR])

    @property
    def industries(self):
        """
        Get all industries in the database
        :return:
        """
        return set(self.__company_list[self.__INDUSTRY])

    @property
    def symbols(self):
        """
        get all symbols
        :return:
        """
        return list(self.__company_list[self.__SYMBOL])

    def update_all_history(self, update_database: bool = True, update_memory: bool = False):
        """
        update all history
        :param update_database:
        :param update_memory:
        :return:
        """
        for symbol in self.symbols:
            history = StockHistory(symbol)
            history.update(update_database, update_memory)
