"""
update stock type. mainly update the type for Stock.
The logic is to check check the stock history, if open, close, high, low
are different in one day, it is a stock
"""
from stock.review.stockenum import PriceType
from stock.review.stockhistory import StockHistory
from stock.review.stockmanager import StockManager
from stock.review.stockmanagermysql import StockManagerMySql

manager = StockManagerMySql()
result = manager.select_columns([StockManager.SYMBOL, StockManager.TYPE])
cursor = manager.create_cursor()
for symbol, stock_type in result:
    if stock_type is None:
        history = StockHistory(symbol)
        if history.is_history_empty():
            continue

        high = history.history(price_type=PriceType.HIGH)
        low = history.history(price_type=PriceType.LOW)
        last_high = high[-1]
        last_low = low[-1]
        if last_high != last_low:
            manager.update_one_symbol(cursor, symbol=symbol, stock_type="S")
manager.commit()
