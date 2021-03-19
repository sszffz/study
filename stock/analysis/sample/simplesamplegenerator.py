"""

"""
from typing import Tuple

from stock.analysis.sample.generatormethod import GeneratorMethod
from stock.analysis.sample.samplegenerator import SampleGenerator
from stock.review.stockenum import PriceType
from stock.review.stockhistory import StockHistory
from stock.review.stockmanager import StockManager


class SimpleSampleGenerator(SampleGenerator):

    def __init__(self, stock_manager: StockManager,
                 generator_method: GeneratorMethod,
                 batch_size: int,
                 split_ratio: Tuple = (6, 3, 1),
                 column_name: str = str(PriceType.OPEN)):
        super(SimpleSampleGenerator, self).__init__(stock_manager, generator_method, batch_size, split_ratio)
        self.column_name = column_name

    def get_dataset(self, symbol: str):
        history = StockHistory(symbol)
        # history.