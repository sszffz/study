"""
sample at each point
"""
import numpy as np

from stock.analysis.sample.generatormethod import GeneratorMethod


class StepGenerator(GeneratorMethod):

    def __init__(self, sample_length: int):
        super(StepGenerator, self).__init__(sample_length)

    def sample_number(self, dataset: np.array) -> int:
        if not dataset or dataset.shape[0] < self.sample_length:
            return 0

        return dataset.shape[0] - self.sample_length + 1

    def get_sample(self, dataset: np.array, index: int) -> np.array:
        return dataset[index:(index + self.sample_length), ...]

