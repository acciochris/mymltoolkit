from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Callable, Any
from typing_extensions import ParamSpec, Protocol, TypeAlias
from collections.abc import Iterator, Iterable

from loguru import logger


__all__ = ("component", "Component", "ComponentList", "Task")

P = ParamSpec("P")
ComponentLike: TypeAlias = "Component | ComponentList | Task"


class ClassComponent(Protocol[P]):
    def __init__(self, *args: P.args, **kwargs: P.kwargs):
        ...


def _identity(*args: Any, **kwargs: Any) -> Any:
    return args if len(args) > 1 else args[0]


@dataclass
class Component:
    func: Callable
    inverse_func: Callable = _identity
    name: str | None = None
    description: str | None = None
    next: Component | None = None
    prev: Component | None = None

    def __str__(self) -> str:
        if not self.name:
            return ""
        if not self.description:
            return self.name
        return f"{self.name}: {self.description}"

    def __or__(self, other: Component) -> ComponentList:
        if isinstance(other, Component):
            return ComponentList(self, self) | other
        return NotImplemented

    def to_task(self) -> Task:
        return ComponentList(self, self).to_task()


def component(func: Callable[P, Any]) -> Callable[P, Component]:
    """Generate a component from `func` (there is no way to specify `inverse_func`)"""

    @functools.wraps(
        func, assigned=("__module__", "__name__", "__qualname__", "__doc__")
    )  # HACK: All components need to declare their positional arguments as optional
    def inner(*args: P.args, **kwargs: P.kwargs) -> Component:
        partial = functools.partial(func, *args, **kwargs)

        return Component(partial, name=func.__name__, description=func.__doc__)

    return inner


def class_component(cls: type[ClassComponent[P]]) -> Callable[P, Component]:
    """Generate a component from `cls`"""

    if not hasattr(cls, "__call__"):
        raise TypeError("`cls` must have __call__ defined")

    @functools.wraps(
        cls, assigned=("__module__", "__name__", "__qualname__", "__doc__")
    )
    def inner(*args: P.args, **kwargs: P.kwargs) -> Component:
        instance = cls(*args, **kwargs)

        return Component(
            instance.__call__,  # type: ignore
            getattr(instance, "inverse", _identity),
            name=cls.__name__,
            description=cls.__doc__,
        )

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
        while current.next:
            yield current.next
            current = current.next

    def reverse_iter(self) -> Iterator[Component]:
        yield self.last
        current = self.last
        while current.prev:
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

    def __call__(
        self, *args: Any, indent: int = 2, _level: int = 0
    ) -> Any:  # _level is the indentation level
        for component in self.components:
            logger.info(
                "{indent}Running {component}",
                component=component,
                indent=" " * _level * indent,
            )

            # Ensure args is an iterable suitable for unpacking
            if not isinstance(args, Iterable):
                args = (args,)

            args = component.func(*args, indent=indent, _level=_level + 1)

        return args

    def inverse(self, *args: Any, indent: int = 2, _level: int = 0) -> Any:
        for component in self.components.reverse_iter():
            logger.info(
                "{indent}Inversely running {component}",
                component=component,
                indent=" " * _level * indent,
            )

            # Ensure args is an iterable suitable for unpacking
            if not isinstance(args, Iterable):
                args = (args,)

            args = component.inverse_func(*args, indent=indent, _level=_level + 1)

        return args

    def as_component(self) -> Component:
        return Component(
            self,
            self.inverse,
            name=f"subtask {self.name}" if self.name else "subtask",
            description=self.description,
        )

    def __or__(self, other: ComponentLike) -> ComponentList:
        return self.as_component() | other

    def __ror__(self, other: ComponentLike) -> ComponentList:
        return other | self.as_component()

    def __str__(self) -> str:
        if not self.name:
            return "task"
        if not self.description:
            return f"task {self.name}"
        return f"task {self.name}: {self.description}"
