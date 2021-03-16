import math
import os
from typing import List

import mysql
from mysql.connector import CMySQLConnection
import pandas as pd
from mysql.connector.abstracts import MySQLCursorAbstract

from security.email import get_mysql_password
from stock.review.stockhistory import StockHistory
from stock.review.stockmanager import StockManager
from stock.review.stockstate import StockState
from utils.database.mysqlutils import is_table_exist, is_database_exist, add_table_column, delete_table_column
from utils.log import log


class StockManagerMySql(StockManager):

    __DATABASE_NAME__ = "financial"

    __TABLE_NAME__ = "stock"

    __ATTEMPTS = "Attempts"

    __LAST_UPDATE_DATE = "LastUpdateDate"

    def __init__(self):
        super().__init__()
        self.__db_conn__: CMySQLConnection = self.__init_sql_connection()

    def __del__(self):
        if self.__db_conn__:
            self.__db_conn__.close()

    def __init_sql_connection(self) -> CMySQLConnection:
        """
        init mySql database connection
        :return:
        """
        db = self.__get_database_connection()

        if not is_table_exist(db, self.__DATABASE_NAME__, self.__TABLE_NAME__):
            self.__create_table(db)

        return db

    def __get_database_connection(self):
        """
        Get the database connection. If database does not exist, create one
        :return:
        """
        sql_password = get_mysql_password()
        if not sql_password:
            raise Exception("Fail to get mySql password")

        db = mysql.connector.connect(user="root",
                                     password=sql_password,
                                     host="localhost")
        if not db:
            raise Exception("Fail to connect mySql server")

        if not is_database_exist(db, self.__DATABASE_NAME__):
            cursor = db.cursor()
            cursor.execute("CREATE DATABASE {}".format(self.__DATABASE_NAME__))
            cursor.close()

        db.close()
        db = mysql.connector.connect(user="root",
                                     password=sql_password,
                                     host="localhost",
                                     db=self.__DATABASE_NAME__)
        return db

    def __create_table(self, db_conn: CMySQLConnection):
        """
        Create table for stock
        :param db_conn:
        :return:
        """
        if not db_conn:
            raise Exception("database connection is invalid")

        cursor = db_conn.cursor()
        cursor.execute("CREATE TABLE {} (\
                        {} VARCHAR(255) PRIMARY KEY,\
                        {} VARCHAR(1023),\
                        {} FLOAT,\
                        {} FLOAT,\
                        {} VARCHAR(1023),\
                        {} INT,\
                        {} VARCHAR(1023),\
                        {} VARCHAR(1023),\
                        {} VARCHAR(1023),\
                        {} VARCHAR(1023),\
                        {} VARCHAR(1023),\
                        {} VARCHAR(1023),\
                        {} VARCHAR(1023),\
                        {} INT,\
                        {} DATE,\
                        {} DATE,\
                        {} DATE\
                        )".format(self.__TABLE_NAME__,
                                  self._SYMBOL,
                                  self._NAME,
                                  self._LAST_SALE,
                                  self._MARKET_CAP,
                                  self._ADR_TSO,
                                  self._IPO_YEAR,
                                  self._SECTOR,
                                  self._INDUSTRY,
                                  self._SUMMARY_QUOTA,
                                  self._EXCHANGE,
                                  self._EXCHANGE_DISPLAY,
                                  self._TYPE,
                                  self._TYPE_DISPLAY,
                                  self.__ATTEMPTS,
                                  self.__LAST_UPDATE_DATE,
                                  self._HISTORY_START_DATE,
                                  self._HISTORY_END_DATE))
        cursor.close()
        # self.update_table_from_xml(db_conn)

    def update_table_from_xml(self, symbol_list_file_path: str,
                              included_exchange_display: tuple = ("NYSE", "NASDAQ")):
        """
        initial table from xml file
        :return:
        """
        if not self.__db_conn__:
            log("fail to connect to mysql database when update table from xml")
            return

        if not os.path.isfile(symbol_list_file_path):
            log("xml file for company list does not exist when initialize database from xml file")
            return

        company_list = pd.read_csv(symbol_list_file_path)
        company_num = company_list.shape[0]

        cursor = self.__db_conn__.cursor()

        if self._SYMBOL in company_list:
            symbol_key = self._SYMBOL
        elif self._TICKER in company_list:
            symbol_key = self._TICKER
        else:
            log("no symbol entry in the xml file: " + symbol_list_file_path)
            return

        for i in range(company_num):
            row = company_list.iloc[i]

            symbol = row[symbol_key]
            if "'" in symbol:
                continue

            if self._EXCHANGE_DISPLAY in row:
                exchange_display = row[self._EXCHANGE_DISPLAY]
                if exchange_display not in included_exchange_display:
                    print("the exchange display for {} is {}. It does not belong to {}. skip it".
                          format(symbol, exchange_display, included_exchange_display))
                    continue

            if self._STATE in row:
                state = StockState(row[self._STATE])
                attempts = state.attempts
                last_update_date = state.update_date
            else:
                attempts = None
                last_update_date = None

            name = row[self._NAME] if self._NAME in row else None
            last_scale = row[self._LAST_SALE] if self._LAST_SALE in row else None
            market_cap = row[self._MARKET_CAP] if self._MARKET_CAP in row else None
            adr_tso = row[self._ADR_TSO] if self._ADR_TSO in row else None
            ipo_year = row[self._IPO_YEAR] if self._IPO_YEAR in row else None
            sector = row[self._SECTOR] if self._SECTOR in row else None
            industry = row[self._INDUSTRY] if self._INDUSTRY in row else None
            summary_quota = row[self._SUMMARY_QUOTA] if self._SUMMARY_QUOTA in row else None
            exchange = row[self._EXCHANGE] if self._EXCHANGE in row else None
            exchange_display = row[self._EXCHANGE_DISPLAY] if self._EXCHANGE_DISPLAY in row else None
            stock_type = row[self._TYPE] if self._TYPE in row else None
            type_display = row[self._TYPE_DISPLAY] if self._TYPE_DISPLAY in row else None

            self.__update_one_symbol(cursor,
                                     symbol,
                                     name,
                                     last_scale,
                                     market_cap,
                                     adr_tso,
                                     ipo_year,
                                     sector,
                                     industry,
                                     summary_quota,
                                     exchange,
                                     exchange_display,
                                     stock_type,
                                     type_display,
                                     attempts,
                                     last_update_date)

        cursor.close()
        self.__db_conn__.commit()

    def __update_one_symbol(self,
                            cursor: MySQLCursorAbstract,
                            symbol: str,
                            name: str = None,
                            last_sale: float = None,
                            market_cap: float = None,
                            adr_tso: str = None,
                            ipo_year: int = None,
                            sector: str = None,
                            industry: str = None,
                            summary_quota: str = None,
                            exchange: str = None,
                            exchange_display: str = None,
                            stock_type: str = None,
                            type_display: str = None,
                            attempts: int = None,
                            last_update_date: str = None,
                            history_start_date: str = None,
                            history_end_date: str = None):
        """
        Add entry for one company
        :param cursor:
        :param symbol:
        :param name:
        :param last_sale:
        :param market_cap:
        :param adr_tso:
        :param ipo_year:
        :param sector:
        :param industry:
        :param summary_quota:
        :param attempts:
        :param last_update_date:
        :return:
        """
        if not symbol:
            raise Exception("Invalid symbol")

        # if a stock symbol does not exist in table, insert it.
        if not self.__is_symbol_exist(cursor, symbol):
            self.__insert_symbol(cursor, symbol)

        # update the symbol other fields
        key_value_list = []
        if name:
            key_value_list.append("{}={}".format(self._NAME, self.__format_entry(name, True)))

        if last_sale:
            key_value_list.append("{}={}".format(self._LAST_SALE, self.__format_entry(last_sale, False)))

        if market_cap:
            key_value_list.append("{}={}".format(self._MARKET_CAP, self.__format_entry(market_cap, False)))

        if adr_tso:
            key_value_list.append("{}={}".format(self._ADR_TSO, self.__format_entry(adr_tso, True)))

        if ipo_year:
            key_value_list.append("{}={}".format(self._IPO_YEAR, self.__format_entry(ipo_year, False)))

        if sector:
            key_value_list.append("{}={}".format(self._SECTOR, self.__format_entry(sector, True)))

        if industry:
            key_value_list.append("{}={}".format(self._INDUSTRY, self.__format_entry(industry, True)))

        if summary_quota:
            key_value_list.append("{}={}".format(self._SUMMARY_QUOTA, self.__format_entry(summary_quota, True)))

        if exchange:
            key_value_list.append("{}={}".format(self._EXCHANGE, self.__format_entry(exchange, True)))

        if exchange_display:
            key_value_list.append("{}={}".format(self._EXCHANGE_DISPLAY, self.__format_entry(exchange_display, True)))

        if stock_type:
            key_value_list.append("{}={}".format(self._TYPE, self.__format_entry(stock_type, True)))

        if type_display:
            key_value_list.append("{}={}".format(self._TYPE_DISPLAY, self.__format_entry(type_display, True)))

        if attempts:
            key_value_list.append("{}={}".format(self.__ATTEMPTS, self.__format_entry(attempts, False)))

        if last_update_date:
            key_value_list.append("{}={}".format(self.__LAST_UPDATE_DATE, self.__format_entry(last_update_date, True)))

        if history_start_date:
            key_value_list.append("{}={}".format(self._HISTORY_START_DATE, self.__format_entry(history_start_date, True)))

        if history_end_date:
            key_value_list.append("{}={}".format(self._HISTORY_END_DATE, self.__format_entry(history_end_date, True)))

        if not key_value_list:
            return

        try:
            sql = "UPDATE {} SET {} WHERE Symbol='{}'".format(self.__TABLE_NAME__, ", ".join(key_value_list), symbol)
            print(sql)
            cursor.execute(sql)
        except Exception as e:
            print(e)

    def __is_symbol_exist(self, cursor: MySQLCursorAbstract, symbol: str):
        """
        Test whether a symbol already exist in the stock table.
        The returned result is like [(1,)].
        If the result is [(1,)], the symbol exist.
        If the result is [(0,)], the symbol does not exist.
        :param cursor:
        :param symbol:
        :return:
        """
        sql = "SELECT EXISTS(SELECT * from {} WHERE Symbol='{}')".format(self.__TABLE_NAME__, symbol)
        print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result[0][0] == 1

    def __insert_symbol(self, cursor: MySQLCursorAbstract, symbol: str):
        """
        if a symbol does not exist in stock table, insert it.
        :param cursor:
        :param symbol:
        :return:
        """
        sql = "INSERT INTO {} ({}) VALUES ({})".format(
                self.__TABLE_NAME__,
                self._SYMBOL,
                self.__format_entry(symbol, True))
        print(sql)
        cursor.execute(sql)

    @staticmethod
    def __format_entry(data, is_str: bool):
        """
        format an entry. If no data. Set NULL
        :return:
        """
        ret_str = "NULL"
        if data:
            if is_str:
                data_str = str(data)
                if data_str != "nan":
                    data_str = data_str.replace("'", " ")
                    ret_str = "'{}'".format(data_str)
            else:
                if not math.isnan(data):
                    ret_str = str(data)

        return ret_str

    def __create_database(self, sql_password: str) -> CMySQLConnection:
        """
        create database
        :return:
        """
        db = mysql.connector.connect(user="root",
                                     password=sql_password,
                                     host="localhost")
        if not db:
            raise Exception("Fail to connect mySql server")

        cursor = db.cursor()
        cursor.execute("CREATE DATABASE {}".format(self.__DATABASE_NAME__))
        cursor.close()
        db.close()

        db = mysql.connector.connect(user="root",
                                     password=sql_password,
                                     host="localhost",
                                     db=self.__DATABASE_NAME__)
        if not db:
            raise Exception("Fail to create database")

        return db

    def __get_set_for_column(self, column_name: str) -> set:
        """
        Get the set of all element in a column
        :return:
        """
        cursor = self.__db_conn__.cursor()
        cursor.execute("SELECT {} from {}".format(column_name, self.__TABLE_NAME__))
        result = cursor.fetchall()
        sector_set = set()
        if result:
            sector_set = set([t[0] for t in result])
        cursor.close()
        return sector_set

    @property
    def sectors(self) -> set:
        """
        Get the set of all sectors
        :return:
        """
        return self.__get_set_for_column(self._SECTOR)

    @property
    def industries(self) -> set:
        """
        get the set of all industrial
        :return:
        """
        return self.__get_set_for_column(self._INDUSTRY)

    @property
    def symbols(self) -> set:
        """
        get the set of all symbols
        :return:
        """
        return self.__get_set_for_column(self._SYMBOL)

    def __get_value(self, symbol: str, column: str):
        """
        get the value of a column for a stock
        :param symbol:
        :param column:
        :return:
        """
        if not self.__db_conn__:
            return None

        cursor = self.__db_conn__.cursor()
        sql = "SELECT {} FROM STOCK WHERE SYMBOL='{}'".format(column, symbol)
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result[0][0]

    def _get_attempts(self, symbol: str):
        """
        get attempts
        :param symbol:
        :return:
        """
        return self.__get_value(symbol, self.__ATTEMPTS)

    @property
    def company_size(self) -> int:
        symbols = self.symbols
        return len(symbols) if symbols else 0

    def update_attempts(self, symbol: str, attempts: int, update_date: str = None, date_range: [List, None] = None):
        cursor = self.__db_conn__.cursor()
        start_date = None
        end_date = None
        if date_range is not None:
            start_date = date_range[0]
            end_date = date_range[1]
        self.__update_one_symbol(cursor, symbol, attempts=attempts, last_update_date=update_date,
                                 history_start_date=start_date, history_end_date=end_date)
        cursor.close()

    def increase_attempts(self, symbol: str, date_range: [List, None]):
        attempts = self._get_attempts(symbol)
        if attempts is None:
            attempts = 1
        else:
            attempts += 1
        self.update_attempts(symbol, attempts, date_range)

    def __commit(self):
        """
        update database by commit
        :return:
        """
        self.__db_conn__.commit()

    def _handle_after_update_all(self):
        self.__commit()

    def _handle_after_update_batch(self):
        """
        handle after a batch of symbols were updated
        :return:
        """
        self.__commit()

    def add_column(self, column_name: str, column_data_type: str):
        """
        add a column in the database
        :param column_name:
        :param column_data_type:
        :return:
        """
        add_table_column(self.__db_conn__, self.__TABLE_NAME__, column_name, column_data_type)

    def delete_column(self, column_name: str):
        """
        delete a column
        :param column_name:
        :return:
        """
        delete_table_column(self.__db_conn__, self.__TABLE_NAME__, column_name)

    def synchronize_history_range(self):
        """
        synchronize the history range between mysql database and the stock
        history files
        :return:
        """
        cursor = self.__db_conn__.cursor()
        for index, symbol in enumerate(self.symbols):
            if not self._is_valid_symbol(symbol):
                continue

            history = StockHistory(symbol)
            start_date = "NULL"
            end_date = "NULL"
            if not history.is_history_empty():
                start_date, end_date = history.date_range

            self.__update_one_symbol(cursor, symbol, history_start_date=start_date, history_end_date=end_date)
            if (index + 1) % 100 == 0:
                self.__db_conn__.commit()

        cursor.close()
        self.__db_conn__.commit()