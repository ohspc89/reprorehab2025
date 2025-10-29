# Week 6 — Control Flow & Functions
> (Originally Week 5 — schedule shifted after the special Week 4 session.)

---

## 🧭 Learning Objectives
By the end of this week, you should be able to:

- Write conditional statements using `if`, `elif`, and `else`
- Use `for` and `while` loops to repeat code efficiently
- Control loop behavior with `break` and `continue`
- Iterate cleanly with `enumerate()` and `zip()`
- Build your own functions with parameters, type hints, and return values
- Return **multiple values** from a function and unpack them
- Recognize when to switch from loops → comprehensions → NumPy vectorization

---

## 📂 Files in this Folder
| File | Description |
|------|--------------|
| [`Week5.py`](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week5/Week5.py) | Main notebook/script for the week. Walkthrough with explanations and mini-tasks. |
| [`Week5_assignment.py`](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week5/Week5_assignment.py) | Weekly assignment — practice tasks on control flow and functions. Submit this one. |

---

## 🧠 Overview
This week we bring structure and logic to your code.

Most programs combine three pillars:
1. **Decisions** — choosing *what* to do (`if / elif / else`, `match / case`)
2. **Repetition** — doing it *again* (`for`, `while`)
3. **Reuse** — packaging it for later (functions)

You’ll also meet some professional habits:
- add type hints (`str | None`)
- protect loops from infinite runs
- use vectorized NumPy operations for speed (`%timeit`)

---

## 🧩 Topics Covered
1. Conditional statements (`if`, `elif`, `else`, `match case`)
2. Boolean logic and truthiness (`0`, `''`, `[]`, etc.)
3. Loops:
   - `for` loops over lists, ranges, and dataframes
   - `while` loops with safe guards
   - `break` and `continue`
4. Pythonic iteration:
   - `enumerate(start=1)` instead of manual counters
   - `zip()` with tuple-unpacking
5. Functions:
   - parameters and defaults
   - docstrings and type hints
   - returning multiple values
6. Quick peek at vectorization and performance (`%timeit`)

---

## 🧪 Practice & Assignment
- **Read/Run:** `week6.py` (top to bottom) — observe each example, modify a line or two, see what changes.
- **Complete:** `week6_assignment.py`

### Assignment Tasks (Overview)
1. **BMI calculator** — handle invalid inputs gracefully
2. **Odd numbers and labels** — filtering and list comprehension
3. **`enumerate` & `zip`** — paired iteration
4. **`break` and `continue`** — loop control
5. **`while` loop and divisibility** — find first number divisible by 7 and 9
6. **Multiple returns** — function returning both max and min word length
7. *(Optional)* `map` + `lambda` vs comprehension — which reads clearer to you?

---

## 💡 Hints & Tips
- If you see something like `str | None`, you need **Python 3.10+**.
  On older versions, replace with `Optional[str]`.
- Guard your `while True` loops with a counter (`max_iter`) to avoid freezing the notebook.
- You can unpack multiple return values:
  ```python
  mean_val, range_val = get_stats(values)

