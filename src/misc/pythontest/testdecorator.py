"""
All test are from the webs
https://realpython.com/primer-on-python-decorators/#decorators-with-arguments
"""

import functools
import math
from typing import Callable, Any


def dec(*args: Any, **kwargs: Any):
    def inner():
        print("hello")
        # return f
    return inner


@dec
def hello_test(a):
    print("main func")


class ClassDecorator:

    def on(self, event_name: Any, *args: Any, **kwargs: Any) -> Callable:
        # def decorator(f: Callable) -> Callable:
        def decorator(f):
            print("decorated")
            return f

        return decorator

    @staticmethod
    def test():
        pass


# def on(event_name: Any, *args: Any, **kwargs: Any) -> Callable:
def on():
    # def decorator(f: Callable) -> Callable:
    def decorator(f, *args, **kwargs):
        print("decorated")
        return f

    return decorator


def repeat(_func=None, *, num_times=2):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            value = None
            for _ in range(num_times):
                value = func(*args, **kwargs)
            return value
        return wrapper_repeat

    if _func is None:
        return decorator_repeat
    else:
        return decorator_repeat(_func)


def count_calls(func):
    @functools.wraps(func)
    def wrapper_count_calls(*args, **kwargs):
        wrapper_count_calls.num_calls += 1
        print(f"Call {wrapper_count_calls.num_calls} of {func.__name__!r}")
        return func(*args, **kwargs)
    wrapper_count_calls.num_calls = 0
    return wrapper_count_calls


import functools

class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.num_calls = 0

    def __call__(self, *args, **kwargs):
        self.num_calls += 1
        print(f"Call {self.num_calls} of {self.func.__name__!r}")
        return self.func(*args, **kwargs)

# @count_calls
@CountCalls
def say_whee():
    print("Whee!")

# @repeat
# def say_whee():
#     print("Whee!")


@repeat(num_times=3)
def greet(name):
    print(f"Hello {name}")


def singleton(cls):
    """Make a class a Singleton class (only one instance)"""
    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance
    wrapper_singleton.instance = None
    return wrapper_singleton

@singleton
class TheOne:
    pass


def cache(func):
    """Keep a cache of previous function calls"""
    @functools.wraps(func)
    def wrapper_cache(*args, **kwargs):
        cache_key = args + tuple(kwargs.items())
        if cache_key not in wrapper_cache.cache:
            wrapper_cache.cache[cache_key] = func(*args, **kwargs)
        return wrapper_cache.cache[cache_key]
    wrapper_cache.cache = dict()
    return wrapper_cache

@cache
@count_calls
def fibonacci(num):
    if num < 2:
        return num
    return fibonacci(num - 1) + fibonacci(num - 2)


def set_unit(unit):
    """Register a unit on a function"""
    def decorator_set_unit(func):
        func.unit = unit
        return func
    return decorator_set_unit


@set_unit("cm^3")
def volume(radius, height):
    return math.pi * radius**2 * height


from flask import Flask, request, abort
import functools
app = Flask(__name__)


def validate_json(*expected_args):                  # 1
    def decorator_validate_json(func):
        @functools.wraps(func)
        def wrapper_validate_json(*args, **kwargs):
            json_object = request.get_json()
            for expected_arg in expected_args:      # 2
                if expected_arg not in json_object:
                    abort(400)
            return func(*args, **kwargs)
        return wrapper_validate_json
    return decorator_validate_json


@app.route("/grade", methods=["POST"])
@validate_json("student_id")
def update_grade():
    json_data = request.get_json()
    # Update database.
    return "success!"

if __name__ == "__main__":
    # dec = ClassDecorator()
    #
    # @on()
    # def log_losses(trainer):
    #     print(trainer)
    #     print("do nothing")
    #
    # log_losses("test")

    # say_whee()
    # greet("val")

    # first_one = TheOne()
    # another_one = TheOne()
    #
    # print(first_one is another_one)
    # print(id(first_one))
    # print(id(another_one))

    print(fibonacci(100))