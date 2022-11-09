"""
sample at each point
"""
import numpy as np

from stock.analysis.sample.picker import Picker


class StepPicker(Picker):

    def __init__(self, sample_length: int):
        super(StepPicker, self).__init__(sample_length)

    def sample_number(self, recorder_number: int) -> int:
        if recorder_number is None or recorder_number < self.sample_length:
            return 0

        return recorder_number - self.sample_length + 1

    def get_sample(self, dataset: np.array, index: int) -> np.array:
        return dataset[index:(index + self.sample_length), ...]

