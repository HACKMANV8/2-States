"""
Retry logic and rate limiting for GitHub API calls.
"""

import asyncio
import time
from typing import Callable, Any, Optional, Dict
from functools import wraps
import httpx


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass


class RateLimitExceeded(GitHubAPIError):
    """Exception raised when GitHub API rate limit is exceeded."""
    pass


class RetryableError(GitHubAPIError):
    """Exception for errors that should be retried."""
    pass


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    # Add jitter (0-20% of delay)
    jitter = delay * 0.2 * (time.time() % 1)
    return delay + jitter


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (httpx.HTTPError, httpx.TimeoutException)
):
    """
    Decorator for retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    # Check if this is a rate limit error
                    if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 403:
                        # Check for rate limit headers
                        rate_limit_remaining = e.response.headers.get("x-ratelimit-remaining")
                        if rate_limit_remaining == "0":
                            reset_time = int(e.response.headers.get("x-ratelimit-reset", 0))
                            current_time = int(time.time())
                            wait_seconds = max(reset_time - current_time, 0)

                            print(f"⚠️  GitHub API rate limit exceeded")
                            print(f"   Will retry after {wait_seconds} seconds")

                            if wait_seconds > 0 and wait_seconds < 3600:  # Don't wait more than 1 hour
                                await asyncio.sleep(wait_seconds + 1)
                                continue
                            else:
                                raise RateLimitExceeded(f"GitHub API rate limit exceeded. Reset in {wait_seconds}s")

                    if attempt < max_retries:
                        delay = exponential_backoff(attempt, base_delay, max_delay)
                        print(f"   ⚠️  Attempt {attempt + 1} failed: {str(e)[:100]}")
                        print(f"   🔄 Retrying in {delay:.1f} seconds...")
                        await asyncio.sleep(delay)
                    else:
                        print(f"   ❌ All {max_retries + 1} attempts failed")

                except Exception as e:
                    # For non-retryable exceptions, raise immediately
                    raise

            # If we've exhausted all retries, raise the last exception
            if last_exception:
                raise RetryableError(f"Failed after {max_retries + 1} attempts") from last_exception

        return wrapper
    return decorator


class GitHubRateLimiter:
    """
    Rate limiter for GitHub API calls.

    Tracks requests and enforces rate limits to avoid hitting GitHub API limits.
    """

    def __init__(self, calls_per_hour: int = 5000):
        """
        Initialize rate limiter.

        Args:
            calls_per_hour: Maximum number of API calls per hour
        """
        self.calls_per_hour = calls_per_hour
        self.call_history: list = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """
        Acquire permission to make an API call.

        Blocks if rate limit would be exceeded.
        """
        async with self.lock:
            now = time.time()
            one_hour_ago = now - 3600

            # Remove calls older than 1 hour
            self.call_history = [t for t in self.call_history if t > one_hour_ago]

            # Check if we're at the limit
            if len(self.call_history) >= self.calls_per_hour:
                # Calculate how long to wait
                oldest_call = self.call_history[0]
                wait_time = oldest_call + 3600 - now

                if wait_time > 0:
                    print(f"⚠️  Rate limit approaching. Waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)

                    # Refresh history after wait
                    now = time.time()
                    one_hour_ago = now - 3600
                    self.call_history = [t for t in self.call_history if t > one_hour_ago]

            # Record this call
            self.call_history.append(now)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get current rate limit statistics.

        Returns:
            Dictionary with rate limit stats
        """
        now = time.time()
        one_hour_ago = now - 3600

        # Count calls in last hour
        recent_calls = len([t for t in self.call_history if t > one_hour_ago])

        return {
            "calls_last_hour": recent_calls,
            "calls_remaining": max(0, self.calls_per_hour - recent_calls),
            "rate_limit": self.calls_per_hour,
            "percentage_used": (recent_calls / self.calls_per_hour * 100)
        }


# Global rate limiter instance
_rate_limiter = GitHubRateLimiter()


def with_rate_limit(func):
    """
    Decorator to enforce rate limiting on GitHub API calls.

    Usage:
        @with_rate_limit
        async def my_github_api_call():
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await _rate_limiter.acquire()
        return await func(*args, **kwargs)

    return wrapper


def get_rate_limit_stats() -> Dict[str, Any]:
    """Get current rate limit statistics."""
    return _rate_limiter.get_stats()


# Combine retry and rate limiting
def github_api_call(max_retries: int = 3):
    """
    Combined decorator for GitHub API calls with retry and rate limiting.

    Usage:
        @github_api_call(max_retries=3)
        async def fetch_pr_data(url):
            ...
    """
    def decorator(func):
        # Apply both decorators
        func = retry_with_backoff(max_retries=max_retries)(func)
        func = with_rate_limit(func)
        return func

    return decorator
