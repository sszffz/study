"""
Test: use tf.range instead of range in the function decorated by @tf.function

I tested it, but didn't find the difference. Maybe understanding is incorrect
"""
from timeit import timeit

import tensorflow as tf
import numpy as np


@tf.function
def loop_tf_range(sum, x):
    for i in tf.range(5):
        sum.assign_add(x[i])
    return sum


@tf.function
def loop_range(sum, x):
    for i in range(5):
        sum.assign_add(x[i])
    return sum


# if __name__ == '__main__':
#     x1 = tf.constant([0, 1, 2, 3, 4])
#     x2 = tf.constant([0, 1, 2, 3, 4])
#     y1 = tf.Variable(0)
#     y2 = tf.Variable(0)
#
#
#     %timeit (print(loop_range(y1, x1)))
#     print(loop_tf_range(y2, x2))


@tf.function(input_signature=[tf.TensorSpec(shape=[None], dtype=tf.float32)])
def test(x):
    for i in tf.range(100):
        x = x + tf.constant(0.0)
    return x

print(test(tf.range(1000, dtype='float32')))