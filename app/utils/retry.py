from __future__ import annotations

import asyncio
import functools
import random
import time
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from loguru import logger

P = ParamSpec("P")
R = TypeVar("R")


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception: Exception | None = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (exponential_base**attempt), max_delay)
                        if jitter:
                            delay *= 1 + random.random()  # nosec - non-crypto jitter for retry backoff
                        logger.warning(
                            "Retry {attempt}/{max} for {func} after {delay:.1f}s: {e}",
                            attempt=attempt + 1,
                            max=max_retries,
                            func=func.__name__,
                            delay=delay,
                            e=e,
                        )
                        time.sleep(delay)
            msg = f"Failed after {max_retries} retries: {last_exception}"
            raise RuntimeError(msg) from last_exception

        return wrapper

    return decorator


def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (exponential_base**attempt), max_delay)
                        if jitter:
                            delay *= 1 + random.random()  # nosec - non-crypto jitter for retry backoff
                        logger.warning(
                            "Async retry {attempt}/{max} for {func} after {delay:.1f}s: {e}",
                            attempt=attempt + 1,
                            max=max_retries,
                            func=func.__name__,
                            delay=delay,
                            e=e,
                        )
                        await asyncio.sleep(delay)
            msg = f"Failed after {max_retries} retries: {last_exception}"
            raise RuntimeError(msg) from last_exception

        return wrapper

    return decorator
