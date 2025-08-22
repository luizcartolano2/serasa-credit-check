import time
from collections import defaultdict
from flask import request, jsonify


class RateLimiter:
    """
    A simple rate limiter class to limit the number of requests from a specific IP address.
    This class uses a sliding window algorithm to track requests and enforce limits.

    Attributes:
        limit (int): Maximum number of requests allowed within the specified period.
        period (int): Time period in seconds during which the limit applies.
        requests (defaultdict): A dictionary to track request timestamps for each IP address.

    Methods:
        is_allowed(ip: str) -> (bool, int):
            Checks if the IP address is allowed to make a request based on the rate limit.
            Returns a tuple (allowed: bool, reset: int) where 'allowed' indicates if the request is allowed,
            and 'reset' indicates the time in seconds until the limit resets.

        decorator(func):
            A decorator to apply rate limiting to a Flask route.
            Returns a wrapped function that applies rate limiting.
    """

    def __init__(self, limit: int = 10, period: int = 60):
        self.limit = limit
        self.period = period
        self.requests = defaultdict(list)

    def is_allowed(self, ip: str) -> (bool, int):
        """
        Verify if the IP is allowed to make a request based on the rate limit.
        :param ip: a string representing the IP address of the requester
        :return: a tuple (allowed: bool, reset: int)
        """
        now = time.time()
        timestamps = self.requests[ip]

        # remove timestamps older than the period
        self.requests[ip] = [t for t in timestamps if t > now - self.period]

        if len(self.requests[ip]) >= self.limit:
            reset = self.period - (now - self.requests[ip][0])
            return False, int(reset)

        # if allowed, add the current timestamp
        self.requests[ip].append(now)
        return True, self.period

    def decorator(self, func):
        """
        Decorator to apply rate limiting to a Flask route.
        :param func: a callable function that represents a Flask route
        :return: a wrapped function that applies rate limiting
        """
        from functools import wraps

        @wraps(func)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            allowed, reset = self.is_allowed(ip)

            remaining = max(0, self.limit - len(self.requests[ip]))

            if not allowed:
                response = jsonify({"error": "Too many requests"})
                response.status_code = 429
                response.headers["X-RateLimit-Limit"] = str(self.limit)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(reset)
                return response

            # call the original function
            response = func(*args, **kwargs)

            # add rate limit headers to the response
            response.headers["X-RateLimit-Limit"] = str(self.limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset)

            return response

        return wrapper
