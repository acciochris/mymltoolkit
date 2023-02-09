"""My machine learning toolkit"""

from __future__ import annotations

from typing import Any

from mymltoolkit.component import (
    Component,
    ComponentList,
    Task,
    class_component,
    _identity,
    ComponentLike,
)

from loguru import logger

__version__ = "0.1.0"


@class_component
class multi:
    """Execute a task for each argument"""

    def __init__(
        self,
        *tasks: ComponentLike | None,
    ):
        new_tasks: list[Task] = []
        for task in tasks:
            if not task:
                identity = Component(
                    _identity, name="identity", description="Do nothing"
                )
                new_tasks.append(
                    ComponentList(identity, identity).to_task(
                        identity.name, identity.description
                    )
                )
                continue
            if isinstance(task, Component):
                new_tasks.append(
                    ComponentList(task, task).to_task(task.name, task.description)
                )
                continue
            if isinstance(task, ComponentList):
                new_tasks.append(task.to_task())
                continue
            if isinstance(task, Task):
                new_tasks.append(task)
                continue

            raise TypeError(
                "tasks must be of type Component | ComponentList | Task | None"
            )

        self.tasks = tuple(new_tasks)

    def __call__(
        self, *args: Any, indent: int = 2, _level: int = 0
    ) -> Any:  # _level is the indentation level
        if len(args) != len(self.tasks):
            raise ValueError(
                "the length of args must match the length of tasks specified"
            )

        outputs = []
        for i, (task, arg) in enumerate(zip(self.tasks, args)):
            logger.info(
                "{indent}Running {task} for argument {i}",
                task=task,
                indent=" " * _level * indent,
                i=i,
            )

            outputs.append(task(arg, indent=indent, _level=_level + 1))

        return tuple(outputs)

    def inverse(self, *args: Any, indent: int = 2, _level: int = 0) -> Any:
        if len(args) != len(self.tasks):
            raise ValueError(
                "the length of args must match the length of tasks specified"
            )

        outputs = []
        for i, (task, arg) in enumerate(zip(self.tasks, args)):
            logger.info(
                "{indent}Inversely running {task} for argument {i}",
                task=task,
                indent=" " * _level * indent,
                i=i,
            )

            outputs.append(task.inverse(arg, indent=indent, _level=_level + 1))

        return tuple(outputs)
