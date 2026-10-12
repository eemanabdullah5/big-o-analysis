import pytest
from dynamic_array import DynamicArray


def make(*values):
    arr = DynamicArray()
    for v in values:
        arr.append(v)
    return arr


def test_empty_array():
    arr = DynamicArray()
    assert len(arr) == 0
    assert list(arr) == []


def test_append_and_get():
    arr = make(10, 20, 30)
    assert len(arr) == 3
    assert arr.get(0) == 10
    assert arr.get(2) == 30


def test_set_overwrites():
    arr = make(1, 2, 3)
    arr.set(1, 99)
    assert list(arr) == [1, 99, 3]


def test_grows_past_initial_capacity():
    arr = DynamicArray(capacity=2)
    for i in range(100):
        arr.append(i)
    assert len(arr) == 100
    assert list(arr) == list(range(100))
    # capacity doubles 2 -> 4 -> 8 -> 16 -> 32 -> 64 -> 128  = 6 resizes
    assert arr.resize_count == 6


def test_insert_front_middle_end():
    arr = make(2, 4)
    arr.insert(0, 1)        # front
    arr.insert(2, 3)        # middle
    arr.insert(4, 5)        # end
    assert list(arr) == [1, 2, 3, 4, 5]


def test_delete_shifts_left():
    arr = make(1, 2, 3, 4)
    assert arr.delete(1) == 2
    assert list(arr) == [1, 3, 4]
    assert arr.delete(0) == 1
    assert arr.delete(1) == 4
    assert list(arr) == [3]


def test_pop_returns_last():
    arr = make(1, 2, 3)
    assert arr.pop() == 3
    assert list(arr) == [1, 2]


def test_search():
    arr = make("a", "b", "c")
    assert arr.search("c") == 2
    assert arr.search("z") == -1


@pytest.mark.parametrize("op", [
    lambda a: a.get(5),
    lambda a: a.get(-1),
    lambda a: a.set(3, 0),
    lambda a: a.delete(3),
    lambda a: a.insert(4, 0),
])
def test_out_of_range_raises(op):
    with pytest.raises(IndexError):
        op(make(1, 2, 3))


def test_pop_empty_raises():
    with pytest.raises(IndexError):
        DynamicArray().pop()
