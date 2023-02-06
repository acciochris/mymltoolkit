"""My personal machine learning toolkit"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any
from typing_extensions import ParamSpec
from collections.abc import Iterator

import functools


__version__ = "0.1.0"
__all__ = ("component", "Component", "ComponentList", "Task")

P = ParamSpec("P")


@dataclass
class Component:
    func: Callable
    name: str | None = None
    description: str | None = None
    next: Component | None = None
    prev: Component | None = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"

    def __or__(self, other: Component) -> ComponentList:
        if isinstance(other, Component):
            return ComponentList(self, self) | other
        return NotImplemented


def component(func: Callable[P, Any]) -> Callable[P, Component]:
    @functools.wraps(
        func, assigned=("__module__", "__name__", "__qualname__", "__doc__")
    )  # HACK: All components need to declare their positional arguments as optional
    def inner(*args: P.args, **kwargs: P.kwargs) -> Component:
        partial = functools.partial(func, *args, **kwargs)

        return Component(partial, func.__name__, func.__doc__)

    return inner


@dataclass
class ComponentList:
    first: Component
    last: Component

    def add_after(self, other: Component) -> ComponentList:
        self.last.next = other
        other.prev = self.last
        return ComponentList(self.first, other)

    def add_before(self, other: Component) -> ComponentList:
        self.first.prev = other
        other.next = self.first
        return ComponentList(other, self.last)

    def concat(self, other: ComponentList) -> ComponentList:
        self.last.next = other.first
        other.first.prev = self.last
        return ComponentList(self.first, other.last)

    def __or__(self, other: Component | ComponentList) -> ComponentList:
        if isinstance(other, Component):
            return self.add_after(other)
        if isinstance(other, ComponentList):
            return self.concat(other)
        return NotImplemented

    def __ror__(self, other: Component) -> ComponentList:
        if isinstance(other, Component):
            return self.add_before(other)
        return NotImplemented

    def __iter__(self) -> Iterator[Component]:
        yield self.first
        current = self.first
        while current.next is not None:
            yield current.next
            current = current.next

    def reverse_iter(self) -> Iterator[Component]:
        yield self.last
        current = self.last
        while current.prev is not None:
            yield current.prev
            current = current.prev

    def __len__(self) -> int:
        return len(list(iter(self)))

    def __str__(self) -> str:
        return " -> ".join([component.name or "(unnamed)" for component in self])

    def to_task(self, name: str | None = None, description: str | None = None) -> Task:
        return Task(self, name, description)


@dataclass
class Task:
    components: ComponentList
    name: str | None = None
    description: str | None = None
    _indent: int = field(default=0, init=False)

    def run(*args: Any, **kwargs: Any) -> Any:
        pass
