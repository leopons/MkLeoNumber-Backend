import time
import functools
from django.http import Http404


def time_it(logger):
    def decorator(method):
        def timed(*args, **kw):
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()
            logger.info(method.__name__ + " took {}".format((te-ts)*1000))
            return result
        return timed
    return decorator


def log_exceptions(logger):
    def decorator(function):
        # A decorator that wraps the passed in function and logs exceptions
        # (with stack trace)
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Http404 as ex:
                template = "An exception of type {0} occurred. \
                    Arguments:\n{2!r}"
                message = template.format(
                    type(ex).__name__, function.__name__, ex.args)
                logger.warning(message)
                raise Http404
            except Exception as ex:
                template = "An exception of type {0} occurred. \
                    Arguments:\n{2!r}"
                message = template.format(
                    type(ex).__name__, function.__name__, ex.args)
                logger.exception(message)
        return wrapper
    return decorator
