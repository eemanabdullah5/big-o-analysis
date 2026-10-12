"""
Singly Linked List
==================

IDEA
----
Instead of one block of memory, every element lives in its own little box
(a Node). Each node holds a value and a pointer to the NEXT node.

    head -> [10 | •] -> [20 | •] -> [30 | None]   <- tail

  + Adding/removing at the FRONT is instant: just move the head pointer.
  + With a tail pointer, adding at the BACK is also instant.
  - There is no "jump to index i". To reach node i you must walk i steps.
  - Removing the LAST node is slow in a *singly* linked list, because to update
    `tail` we need the node BEFORE it, and we can only walk forwards from head.

BIG-O SUMMARY  (n = number of elements)
---------------------------------------
  push_front(x)        O(1)   new node points to old head
  push_back(x)         O(1)   thanks to the tail pointer
  pop_front()          O(1)   move head one step
  pop_back()           O(n)   must walk to the second-to-last node
  get(i)               O(n)   walk i steps
  insert(i, x)         O(n)   walk to position i-1, then relink (relinking is O(1))
  delete_value(x)      O(n)   walk until found
  search(x)            O(n)   walk until found

Compare with DynamicArray: array wins at get(i), list wins at the front.
"""


class Node:
    __slots__ = ("value", "next")               # small memory optimisation

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    # ------------------------------------------------------------------ basics
    def __len__(self):
        return self._size

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current.value
            current = current.next

    def __repr__(self):
        return " -> ".join(str(v) for v in self) or "(empty)"

    # ------------------------------------------------------------------ O(1)
    def push_front(self, value):
        """O(1): new node points at the current head, then becomes the head."""
        node = Node(value, self.head)
        self.head = node
        if self.tail is None:                   # list was empty
            self.tail = node
        self._size += 1

    def push_back(self, value):
        """O(1): link the new node after the tail. No walking needed."""
        node = Node(value)
        if self.tail is None:                   # list was empty
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def pop_front(self):
        """O(1): move head one step forward."""
        if self.head is None:
            raise IndexError("pop from empty list")
        value = self.head.value
        self.head = self.head.next
        if self.head is None:                   # list became empty
            self.tail = None
        self._size -= 1
        return value

    def peek_front(self):
        """O(1)."""
        if self.head is None:
            raise IndexError("peek at empty list")
        return self.head.value

    # ------------------------------------------------------------------ O(n)
    def pop_back(self):
        """O(n): we need the node *before* tail, so we walk from head."""
        if self.head is None:
            raise IndexError("pop from empty list")
        if self.head is self.tail:              # only one node
            return self.pop_front()
        current = self.head
        while current.next is not self.tail:    # walk to second-to-last
            current = current.next
        value = self.tail.value
        current.next = None
        self.tail = current
        self._size -= 1
        return value

    def get(self, index):
        """O(n): no direct jump; walk `index` steps from the head."""
        if not 0 <= index < self._size:
            raise IndexError(f"index {index} out of range for size {self._size}")
        current = self.head
        for _ in range(index):
            current = current.next
        return current.value

    def insert(self, index, value):
        """O(n) to find the spot, O(1) to relink."""
        if not 0 <= index <= self._size:
            raise IndexError(f"index {index} out of range for insert")
        if index == 0:
            return self.push_front(value)
        if index == self._size:
            return self.push_back(value)
        prev = self.head
        for _ in range(index - 1):
            prev = prev.next
        prev.next = Node(value, prev.next)
        self._size += 1

    def delete_value(self, value):
        """O(n): remove the first node holding `value`. Returns True if removed."""
        prev, current = None, self.head
        while current is not None:
            if current.value == value:
                if prev is None:                # deleting the head
                    self.head = current.next
                else:
                    prev.next = current.next
                if current is self.tail:        # deleting the tail
                    self.tail = prev
                self._size -= 1
                return True
            prev, current = current, current.next
        return False

    def search(self, value):
        """O(n): returns the index of `value`, or -1."""
        for i, v in enumerate(self):
            if v == value:
                return i
        return -1
