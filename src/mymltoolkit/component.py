"""Components that can be used in pipelines"""

from __future__ import annotations

from dataclasses import dataclass

import functools
import typing

if typing.TYPE_CHECKING:
    from typing import Callable, ParamSpec, Any

    P = ParamSpec("P")


@dataclass
class Component:
    func: Callable
    name: str | None = None
    description: str | None = None
    next: Component | None = None
    prev: Component | None = None

    def __call__(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)


def component(func: Callable[P, Any]):
    @functools.wraps(
        func, assigned=("__module__", "__name__", "__qualname__", "__doc__")
    )
    def inner(*args: P.args, **kwargs: P.kwargs) -> Component:
        partial = functools.partial(func, *args, **kwargs)

        return Component(partial, func.__name__, func.__doc__)

    return inner
