"""Components that can be used in pipelines"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import functools
import logging


@dataclass
class Component:
    func: Callable
    next: Callable | None = None
    prev: Callable | None = None

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def component(description: str):
    """
    Returns a decorator, which in turn returns a transformed function which,
    when called, returns a Component whose function is the functools.partial of the
    original function, plus a little logging
    """

    def decorator(func):
        @functools.wraps(
            func, assigned=("__module__", "__name__", "__qualname__", "__doc__")
        )
        def f(*args, **kwargs) -> Component:
            partial = functools.partial(func, *args, **kwargs)

            def inner(*args, **kwargs):
                logging.info(description)
                return partial(*args, **kwargs)

            return Component(inner)

        return f

    return decorator
