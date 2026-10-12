import pytest
from linked_list import LinkedList


def make(*values):
    ll = LinkedList()
    for v in values:
        ll.push_back(v)
    return ll


def test_empty_list():
    ll = LinkedList()
    assert len(ll) == 0
    assert ll.head is None and ll.tail is None
    assert repr(ll) == "(empty)"


def test_push_front_reverses_order():
    ll = LinkedList()
    for v in (1, 2, 3):
        ll.push_front(v)
    assert list(ll) == [3, 2, 1]
    assert ll.tail.value == 1


def test_push_back_keeps_order():
    ll = make(1, 2, 3)
    assert list(ll) == [1, 2, 3]
    assert repr(ll) == "1 -> 2 -> 3"


def test_pop_front_and_back():
    ll = make(1, 2, 3)
    assert ll.pop_front() == 1
    assert ll.pop_back() == 3
    assert list(ll) == [2]
    assert ll.head is ll.tail
    assert ll.pop_back() == 2
    assert ll.head is None and ll.tail is None   # fully empty again


def test_get():
    ll = make("a", "b", "c")
    assert ll.get(0) == "a"
    assert ll.get(2) == "c"


def test_insert_front_middle_end():
    ll = make(2, 4)
    ll.insert(0, 1)
    ll.insert(2, 3)
    ll.insert(4, 5)
    assert list(ll) == [1, 2, 3, 4, 5]
    assert ll.tail.value == 5


def test_delete_value_head_middle_tail():
    ll = make(1, 2, 3, 4)
    assert ll.delete_value(1)           # head
    assert ll.delete_value(3)           # middle
    assert ll.delete_value(4)           # tail -> tail pointer must move back
    assert list(ll) == [2]
    assert ll.tail.value == 2
    ll.push_back(9)                     # proves tail is still correct
    assert list(ll) == [2, 9]


def test_delete_value_missing():
    ll = make(1, 2)
    assert not ll.delete_value(42)
    assert len(ll) == 2


def test_search():
    ll = make(5, 6, 7)
    assert ll.search(7) == 2
    assert ll.search(8) == -1


@pytest.mark.parametrize("op", [
    lambda l: l.get(3),
    lambda l: l.insert(5, 0),
])
def test_out_of_range_raises(op):
    with pytest.raises(IndexError):
        op(make(1, 2, 3))


@pytest.mark.parametrize("op", ["pop_front", "pop_back", "peek_front"])
def test_empty_operations_raise(op):
    with pytest.raises(IndexError):
        getattr(LinkedList(), op)()
