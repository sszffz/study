"""
Define an interface about how to sample data from database
"""
import abc
import random
from typing import Tuple, Dict

from stock.analysis.sample.generatormethod import GeneratorMethod
from stock.analysis.sample.sampleenum import SampleType
from stock.review.stockmanager import StockManager


class SampleGenerator:

    def __init__(self,
                 stock_manager: StockManager,
                 generator_method: GeneratorMethod,
                 batch_size: int,
                 split_ratio: Tuple = (6, 3, 1)):
        """
        symbol_dataset_dict is a dictionary. Key is symbol, the value is dataset
        sample_dict is a dictionary. Key is SampleType, value is a tuple (symbol, index)
        dataset is

        :param stock_manager:
        :param generator_method:
        :param batch_size:
        :param split_ratio:
            training, validation and test ratio
        """
        super(SampleGenerator, self).__init__()
        self.stock_manager: StockManager = stock_manager
        self.generator_method: GeneratorMethod = generator_method
        self.batch_size: int = batch_size
        self.split_ratio: Tuple = split_ratio
        self.symbol_dataset_dict: Dict = self.__get_symbol_dataset_dict()
        self.sample_dict: Dict = self.__split_samples()

    @abc.abstractmethod
    def get_dataset(self, symbol: str):
        """
        get the dataset for one symbol
        :return:
        """
        raise NotImplementedError("Implement it in concrete class")

    def __split_samples(self) -> Dict:
        """
        split sample to generate the samples for training, validation and testing
        :return:
        """
        total_sample_num = sum([count for _, count in self.symbol_dataset_dict.values()])
        train_sample_num = int(self.split_ratio[0]/total_sample_num)
        validation_sample_num = int(self.split_ratio[1] / total_sample_num)

        # generate all sample index. A list of tuple with (symbol, index) in which
        # index is unique id when generating sample for a symbol.
        symbol_sample_index_list = [(symbol, i) for symbol, (_, count) in self.symbol_dataset_dict.items()
                                    for i in range(count)]

        # random sample
        random.shuffle(symbol_sample_index_list)

        validation_end_index = train_sample_num + validation_sample_num
        train_sample_index_list = symbol_sample_index_list[:train_sample_num]
        validation_sample_index_list = symbol_sample_index_list[train_sample_num:validation_end_index]
        test_sample_index_list = symbol_sample_index_list[validation_end_index:]

        return {SampleType.TRAIN: train_sample_index_list,
                SampleType.VALIDATION: validation_sample_index_list,
                SampleType.TEST: test_sample_index_list}

    def __get_symbol_dataset_dict(self) -> Dict:
        """
        get symbol dataset dictionary. The key is symbol, the value is the tuple
        of dataset and number of sample for this symbol.
        :return:
        """
        symbol_dataset_dict = dict()
        for symbol in self.__get_symbol_set_for_sample():
            dataset = self.get_dataset(symbol)
            if not dataset:
                continue

            symbol_sample_num = self.generator_method.sample_number(dataset)
            if symbol_sample_num <= 0:
                continue

            symbol_dataset_dict[symbol] = (dataset, symbol_sample_num)

        return symbol_dataset_dict

    def __get_symbol_set_for_sample(self):
        """
        Get the symbol set for sampling. Some stock can be excluded for sampling.
        By default, we use all symbols
        :return:
        """
        return self.stock_manager.symbols

    def batch_number(self, sample_type: SampleType):
        """
        Calculate how many batch can be generated from database
        :return:
        """
        return self.sample_dict[sample_type][1] // self.batch_size

    def sample_generator(self, sample_type: SampleType):
        """
        sample generator. It generates one sample
        :return:
        """
        sample_list = self.sample_dict[sample_type]
        for sample in sample_list:
            symbol, index = sample
            dataset = self.symbol_dataset_dict[symbol]
            yield self.generator_method.get_sample(dataset, index)

    def batch_generator(self, sample_type: SampleType):
        """
        batch generator. It generates a batch of sample (several of samples)
        :return:
        """
        sample_generator = self.sample_generator(sample_type)
        while True:
            batch = []
            for _ in range(self.batch_size):
                batch.append(next(sample_generator))
            yield batch

def test_g():
    a = [1, 2, 3]
    for t in a:
        yield t


if __name__ == "__main__":
    it = test_g()
    print(next(it))
    print(next(it))
    print(next(it))
    print(next(it))
