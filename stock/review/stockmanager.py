"""
manage all stocks
"""
import os
from datetime import datetime
from shutil import copyfile
from typing import Dict

import urllib.request
import pandas as pd

from security.config import config
from stock.review.historyutils import datetime_to_str
from stock.review.stockenum import HistoryDataFailureType
from stock.review.stockhistory import StockHistory
from stock.review.stockstate import StockState
from utils.log import log


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
    __STATE = "State"

    __INVALID_FILE_NAME = {"CON", "PRN", "NULL"}

    # if fail more than five times, we may set the stock inactive
    __MAX_ATTEMPTS_NUM = 5

    # if fail to get the record for the past 14 days, we may set the stock inactive
    __MAX_INACTIVE_DAYS = 14

    __DELIMITER: str = ","

    # After every 20 stocks, we check the server is accessible
    __SERVER_TEST_FREQ = 20

    def __init__(self):
        self.__init_company_list()
        self.__init_index_dict()

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
                fp.write("{},{},{},{},{},{},{},{},{},{}\n".format(self.__SYMBOL,
                                                                  self.__NAME,
                                                                  self.__LAST_SALE,
                                                                  self.__MARKET_CAP,
                                                                  self.__ADR_TSO,
                                                                  self.__IOP_YEAR,
                                                                  self.__SECTOR,
                                                                  self.__INDUSTRY,
                                                                  self.__SUMMARY_QUOTA,
                                                                  self.__STATE))

        # if there is temp state file exist, merge the state first.
        self.__merge_temp_state_file()
        self.__company_list: pd.DataFrame = pd.read_csv(self.__company_list_file_path)

    def __init_index_dict(self):
        """
        initialize index dict. Create an index from symbol to tuple of (loc and state)
        :return:
        """
        self.__index_dict = dict()
        states = self.__company_list[self.__STATE]
        for index, symbol in enumerate(self.symbols):
            self.__index_dict[symbol] = (index, StockState(states[index]))

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

    def __merge_temp_state_file(self):
        """
        merge temperate state file.
        :return:
        """
        def get_state_dict(file_path: str) -> Dict:
            """
            get the temp state from file
            :param file_path:
            :return:
            """
            state_dict = dict()
            with open(file_path, 'r') as fp:
                for line_buff in fp.readlines():
                    line_buff = line_buff.strip()
                    if not line_buff:
                        continue

                    pair = line_buff.split(",")
                    if len(pair) != 2:
                        continue

                    state_dict[pair[0]] = pair[1]
            return state_dict

        def merge_temp_state(state_dict: Dict):
            """
            merge temp state
            :param state_dict:
            :return:
            """
            temp_company_list_file_path = config.path.company_temp_state_file_path + "temp"
            with open(temp_company_list_file_path, "w") as dst_fp:
                with open(config.path.company_list_file_path, "r") as src_fp:
                    for line_buf in src_fp.readlines():
                        proc_buf = line_buf.strip()
                        items = proc_buf.split(self.__DELIMITER)
                        if len(items) > 1 and items[0] in state_dict:
                            items[-1] = state_dict[items[0]]
                            dst_fp.write("{}\n".format(self.__DELIMITER.join(items)))
                        else:
                            dst_fp.write(line_buf)

            copyfile(temp_company_list_file_path, config.path.company_list_file_path)
            os.remove(temp_company_list_file_path)

        if not os.path.isfile(config.path.company_temp_state_file_path):
            return

        temp_state_dict = get_state_dict(config.path.company_temp_state_file_path)
        merge_temp_state(temp_state_dict)
        os.remove(config.path.company_temp_state_file_path)

    def __get_state(self, symbol: str) -> [StockState, None]:
        """
        get the state of the given symbol
        :param symbol:
        :return:
        """
        if not symbol:
            return None

        if symbol not in self.__index_dict:
            return None

        item = self.__index_dict[symbol]
        if item is None or not isinstance(item, tuple) or len(item) < 2:
            return None

        state = item[1]
        if not isinstance(state, StockState):
            return None

        return state

    @staticmethod
    def __is_active(stock_state: StockState, symbol: str) -> bool:
        """
        test whether a stock is still active or not
        :param stock_state:
        :return:
        """
        if stock_state is None:
            log("{} Warn: unknown error when testing whether a stock is still active. "
                "We set it active by default".format(symbol))
            return True

        return stock_state.attempts < StockManager.__MAX_ATTEMPTS_NUM

    @staticmethod
    def __is_server_accessible():
        """
        Check whether financial server is accessible
        :return:
        """
        return urllib.request.urlopen("https://finance.yahoo.com/quote/AAPL").getcode() == 200

    def update_all_history(self, update_database: bool = True, update_memory: bool = False,
                           update_inactive: bool = False):
        """
        update all history
        :param update_database:
        :param update_memory:
        :param update_inactive:
            whether update inactive stocks
        :return:
        """
        stock_num = self.company_size
        for index, symbol in enumerate(self.symbols):
            log("Info: updating the history for {} {}/{}".format(symbol, index+1, stock_num))

            # test whether server is accessible. if not, quit
            if index % self.__SERVER_TEST_FREQ == 0:
                if not self.__is_server_accessible():
                    log("Warn: Server is not accessible. Stop updating")
                    break

            if symbol in self.__INVALID_FILE_NAME:
                log("INFO: {} is invalid as a file name for saving".format(symbol))
                continue

            history = StockHistory(symbol)
            state = self.__get_state(symbol)
            if not update_inactive and not self.__is_active(state, symbol):
                continue

            failure_type = history.update(update_database, update_memory)
            if state is not None:
                with open(config.path.company_temp_state_file_path, "a+") as fp:
                    if failure_type == HistoryDataFailureType.SUCCESS:
                        state.update_date = datetime_to_str(datetime.now())
                        state.attempts = 0
                    else:
                        state.increase_attempts()

                    state_record = self.__DELIMITER.join([symbol, str(state)])
                    fp.write("{}\n".format(state_record))

        self.__merge_temp_state_file()
