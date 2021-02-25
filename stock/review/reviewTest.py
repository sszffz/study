"""
Test
"""
import os

import matplotlib.pyplot as plt

from yahoofinancials import YahooFinancials

from security.config import config
from stock.review.stockenum import ViewMode
from stock.review.stockhistory import StockHistory

#
# # code = "AABA"
# code = "AAPL"
# path = os.path.join(config.path.stock_history_folder_path, code + ".csv")
# stock = StockHistory(code, from_file=path)
# stock.print()
# # plot(stock.get_open())
# date = stock.date
# daily = stock.open()
# weekly = stock.open(view_mode=ViewMode.WEEKLY)
# monthly = stock.open(view_mode=ViewMode.MONTHLY)
#
# # plt.plot(daily)
# # plt.plot(weekly)
# # plt.plot(monthly)
# #
# # plt.show()
#
# print(stock.range)
# stock.update()


# ticker = 'AAPL'
# # ticker = 'AABA'
# # st = YahooFinancials(ticker)
# # historical_stock_prices = st.get_historical_price_data('2019-09-15', '2020-09-15', 'weekly')
#
#
# stock = StockHistory(ticker)
# stock.update()
# from stock.review.stockmanager import StockManager
#
from stock.review.stockmanager import StockManager

manager = StockManager()
# print(manager.company_size)
manager.update_all_history()
# print(manager.sectors)
# print(manager.industries)
# from utils.log import log
#
# log("test")

print("stop here")