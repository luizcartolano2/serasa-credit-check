import time
from functools import wraps
from flask import g


def track_metrics(func):
    """
    A decorator to track the duration of a request and store it in the Flask global context.
    :param func: a callable function that represents a Flask route
    :return: a wrapped function that tracks the request duration
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        g.request_duration = duration
        return result
    return wrapper
