import tensorflow as tf
import numpy as np


@tf.function
def cube(x):
    return x**3


def _main_gradient():
    x = tf.Variable(5.0)
    with tf.GradientTape() as tape:
        y = cube(x)
    gradient = tape.gradient(y, x)
    print(gradient)


def _main_func():
    a = tf.constant(1.0)
    b = tf.constant(2.0)
    print(rand_multiply(a))
    print(rand_multiply(b))


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
