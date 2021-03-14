"""
sample at each point
"""
import numpy as np

from stock.analysis.sample.generatormethod import GeneratorMethod


class DailyGenerator(GeneratorMethod):

    def __init__(self, sample_length: int):
        super(DailyGenerator, self).__init__(sample_length)

    def sample_number(self, dataset: np.array) -> int:
        if not dataset or dataset.shape[0] < self.sample_length:
            return 0

        return dataset.shape[0] - self.sample_length + 1

    def next_sample(self, dataset: np.array) -> np.array:
        sample_order = self._generate_random_order(dataset)
        for start_idx in sample_order:
            yield dataset[start_idx:(start_idx + self.sample_length), ...]


