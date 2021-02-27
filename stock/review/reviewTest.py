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
# # ticker = "PRN"
# # # ticker = 'AABA'
# st = YahooFinancials(ticker)
# historical_stock_prices = st.get_historical_price_data('2021-02-20', '2021-02-22', 'daily')
#
#
# stock = StockHistory(ticker)
# stock.update()

from stock.review.stockmanager import StockManager

manager = StockManager()
manager.update_all_history()

print("stop here")
