"""
Dynamic Array (a resizable array, like Python's built-in list)
==============================================================

IDEA
----
A real array is one fixed-size block of memory. Getting element i is instant
because the computer jumps straight to   start_address + i * element_size.

The problem: a fixed block can't grow. So a *dynamic* array does this:
  - keep a block with some spare room ("capacity")
  - when it's full, allocate a block TWICE as big and copy everything over

We simulate the raw memory block with a Python list of fixed length
(`[None] * capacity`) and never call .append() / .insert() on it. Everything
below is done by hand so you can see where the work (and the Big-O) comes from.

BIG-O SUMMARY  (n = number of elements)
---------------------------------------
  get(i) / set(i)      O(1)            direct jump to index
  append(x)            O(1) amortized  usually O(1); occasionally O(n) resize
  pop()                O(1)            remove from the end, nothing shifts
  insert(i, x)         O(n)            everything after i shifts right
  delete(i)            O(n)            everything after i shifts left
  search(x)            O(n)            may have to look at every element
"""


class DynamicArray:
    def __init__(self, capacity=4):
        self._capacity = capacity               # size of the memory block
        self._size = 0                          # how many slots are actually used
        self._data = [None] * capacity          # the "raw memory block"
        self.resize_count = 0                   # for curiosity: how often we grew

    # ------------------------------------------------------------------ basics
    def __len__(self):
        return self._size

    def __iter__(self):
        for i in range(self._size):
            yield self._data[i]

    def __repr__(self):
        return f"DynamicArray({list(self)})"

    def _check_index(self, index):
        if not 0 <= index < self._size:
            raise IndexError(f"index {index} out of range for size {self._size}")

    # ------------------------------------------------------------------ O(1)
    def get(self, index):
        """O(1): one direct jump, no matter how big the array is."""
        self._check_index(index)
        return self._data[index]

    def set(self, index, value):
        """O(1): same reasoning as get()."""
        self._check_index(index)
        self._data[index] = value

    def append(self, value):
        """O(1) amortized.

        Most appends just write into the next free slot -> O(1).
        When the block is full we resize (copy n items) -> O(n), BUT because we
        double the capacity each time, resizes get rarer and rarer. Spread over
        many appends the average cost per append stays constant.
        """
        if self._size == self._capacity:
            self._resize(2 * self._capacity)
        self._data[self._size] = value
        self._size += 1

    def pop(self):
        """O(1): remove the last element. Nothing has to shift."""
        if self._size == 0:
            raise IndexError("pop from empty array")
        self._size -= 1
        value = self._data[self._size]
        self._data[self._size] = None           # let Python free the object
        return value

    # ------------------------------------------------------------------ O(n)
    def insert(self, index, value):
        """O(n): every element from `index` onwards moves one slot right.

        Worst case is index 0: all n elements move.
        """
        if not 0 <= index <= self._size:        # index == size means "at the end"
            raise IndexError(f"index {index} out of range for insert")
        if self._size == self._capacity:
            self._resize(2 * self._capacity)
        # shift right, starting from the back so we don't overwrite anything
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def delete(self, index):
        """O(n): every element after `index` moves one slot left to fill the gap."""
        self._check_index(index)
        value = self._data[index]
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._size -= 1
        self._data[self._size] = None
        return value

    def search(self, value):
        """O(n): linear search. Returns the index, or -1 if not found."""
        for i in range(self._size):
            if self._data[i] == value:
                return i
        return -1

    # ------------------------------------------------------------------ helper
    def _resize(self, new_capacity):
        """O(n): allocate a bigger block and copy every element across."""
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity
        self.resize_count += 1
