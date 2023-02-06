from mymltoolkit import component, Component, Task


@component
def foo(a=None, b=None, *, c=3):
    """Add a, b and c"""
    if not (a and b):
        return
    return a + b + c


@component
def bar(a=None):
    """Divide a by 2, 42"""
    if not a:
        return
    return a / 2, 42


@component
def baz(a=None, b=None):
    """Add a and b"""
    if not (a and b):
        return
    return a + b


def test_component():
    assert isinstance(foo(), Component)
    assert foo(c=1)(1, 2) == 4


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
