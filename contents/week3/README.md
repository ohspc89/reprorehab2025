# Week 3: Tabular Data Manipulation in Python II

In Week 2 you learned how to *load* and *inspect* tabular data.

This week we shift gears to **reorganizing and combining** datasets - the foundation of every reproducible data pipeline.

You'll explore how to:

- Combine multiple DataFrames using `concat` and `merge`
- Convert between *wide* and *long* formats (`melt`, `pivot`)
- Filter text-based columns using string methods (`.str`)
- Detect and fill missing values
- Interpolate continuous signals over time

These steps mirror what researchers routinely do when handling multi-session, multi-sensor data in rehabilitation studies.

## 📘 Main Notebook: [Tabular Data Manipulation in Python II](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week3/data_wrangling_pandas_part2.py)
This exercise uses small synthetic datasets (`sub01.csv` - `sub04.csv`) to simulate multi-subject experimental data.

You'll recreate a realistic workflow:

1. **Constructing DataFrames** from Python dictionaries and lists
2. **Filtering and selecting subsets using** `.loc[]`, `.query()`, and logical operators
3. **Applying string operations** (`.str.split()`, `.str.contains()`, `.str.replace()`)
4. **Combine datasets** vertically (`pd.concat`) and horizontally (`merge`)
5. **Reshaping data** between *wide* and *long* formats using `.melt()` and `.pivot()`
6. **Adding new variables** dynamically with `.assign()` and f-strings
7. **Exporting clean data** to CSV for further analyses
8. **Data assembly**: use list comprehensions, `.join()`, and `.zfill()` to build file paths dynamically.
9. **Categorical ordering**: convert variables like `time = ['pre', 'test', 'post']`  into ordered `pd.Categorical` values.

It's designed as a guided exploration - print each output, observe the structure, and note how transformations affect indexing and variable names.

## 🧩 Slides: [Data Wrangling with Pandas](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week3/data_wrangling_pandas.pdf)
This slides summarize:
- The logic behind *tidy data* and why *long format* simplifies visualization and stats
- Core pandas transformations (`concat`, `merge`, `melt`, `pivot`)
- Examples showing how multiple sensor datasets can be combined across participants or sessions

Use these slides as a visual map of how each operation connects to real research workflows.

## 🧮 Assignment: [Week 3 assignment](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week3/Week3_assignment.py)
This script extends what you learned above by introducing a small *multi-subject simulation*. You'll load, combine, and reshape data across participants and measurement sessions

### **You'll practice**:
- Loading multiple CSVs and concatenating them with `pd.concat()`
- Creating an ordered categorical variable for `time = ['pre', 'test', 'post']`
- Splitting compound variable names with `.str.split('-')`
- Using `.str.startswith()` and `.str.endswith()` for targeted filtering
- Converting between *long* and *wide* formats to prepare summary statistics

This mirrors what you'd do when preparing longitudinal datasets for downstream analysis. Read this [note](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week3/enumerate.py) to further understand `enumerate()` and f-string.

## 🧭 Extra: [Handling Missing Data & Interpolation](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week3/missing_values_pandas.py). 
The topic of this extra notebook is: Handling Missing values using Pandas.
Real datasets often contain gaps or irregular timestamps.

This notebook focuses on strategies to detect and fill missing values:
- Identify missing entries using `.isna()` and summarize with `.sum()`
- Drop incomplete rows using `.dropna()`
- Replace or estimate missing values with `.fillna()` and `.interpolate()`
- Compare interpolation methods (`linear`, `quadratic`, `time`) to see their effect on simulated IMU-like time-series

By practicing with noisy, incomplete data, you'll gain intuition for how to reconstruct continuous signals before downstream analysis.

## ✨ Take-Home Message
Data rarely arrive analysis-ready.

This week's assignment teaches you how to *think structurally* about data - how to organize information so that your code scales, your plots make sense, and your research stays reproducible.

### Video recording
Please find the recorded pod meeting [here](https://drive.google.com/file/d/1furlBaWV6VZUZaZ5TeKJLxzm5ltUCN4S/view?usp=drive_link)
