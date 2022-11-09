"""
Define an interface about how to sample data from database
"""
import random
from typing import Tuple, Dict

from stock.analysis.sample.datasetcreator import DatasetCreator
from stock.analysis.sample.picker import Picker
from stock.analysis.sample.sampleenum import SampleType
from stock.review.stockmanager import StockManager


class SampleGenerator:

    def __init__(self,
                 stock_manager: StockManager,
                 dataset_creator: DatasetCreator,
                 sample_picker: Picker,
                 batch_size: int = 10,
                 split_ratio: Tuple = (6, 3, 1)):
        """
        symbol_dataset_dict is a dictionary. Key is symbol, the value is dataset
        sample_dict is a dictionary. Key is SampleType, value is a tuple (symbol, index)
        dataset is

        :param stock_manager:
        :param sample_picker:
        :param batch_size:
        :param split_ratio:
            training, validation and test ratio
        """
        super(SampleGenerator, self).__init__()
        self.stock_manager: StockManager = stock_manager
        self.dataset_creator: DatasetCreator = dataset_creator
        self.sample_picker: Picker = sample_picker
        self.batch_size: int = batch_size
        self.split_ratio: Tuple = split_ratio
        self.symbol_dataset_dict: Dict = self.__get_symbol_dataset_dict()
        self.sample_dict: Dict = self.__split_samples()

    def __split_samples(self) -> Dict:
        """
        split sample to generate the samples for training, validation and testing
        :return:
        """
        split_sum = sum(self.split_ratio)
        total_sample_num = sum([count for _, count in self.symbol_dataset_dict.values()])
        train_sample_num = int(self.split_ratio[0]*total_sample_num/split_sum)
        validation_sample_num = int(self.split_ratio[1]*total_sample_num/split_sum)

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

        print("training sample size: {}".format(len(train_sample_index_list)))
        print("validation sample size: {}".format(len(validation_sample_index_list)))
        print("test sample size: {}".format(len(test_sample_index_list)))
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
        for symbol, recorder_number in self.stock_manager.get_symbols_record_numbers():
            if recorder_number is None or recorder_number == 0:
                continue

            valid_dataset_size = recorder_number - self.dataset_creator.diff_with_record_number(symbol)
            symbol_sample_num = self.sample_picker.sample_number(valid_dataset_size)
            if symbol_sample_num <= 0:
                continue

            symbol_dataset_dict[symbol] = [None, symbol_sample_num]

        print("{} symbols were obtained from database".format(len(symbol_dataset_dict)))
        return symbol_dataset_dict

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
            dataset_info = self.symbol_dataset_dict[symbol]
            dataset = dataset_info[0]
            if dataset is None:
                dataset = self.dataset_creator.create_dataset(symbol)
                dataset_info[0] = dataset

            yield self.sample_picker.get_sample(dataset, index)

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
