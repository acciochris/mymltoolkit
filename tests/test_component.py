from mymltoolkit import component, Component


@component
def foo(a, b, *, c=3):
    return a + b + c


@component
def bar(a):
    return a / 2, 42


@component
def baz(a, b):
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
