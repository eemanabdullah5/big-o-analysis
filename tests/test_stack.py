import pytest
from stack import ArrayStack, LinkedListStack

# Both stacks must behave identically, so every test runs on both.
STACKS = [ArrayStack, LinkedListStack]


@pytest.mark.parametrize("Stack", STACKS)
def test_lifo_order(Stack):
    s = Stack()
    for v in (1, 2, 3):
        s.push(v)
    assert [s.pop(), s.pop(), s.pop()] == [3, 2, 1]
    assert s.is_empty()


@pytest.mark.parametrize("Stack", STACKS)
def test_peek_does_not_remove(Stack):
    s = Stack()
    s.push("x")
    assert s.peek() == "x"
    assert len(s) == 1


@pytest.mark.parametrize("Stack", STACKS)
def test_many_items(Stack):
    s = Stack()
    for i in range(1000):
        s.push(i)
    assert len(s) == 1000
    assert s.pop() == 999


@pytest.mark.parametrize("Stack", STACKS)
@pytest.mark.parametrize("op", ["pop", "peek"])
def test_empty_raises(Stack, op):
    with pytest.raises(IndexError):
        getattr(Stack(), op)()


@pytest.mark.parametrize("Stack", STACKS)
@pytest.mark.parametrize("text, ok", [
    ("()", True), ("{[()]}", True), ("([]{})", True), ("", True),
    ("(]", False), ("((", False), ("())", False), ("{[(])}", False),
])
def test_bracket_checker(Stack, text, ok):
    """A classic real use of a stack: matching brackets."""
    pairs = {")": "(", "]": "[", "}": "{"}
    s = Stack()
    valid = True
    for ch in text:
        if ch in "([{":
            s.push(ch)
        elif ch in pairs:
            if s.is_empty() or s.pop() != pairs[ch]:
                valid = False
                break
    valid = valid and s.is_empty()
    assert valid == ok
