"""
define how to create a dataset for a symbol
"""
import abc


class DatasetCreator:

    @abc.abstractmethod
    def create_dataset(self, symbol: str):
        """
        Given the symbol, define how to get the dataset for the symbol
        :param symbol:
        :return:
        """
        raise NotImplementedError("Implement in concrete class")

    @abc.abstractmethod
    def diff_with_record_number(self, symbol: str):
        """
        record number is the size of all record for the history of a stock. However,
        In some scenario, the size of dataset is not equal the number of record.
        For example, return the daily change rate, the valid dataset size is 1
        less than the number of all record. Then this method should return 1.
        If the dataset is the weekly change rate, the valid dataset size is 5
        less than the number of all record, then this method should return 5.
        :param symbol:
        :return:
        """
        raise NotImplementedError("Implement in concrete class")