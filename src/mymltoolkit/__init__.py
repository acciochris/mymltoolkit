"""My machine learning toolkit"""

from __future__ import annotations

from typing import Any
import sys

from mymltoolkit.component import (
    class_component,
    component,
    SupportsTask,
    _info,
)

from loguru import logger

# Plotting
import seaborn.relational as _rel
import seaborn.distributions as _dis
import seaborn.categorical as _cat
import seaborn.axisgrid as _grid
import seaborn.matrix as _mat
import seaborn.regression as _reg


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

_LOGGING_LEVEL: int = -1


def setup_logging(
    format: str = "{time:HH:mm:ss} | {message}", *, remove: bool = True, level: int = -1
):
    """Enable logging for mymltoolkit

    `format`: format string
    `remove`: remove the default stderr logger
    `level`: number of logging levels (-1 for all)
    """
    global _LOGGING_LEVEL

    logger.enable("mymltoolkit")
    if remove:
        logger.remove()
    logger.add(
        sys.stderr,
        format=format,
    )
    _LOGGING_LEVEL = level


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
heatmap = component(_mat.heatmap)
clustermap = component(_mat.clustermap)
lmplot = component(_reg.lmplot)
regplot = component(_reg.regplot)
residplot = component(_reg.regplot)

########
# Meta #
########


@class_component
class multi:
    """Perform a transformation for each argument"""

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

            _info(
                "Running {task} for argument {i}",
                task=task,
                i=i,
                indent=indent,
                _level=_level,
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

            _info(
                "Inversely running {task} for argument {i}",
                task=task,
                i=i,
                indent=indent,
                _level=_level,
            )

            outputs.append(task.inverse(arg, indent=indent, _level=_level + 1))

        return tuple(outputs)


@class_component
class agg:
    """Aggregate multiple transformations over the same input"""

    def __init__(self, *tasks: SupportsTask):
        self.tasks = [task.to_task() for task in tasks]

    def __call__(
        self, *args: Any, indent: int = 2, _level: int = 0
    ) -> Any:  # _level is the indentation level
        outputs = []
        for i, task in enumerate(self.tasks):
            _info(
                "Running {task} {i}",
                task=task,
                i=i,
                indent=indent,
                _level=_level,
            )

            outputs.append(task(*args, indent=indent, _level=_level + 1))

        return tuple(outputs)


@class_component
class each:
    """Apply a transformation on each of the arguments"""

    def __init__(self, task: SupportsTask) -> None:
        self.task = task.to_task()

    def __call__(
        self, *args: Any, indent: int = 2, _level: int = 0
    ) -> Any:  # _level is the indentation level
        outputs = []
        for i, arg in enumerate(args):
            _info(
                "Running {task} for argument {i}",
                task=self.task,
                i=i,
                indent=indent,
                _level=_level,
            )

            outputs.append(self.task(arg, indent=indent, _level=_level + 1))

        return tuple(outputs)
