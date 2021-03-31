"""
manage all stocks
"""
import os
from shutil import copyfile
from typing import Dict, List

import pandas as pd

from security.config import config
from stock.review.stockmanager import StockManager
from stock.review.stockstate import StockState
from utils.log import log


class StockManagerFile(StockManager):

    __DELIMITER: str = ","

    def __init__(self):
        super().__init__()
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
                fp.write("{},{},{},{},{},{},{},{},{},{}\n".format(self.SYMBOL,
                                                                  self.NAME,
                                                                  self.LAST_SALE,
                                                                  self.MARKET_CAP,
                                                                  self.ADR_TSO,
                                                                  self.IPO_YEAR,
                                                                  self.SECTOR,
                                                                  self.INDUSTRY,
                                                                  self.SUMMARY_QUOTA,
                                                                  self.STATE))

        # if there is temp state file exist, merge the state first.
        self.__merge_temp_state_file()
        self.__company_list: pd.DataFrame = pd.read_csv(self.__company_list_file_path)

    def __init_index_dict(self):
        """
        initialize index dict. Create an index from symbol to tuple of (loc and state)
        :return:
        """
        self.__index_dict = dict()
        states = self.__company_list[self.STATE]
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
        return set(self.__company_list[self.SECTOR])

    @property
    def industries(self):
        """
        Get all industries in the database
        :return:
        """
        return set(self.__company_list[self.INDUSTRY])

    @property
    def symbols(self):
        """
        get all symbols
        :return:
        """
        return list(self.__company_list[self.SYMBOL])

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

    def _get_attempts(self, symbol: str):
        stock_state = self.__get_state(symbol)
        if stock_state is None:
            log("{} Warn: unknown error when testing whether a stock is still active. "
                "We set it active by default".format(symbol))
            return None

        return stock_state.attempts

    def _handle_after_update_all(self):
        """
        merge state file to the main stock file
        :return:
        """
        self.__merge_temp_state_file()

    def update_attempts(self, symbol: str, attempts: int, update_date: str, date_range: [List, None], record_num: int):
        state = self.__get_state(symbol)

        if state is not None:
            with open(config.path.company_temp_state_file_path, "a+") as fp:
                state.update_date = update_date
                state.attempts = 0
                state_record = self.__DELIMITER.join([symbol, str(state)])
                fp.write("{}\n".format(state_record))

    def increase_attempts(self, symbol: str, date_range: [List, None], record_num: int):
        state = self.__get_state(symbol)

        if state is not None:
            with open(config.path.company_temp_state_file_path, "a+") as fp:
                state.increase_attempts()
                state_record = self.__DELIMITER.join([symbol, str(state)])
                fp.write("{}\n".format(state_record))

    def get_symbols_record_numbers(self):
        raise NotImplementedError("it is not implemented yet")
