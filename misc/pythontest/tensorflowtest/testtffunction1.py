"""
test: avoid to include method from external library in the function decorated
by @tf.function
"""
import tensorflow as tf
import numpy as np


@tf.function
def rand_multiply_np(x):
    r = np.random.randn()
    return x * r


@tf.function
def rand_multiply_tf(x):
    r = tf.random.normal(x.shape)
    return x * r


if __name__ == '__main__':
    x = tf.constant(1.0)
    print("np:")
    for _ in range(3):
        print(rand_multiply_np(x))
    print("tf:")
    for _ in range(3):
        print(rand_multiply_tf(x))
