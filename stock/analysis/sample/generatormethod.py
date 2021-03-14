"""
define how to generate one sample from given array
"""
import abc
from random import randrange
from typing import List

import numpy as np


class GeneratorMethod:

    def __init__(self, sample_length: int):
        super(GeneratorMethod, self).__init__()
        self.sample_length = sample_length

    @abc.abstractmethod
    def sample_number(self, dataset: np.array) -> int:
        """
        Given a array (can be any dimension), estimate how many sample can be
        obtained from it.
        :return:
        """
        raise Exception("Implement it in concrete class")

    @abc.abstractmethod
    def next_sample(self, dataset: np.array) -> np.array:
        """
        It is a generator. Generate next sample
        :param dataset:
        :return:
        """
        pass

    def _generate_random_order(self, dataset: np.array) -> List:
        """
        Generate the randomize order for sampling
        :return:
        """
        sample_num = self.sample_number(dataset)
        return randrange(sample_num) if sample_num > 0 else []
