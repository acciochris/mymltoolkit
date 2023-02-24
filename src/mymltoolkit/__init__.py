"""My machine learning toolkit"""

from __future__ import annotations

from typing import Any
import sys

from mymltoolkit.component import (
    Task,
    class_component,
    _identity,
)

from loguru import logger

__version__ = "0.1.0"


def setup_logging(format: str = "{time:HH:mm:ss} | {message}"):
    """Enable logging for mymltoolkit"""
    logger.enable("mymltoolkit")
    logger.remove()
    logger.add(
        sys.stderr,
        format=format,
    )


##############
# Components #
##############


@class_component
class multi:
    """Execute a task for each argument"""

    def __init__(
        self,
        *tasks: Task | None,
    ):
        self.tasks = [task or _identity for task in tasks]

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
