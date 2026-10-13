"""
Benchmark: does the measured time match the Big-O we predicted?
===============================================================
HOW IT WORKS
------------
For every operation we:
  1. build a structure with n elements, for n = 1k, 2k, 4k ... 64k
  2. time the operation (repeated many times, best of several runs)
  3. look at how the time grows when n doubles
THE TRICK FOR CHECKING BIG-O
----------------------------
If time = c * n^k, then  log(time) = k * log(n) + log(c).
So on a log-log plot the points form a straight line whose SLOPE is k:
    slope ~ 0  -> time doesn't grow with n      -> O(1)
    slope ~ 1  -> time doubles when n doubles   -> O(n)
    slope ~ 2  -> time x4 when n doubles        -> O(n^2)
We fit that slope with least squares and compare it to our prediction.
Run:  python benchmark.py
Out:  results/results.md   (table for the README)
      results/*.png        (graphs)
"""

import math
import os
import time
from dynamic_array import DynamicArray
from linked_list import LinkedList
from stack import ArrayStack, LinkedListStack

SIZES = [1_000, 2_000, 4_000, 8_000, 16_000, 32_000, 64_000]
REPEATS = 7  # take the best of 7 runs (least disturbed by the OS)
OUT_DIR = "results"


# ---------------------------------------------------------------- builders


def build_array(n):
    a = DynamicArray()
    for i in range(n):
        a.append(i)
    return a


def build_list(n):
    ll = LinkedList()
    for i in range(n):
        ll.push_back(i)
    return ll


def build_stack(cls, n):
    s = cls()
    for i in range(n):
        s.push(i)
    return s


# ---------------------------------------------------------------- operations
# Each entry: (structure, operation, expected Big-O, setup(n), op(obj, n), k)
#   setup builds a fresh structure of size n (NOT timed); pop tests build
#   n + k elements so we never pop from an empty structure
#   op is called k times and timed; we report time per single call
# O(1) ops are so fast that we repeat them more (k larger) so the timer can
# actually see them. k does not change the slope, only the precision.
FAST, SLOW = 2_000, 20
# Amortized ops (append / ArrayStack.push) are measured as "n appends starting
# from EMPTY, divided by n". Timing only 2,000 appends on top of n elements is
# NOT amortized: if a resize lands in that window, its O(n) copy is divided by
# just 2,000 calls and append wrongly looks like O(n). (Try it: set k=FAST.)
PER_N = "n"
OPERATIONS = [
    # ---- DynamicArray
    (
        "DynamicArray",
        "get(middle)",
        "O(1)",
        build_array,
        lambda a, n: a.get(n // 2),
        FAST,
    ),
    (
        "DynamicArray",
        "append",
        "O(1)",
        lambda n: DynamicArray(),
        lambda a, n: a.append(0),
        PER_N,
    ),
    (
        "DynamicArray",
        "pop",
        "O(1)",
        lambda n: build_array(n + FAST),
        lambda a, n: a.pop(),
        FAST,
    ),
    (
        "DynamicArray",
        "insert(0)",
        "O(n)",
        build_array,
        lambda a, n: a.insert(0, -1),
        SLOW,
    ),
    (
        "DynamicArray",
        "delete(0)",
        "O(n)",
        build_array,
        lambda a, n: a.delete(0),
        SLOW,
    ),
    (
        "DynamicArray",
        "search(miss)",
        "O(n)",
        build_array,
        lambda a, n: a.search(-5),
        SLOW,
    ),
    # ---- LinkedList
    (
        "LinkedList",
        "push_front",
        "O(1)",
        build_list,
        lambda linked_list, n: linked_list.push_front(0),
        FAST,
    ),
    (
        "LinkedList",
        "push_back",
        "O(1)",
        build_list,
        lambda linked_list, n: linked_list.push_back(0),
        FAST,
    ),
    (
        "LinkedList",
        "pop_front",
        "O(1)",
        lambda n: build_list(n + FAST),
        lambda linked_list, n: linked_list.pop_front(),
        FAST,
    ),
    (
        "LinkedList",
        "pop_back",
        "O(n)",
        build_list,
        lambda linked_list, n: linked_list.pop_back(),
        SLOW,
    ),
    (
        "LinkedList",
        "get(middle)",
        "O(n)",
        build_list,
        lambda linked_list, n: linked_list.get(n // 2),
        SLOW,
    ),
    (
        "LinkedList",
        "search(miss)",
        "O(n)",
        build_list,
        lambda linked_list, n: linked_list.search(-5),
        SLOW,
    ),
    # ---- Stacks
    (
        "ArrayStack",
        "push",
        "O(1)",
        lambda n: ArrayStack(),
        lambda s, n: s.push(0),
        PER_N,
    ),
    (
        "ArrayStack",
        "pop",
        "O(1)",
        lambda n: build_stack(ArrayStack, n + FAST),
        lambda s, n: s.pop(),
        FAST,
    ),
    (
        "LinkedListStack",
        "push",
        "O(1)",
        lambda n: build_stack(LinkedListStack, n),
        lambda s, n: s.push(0),
        FAST,
    ),
    (
        "LinkedListStack",
        "pop",
        "O(1)",
        lambda n: build_stack(LinkedListStack, n + FAST),
        lambda s, n: s.pop(),
        FAST,
    ),
]


# ---------------------------------------------------------------- measuring


def time_per_call(setup, op, n, k):
    """Best-of-REPEATS time for ONE call of op on a structure of size n."""
    if k == PER_N:
        k = n
    best = math.inf
    for _ in range(REPEATS):
        obj = setup(n)  # fresh structure, not timed
        start = time.perf_counter()
        for _ in range(k):
            op(obj, n)
        best = min(best, time.perf_counter() - start)
    return best / k


def fit_slope(sizes, times):
    """Least-squares slope of log(time) against log(n)."""
    xs = [math.log(n) for n in sizes]
    ys = [math.log(t) for t in times]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den


def classify(slope):
    if slope < 0.35:
        return "O(1)"
    if 0.65 <= slope <= 1.35:
        return "O(n)"
    if 1.65 <= slope <= 2.35:
        return "O(n^2)"
    return "unclear"


# ---------------------------------------------------------------- report


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    results = []
    for struct, name, expected, setup, op, k in OPERATIONS:
        times = [time_per_call(setup, op, n, k) for n in SIZES]
        slope = fit_slope(SIZES, times)
        observed = classify(slope)
        match = "✅" if observed == expected else "❌"
        results.append((struct, name, expected, observed, slope, times, match))
        print(
            f"{struct:16} {name:14} expected {expected:5} "
            f"observed {observed:7} "
            f"slope {slope:5.2f}  {match}"
        )
    amortized = amortized_append_demo()
    write_markdown(results, amortized)
    plot(results)
    passed = sum(r[6] == "✅" for r in results)
    print(f"\n{passed}/{len(results)} operations match their predicted Big-O")


def amortized_append_demo():
    """Why append is O(1) *amortized*: average cost per append stays flat
    even though individual appends that trigger a resize cost O(n)."""
    rows = []
    for n in SIZES:
        a = DynamicArray()
        start = time.perf_counter()
        for i in range(n):
            a.append(i)
        total = time.perf_counter() - start
        rows.append((n, total / n * 1e9, a.resize_count))
    return rows


def write_markdown(results, amortized):
    head = (
        "| Structure | Operation | Expected | Observed | Slope | "
        + " | ".join(f"n={n // 1000}k" for n in SIZES)
        + " | Match |"
    )
    sep = "|" + "---|" * (6 + len(SIZES))
    lines = [
        "## Benchmark results (time per call, microseconds)",
        "",
        head,
        sep,
    ]
    for struct, name, exp, obs, slope, times, match in results:
        cells = " | ".join(f"{t * 1e6:.2f}" for t in times)
        lines.append(
            f"| {struct} | `{name}` | {exp} | {obs} | {slope:.2f} | {cells} | {match} |"
        )
    lines += [
        "",
        "## Amortized append (DynamicArray)",
        "",
        "| n appends | avg ns per append | resizes |",
        "|---|---|---|",
    ]
    for n, ns, r in amortized:
        lines.append(f"| {n:,} | {ns:.0f} | {r} |")
    with open(os.path.join(OUT_DIR, "results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def plot(results):
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping graphs (pip install matplotlib)")
        return
    for struct in dict.fromkeys(r[0] for r in results):
        rows = [r for r in results if r[0] == struct]
        fig, ax = plt.subplots(figsize=(7, 4.5))
        for _, name, exp, obs, slope, times, _ in rows:
            style = "-" if exp == "O(n)" else "--"
            ax.plot(
                SIZES,
                [t * 1e6 for t in times],
                style,
                marker="o",
                label=f"{name}  (expected {exp}, slope {slope:.2f})",
            )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("n (number of elements)")
        ax.set_ylabel("time per call (µs)")
        ax.set_title(f"{struct}: flat line = O(1), rising line = O(n)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(os.path.join(OUT_DIR, f"{struct}.png"), dpi=120)
        plt.close(fig)
    # head-to-head: the classic array vs linked list trade-off
    pick = {(r[0], r[1]): r[5] for r in results}
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for key, label in [
        (("DynamicArray", "get(middle)"), "array get(i)  O(1)"),
        (("LinkedList", "get(middle)"), "linked list get(i)  O(n)"),
        (("DynamicArray", "insert(0)"), "array insert at front  O(n)"),
        (("LinkedList", "push_front"), "linked list insert at front  O(1)"),
    ]:
        ax.plot(SIZES, [t * 1e6 for t in pick[key]], marker="o", label=label)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n (number of elements)")
    ax.set_ylabel("time per call (µs)")
    ax.set_title("Array vs Linked List: each wins at something different")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "array_vs_linked_list.png"), dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    main()
