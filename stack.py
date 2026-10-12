"""
Stack (LIFO: Last In, First Out)
================================

IDEA
----
Think of a stack of plates: you only ever touch the TOP plate.
  push(x) -> put a plate on top
  pop()   -> take the top plate off
  peek()  -> look at the top plate without removing it

A stack is an *abstract* data type: it says WHAT operations exist, not HOW
they're stored. So we build it twice, on top of our two structures, and the
trick in both is to put the "top" where that structure is fastest:

  ArrayStack       top = END of the array    (append / pop at end are O(1))
  LinkedListStack  top = HEAD of the list    (push_front / pop_front are O(1))

If you put the top at the wrong end (front of an array, or tail of a singly
linked list) pop becomes O(n). Try it as an exercise and benchmark it!

BIG-O: push, pop, peek, is_empty are all O(1) in both versions
(ArrayStack.push is O(1) *amortized* because of occasional resizes).

Real uses: undo history, browser back button, function calls (the "call
stack"), checking matching brackets, depth-first search.
"""

from dynamic_array import DynamicArray
from linked_list import LinkedList


class ArrayStack:
    def __init__(self):
        self._items = DynamicArray()

    def push(self, value):
        self._items.append(value)               # O(1) amortized

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()                # O(1)

    def peek(self):
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._items.get(len(self._items) - 1)   # O(1)

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)


class LinkedListStack:
    def __init__(self):
        self._items = LinkedList()

    def push(self, value):
        self._items.push_front(value)           # O(1)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop_front()          # O(1)

    def peek(self):
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._items.peek_front()         # O(1)

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)
