import mymltoolkit as mlt
from mymltoolkit.component import component, class_component, Component, Task
from mymltoolkit import multi, agg, each


import pytest


mlt.setup_logging("{message}")


@component
def foo(a=None, b=None, *, c=3, **extra):
    """Add a, b and c"""
    if not (a and b):
        return
    return a + b + c


@component
def bar(a=None, **extra):
    """Divide a by 2, 42"""
    if not a:
        return
    return a // 2, 42


@component
def baz(a=None, b=None, **extra):
    """Add a and b"""
    if not (a and b):
        return
    return a + b


@component
def two_and_three(**extra):
    return 2, 3


@component
def product(a=None, b=None, **extra):
    if not (a and b):
        return 1

    return a * b


@component
def quotient(a=None, b=None, **extra):
    if not (a and b):
        return 1

    return a / b


@class_component
class add:
    def __init__(self, a=2):
        self.a = a

    def __call__(self, b, **extra):
        return self.a + b

    def inverse(self, c, **extra):
        return c - self.a


@class_component
class subtract:
    def __init__(self, a=2):
        self.a = a

    def __call__(self, b, **extra):
        return b - self.a

    def inverse(self, c, **extra):
        return c + self.a


def test_component():
    assert isinstance(foo(), Component)
    assert foo(c=1).func(1, 2) == 4


def test_component_list():
    list1 = foo(c=2) | bar() | baz()
    list2 = foo(c=2) | (bar() | baz())

    assert str(list1) == "foo -> bar -> baz"
    assert str(list1) == str(list2)
    assert list(list1) == list(reversed(list(list1.reverse_iter())))
    assert isinstance(list1.to_task(), Task)


def test_task():
    task = Task(foo(c=3) | bar() | baz(), "quux", "More quux")

    assert task(1, 2) == 45


def test_subtask():
    task = Task(foo(c=3) | bar() | baz(), "quux", "More quux")
    supertask = (bar(6) | task).to_task("supertask")
    supersupertask = (supertask | bar()).to_task()

    assert supertask() == 66
    assert supersupertask(indent=4) == (33, 42)


def test_inverse_component():
    assert isinstance(add(a=3), Component)
    assert add(a=3).func(2) == 5
    assert add(a=3).inverse_func(5) == 2

    add2 = add(a=5)

    assert add2.func(2) == 7
    assert add2.inverse_func(7) == 2

    add_2_subtract_5 = (add(2) | subtract(5)).to_task("add_2_subtract_5")

    assert add_2_subtract_5(5) == 2
    assert add_2_subtract_5.inverse(5) == 8

    identity = (add(3) | add_2_subtract_5).to_task("identity")

    assert identity(159) == 159
    assert identity.inverse(-50) == -50


def test_multicomponent():
    multi1 = multi(add(3), subtract(6)).to_task()

    assert multi1(5, 7) == (8, 1)
    with pytest.raises(ValueError):
        multi1(5, 6, 7)

    multi2 = multi1 | baz()
    multi3 = bar() | multi1
    multi4 = multi3.to_task("multi3") | multi(subtract(5), add(2))
    identity = multi1 | multi(subtract(3), add(6))

    assert multi2.to_task()(5, 7) == 9
    assert multi3.to_task()(6) == (6, 36)
    assert multi4.to_task()(6) == (1, 38)
    assert identity.to_task()(5, 5) == (5, 5)

    identity2 = multi(
        add(3) | subtract(3),
        (add(4) | subtract(4)).to_task("identity", "Do nothing"),
    )

    assert identity2.func(5, 5) == (5, 5)

    identity3 = multi(None, None)

    assert identity3.func(5, 5) == (5, 5)

    assert multi2.to_task().inverse(8, 1) == (5, 7)
    assert identity2.inverse_func(5, 5) == (5, 5)


def test_aggregate():
    task = (two_and_three() | agg(product(), quotient())).to_task()

    assert task() == (6, 2 / 3)


def test_each():
    task = (two_and_three() | each(add())).to_task()

    assert task() == (4, 5)
