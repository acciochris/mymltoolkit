"""My machine learning toolkit"""

from __future__ import annotations

from typing import Any
import sys

from mymltoolkit.component import (
    class_component,
    component,
    SupportsTask,
)

from loguru import logger

# Plotting
import seaborn.relational as _rel
import seaborn.distributions as _dis
import seaborn.categorical as _cat
import seaborn.axisgrid as _grid


__version__ = "0.1.0"
__all__ = [
    "setup_logging",
    # Plotting
    "relplot",
    "scatterplot",
    "lineplot",
    "displot",
    "histplot",
    "kdeplot",
    "ecdfplot",
    "rugplot",
    "catplot",
    "stripplot",
    "swarmplot",
    "boxplot",
    "violinplot",
    "pointplot",
    "barplot",
]


def setup_logging(format: str = "{time:HH:mm:ss} | {message}", remove: bool = True):
    """Enable logging for mymltoolkit"""
    logger.enable("mymltoolkit")
    if remove:
        logger.remove()
    logger.add(
        sys.stderr,
        format=format,
    )


##############
# Components #
##############

###########################
# Plotting (with seaborn) #
###########################

relplot = component(_rel.relplot)
scatterplot = component(_rel.scatterplot)
lineplot = component(_rel.lineplot)
displot = component(_dis.displot)
histplot = component(_dis.histplot)
kdeplot = component(_dis.kdeplot)
ecdfplot = component(_dis.ecdfplot)
rugplot = component(_dis.rugplot)
catplot = component(_cat.catplot)
stripplot = component(_cat.stripplot)
swarmplot = component(_cat.swarmplot)
boxplot = component(_cat.boxplot)
violinplot = component(_cat.violinplot)
pointplot = component(_cat.pointplot)
barplot = component(_cat.barplot)
jointplot = component(_grid.jointplot)
pairplot = component(_grid.pairplot)

########
# Meta #
########


@class_component
class multi:
    """Execute a task for each argument"""

    def __init__(
        self,
        *tasks: SupportsTask | None,
    ):
        self.tasks = [task.to_task() if task else None for task in tasks]

    def __call__(
        self, *args: Any, indent: int = 2, _level: int = 0
    ) -> Any:  # _level is the indentation level
        if len(args) != len(self.tasks):
            raise ValueError(
                "the length of args must match the length of tasks specified"
            )

        outputs = []
        for i, (task, arg) in enumerate(zip(self.tasks, args)):
            if not task:
                outputs.append(arg)  # Do nothing
                continue

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
            if not task:
                outputs.append(arg)  # Do nothing
                continue

            logger.info(
                "{indent}Inversely running {task} for argument {i}",
                task=task,
                indent=" " * _level * indent,
                i=i,
            )

            outputs.append(task.inverse(arg, indent=indent, _level=_level + 1))

        return tuple(outputs)
