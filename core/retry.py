import functools
import time


def retry(max_retries=3, delay=2):
    """
    Decorator to automatically retry a function upon failure.

    Retries the wrapped function up to `max_retries` times with a delay between attempts,
    handling common exceptions like AssertionError, ValueError, and ConnectionError.
    """
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (AssertionError, ValueError, ConnectionError) as e:
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        raise
        return wrapper_retry
    return decorator_retry
