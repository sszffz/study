"""
enumerate type for sample
"""
from enum import Enum


class SampleType(Enum):
    TRAIN = 0
    VALIDATION = 1
    TEST = 2
