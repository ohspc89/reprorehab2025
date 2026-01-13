# Week 1 - Getting Started with Python

Welcome to your first week of the *ReproRehab Intro MATLAB/Python Pod.

This week's material helps you build a foundation in Python programming and the Spyder environment.

You will learn how to write and run code, manipulate basic data types, and understand real-world data structures like **dictionaries** and **JSON** files.

## Learning Objectives
By the end of this week, learners will be able to:
- Set up and use **Spyder** (or another IDE) to run Python scripts.
- Understand Python's core data types (`int`, `float`, `list`, `dict`).
- Read and write basic Python scripts (`.py` files).
- Describe and access dictionary structures (keys <-> values).
- Load and inspect a JSON file as a nested dictionary.
- Apply list comprehension for simple data iteration.
- Visualize simple numerical data with `matplotlib`.

## 🧩 Slides: [Getting Started with Python](https://docs.google.com/presentation/d/1_W5MP1g7ZHytF_Gfut1nUQxTp_iiAao04qkHP7sRymc/edit?usp=sharing)
- Introduction to Spyder IDE interface (editor, console, variable explorer).
- Checking working directory and saving scripts.
- Basic plot example using `matplotlib.pyplot`.
- Explanation of data types (`int`, `list`, `dict`).
- Understanding indexing (`[]`) and function calls (`()`).
- How Python handles range, loops, and list comprehension.
- Comparison with MATLAB for users transitioning from it.

## 📘 Extra Notebook: [More on Dictionary](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week1/More_on_dictionary.py)
- Deep dive into dictionary methods (`keys()`, `values()`, `items()`).
- Difference between **calling** functions and **indexing** data(`()` vs `[]`).
- Nested dictionary examples using mock HBCD metadata (`metadata["site"]["Levels"]`).
- Explanation of TypeError and IndexError with simple toy examples.

## Useful Videos
Here are some videos to reference in response to the questions discussed during the pod meeting.
- Introduction to Variables and Data Types: https://www.youtube.com/watch?v=t1KIazbIlzk
- Ranges vs. Lists: https://www.youtube.com/watch?v=rdLlPZQfI3E
- Dictionaries: https://www.youtube.com/watch?v=4t10v2QmTHU

### Extras:
- We talked about lists today, but there are other types of data collections. This video introduces lists, tuples, and sets, summarizing their differences and applications. https://www.youtube.com/watch?v=11WrzU81q68
- We introduced list comprehensions today to square integers, but there are other uses and ways to write more complex code in one line. This video re-introduces list comprehensions, shows usages with different data types, and then shows more advanced uses. https://www.youtube.com/watch?v=DUnY6l482Lk

## 🧮 Assignment: [Week1_assignment.py](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week1/Week1_assignment.py)

### Overview
The assignment connects all the concepts from this week by introducing **JSON as a real-world data format** and guiding you through a mini data-analysis exercise.

### Tasks
1. **Read JSON from a URL** and save its content to a variable (`data`).
2. **Explore data structure** and report key levels and participant counts.
3. **Extract specific information** from nested dict elements.
4. **Organize data** into a new dictionary (`sleep_hours`) with daily records.
5. **Compute summary statistics** (mean and standard deviation) using NumPy.
6. **Plot results** using `matplotlib`, showing daily sleep hour means.

### Skills You'll Gain
- Navigating API-based data (`urllib.request`).
- Working with nested data structures.
- Writing list comprehensions for aggregation.
- Generating basic data visualizations with labels and ranges.
- Strengthening your understanding of data types and modules.

## 🧭 Extra Assignment: [Introduction to Regular Expressions (Regex)](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week1/Regular_expression_in_Python.py)
- Learn how to match string patterns using `re` module.
- Understand common patterns (`\d`, `\w`, `+`, `*`, `^`, `$`, `[]`).
- Practice pattern matching in toy examples (e.g., finding digits and license plates).
- Apply regex to validate filenames with structured patterns (e.g., `sub-001_ses-01_acq-primary_motion.tsv`
- Combine regex and list comprehension to detect format errors in filenames.
