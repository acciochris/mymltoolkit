"""My personal machine learning toolkit"""

from __future__ import annotations

from dataclasses import dataclass

import functools
import typing

if typing.TYPE_CHECKING:
    from typing import Callable, Any

__version__ = "0.1.0"
__all__ = ("component", "Component", "ComponentList", "Task")


@dataclass
class Component:
    func: Callable
    name: str | None = None
    description: str | None = None
    next: Component | None = None
    prev: Component | None = None

    def __call__(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"

    def __or__(self, other: Component) -> ComponentList:
        if isinstance(other, Component):
            return ComponentList(self, self) | other
        return NotImplemented


def component(func: Callable):
    @functools.wraps(
        func, assigned=("__module__", "__name__", "__qualname__", "__doc__")
    )
    def inner(**kwargs) -> Component:
        partial = functools.partial(func, **kwargs)

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

    def __iter__(self):
        yield self.first
        current = self.first
        while current.next is not None:
            yield current.next
            current = current.next

    def reverse_iter(self):
        yield self.last
        current = self.last
        while current.prev is not None:
            yield current.prev
            current = current.prev

    def __len__(self):
        return len(list(iter(self)))

    def __str__(self):
        return " -> ".join([component.name or "(unnamed)" for component in self])


@dataclass
class Task:
    components: ComponentList
    name: str | None = None
    description: str | None = None
