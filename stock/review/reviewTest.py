"""
Test
"""
import os

import matplotlib.pyplot as plt

from security.config import config
from stock.review.stockenum import ViewMode
from stock.review.stockhistory import StockHistory

code = "AABA"
path = os.path.join(config.path.stock_history_folder_path, code + ".csv")
stock = StockHistory(code, path)
stock.print()
# plot(stock.get_open())
date = stock.date
daily = stock.open()
weekly = stock.open(view_mode=ViewMode.WEEKLY)
monthly = stock.open(view_mode=ViewMode.MONTHLY)

plt.plot(daily)
plt.plot(weekly)
plt.plot(monthly)

plt.show()
