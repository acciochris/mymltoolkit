from mymltoolkit import component, Component


@component
def foo(a=None, b=None, *, c=3):
    if not (a and b):
        return
    return a + b + c


@component
def bar(a=None):
    if not a:
        return
    return a / 2, 42


@component
def baz(a=None, b=None):
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
