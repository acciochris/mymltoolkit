# `mymltoolkit`

My personal machine learning toolkit

**Warning**: The API of this library may be unstable.

## Installation

```console
$ pip install git+https://github.com/acciochris/mymltoolkit
```

## Usage

Three classes and two decorators, namely `Component`, `ComponentList`, `Task`, `component` and
`class_component` comprise the basis of this library.

### `Component`

A `Component` is a transformation (and its inverse transformation). It should only be instantiated
**on demand** (see `component` and `class_component`) and should only be used by transforming it
into a `Task`.

### `ComponentList`

A list of `Component`s, joined together by the pipe (`|`) operator.

### `Task`

An executable task, produced by calling `.to_task()` on a `Component` or a `ComponentList`.

### `component`

A function decorator that transforms a function into a corresponding component generator.

There are a few subtleties when using this decorator.

### `class_component`

A class decorator that transforms a class into a corresponding component generator.

### Example

```python
from __future__ import annotations

from mymltoolkit.component import component

@component
def add(  # The function name is taken as the name of the component
    a: int | None = None,  # Subtlety 1: all positional arguments should have default values
    b: int | None = None,  # (why: type hints)
    *,  # Best practice: use keyword-only arguments as config params
    use_subtract_instead: bool = False,
    **extra,  # Subtlety 2: must have additional keyword arguments (why: indent and _level (see below))
) -> int:
    """Add (or subtract) two ints"""  # The __doc__ is used as the description of the component
    return a + b if not use_subtract_instead else a - b

# Usage
task = add(use_subtract_instead=True).to_task()
task(2, 3)  # -1

@class_component
class subtract:  # Class name as name of the component
    """Subtract two ints (perhaps twice)"""  # __doc__ as description

    def __init__(self, b: int = 2, twice: bool = False):
        self.twice = twice

    def __call__(self, a: int, **extra):  # No longer need Subtlety 1, but Subtlety 2 still holds
        return a - self.b if not self.twice else a - self.b * 2

    def inverse(self, a: int, **extra):  # Inverse transform (optional)
        return a + self.b if not self.twice else a + self.b * 2

task2 = (add() | subtract(3, twice=True)).to_task()
task2(3, 3)  # 0
task2.inverse(0)  # 6! For components without an inverse, the identity function is used
```

**Warning**: Do not reuse a `Component`! `Component`s contain information such as which function
should be called next in a chain, so they must not be reused. Turn it into a `Task` instead.
