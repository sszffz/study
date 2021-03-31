"""
Create dataset from history using one column data
"""
import numpy as np

from stock.analysis.sample.datasetcreator import DatasetCreator
from stock.review.stockenum import PriceType
from stock.review.stockhistory import StockHistory


class SingleCreator(DatasetCreator):

    def __init__(self, price_type: PriceType):
        self.price_type = price_type

    def create_dataset(self, symbol: str) -> np.array:
        """
        Get dataset for generator. It corresponds to one column in the stock
        history file, defined for "Price_Type", like open price, close price.
        :param symbol:
        :return:
        """
        history = StockHistory(symbol)
        return history.history(price_type=self.price_type)

    def diff_with_record_number(self, symbol: str) -> int:
        """
        The size of dataset generated from this class is the same as number
        of record of stock history
        :param symbol:
        :return:
        """
        return 0

