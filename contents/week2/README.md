# Week 2. Tabular Data Manipulation in Python I

This week, we start working with tabular data - one of the most common formats you'll encounter in rehabilitation and behavioral research.

Our main tool will be **pandas**, a powerful Python library that makes data loading, filtering, and summarizing easier than ever.

You will learn how to:
- load `.csv` and `.tsv` files into pandas DataFrames,
- explore dataset structure and metadata
- rename columns, slice and filter values,
- and perform basic descriptive statistics and visualization.

### Goal of Week 2:
Get comfortable with pandas' DataFrame - how to load, inspect, reshape, and summarize data.

Once you can do this fluently, every dataset you meet (physio, motion, fNIRS, speech, etc.) will start to feel like a familiar structure waiting to be explored.

## 🧩 Slides - [Tabular Data Manipulation in Python I](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week2/Tabular%20data%20manipulation%20in%20Python%20I.pdf)

Reference slides summarize:
- key pandas functions (`read_csv`, `rename`, `iloc`, `loc`, `describe`),
- common parameters (`sep`, `header`, `usecols`, `engine`),
- and quick visualization commands.

Use them as a lookup while you code!

## 📘 Extra Notebook [Read and manipulate a CSV file](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week2/reading_csv_real_world.py)

By studying this script, you will:
- Grasp **how to go from raw CSV to derived features** in pandas.
- See how **basic indexing and column manipulation** scale to real data.
- Understand **axis behavior**, **data type handling**, and **naming conventions**.
- Gain first exposure to **data visualization** and **exporting cleaned datasets**.
- Appreciate how to write code that's both functional and readable for collaborators.

## 🧮 Main Assignment - [Week2_assignment.py](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week2/Week2_assignment.py)

You will use a **public wearable-sensor dataset** (PhysioNet) to practice hands-on data handling.

### Tasks include:
1. Loading a CSV file using `pd.read_csv()` and inspecting structure with `.head()` and `.info()`.
2. Renaming columns (`rename`) and selecting subsets(`iloc`, `loc`).
3. Filtering rows that meet a condition.
4. Computing summary statistics (`describe`, `mean`, `std`, `min`, `max`).
5. Reading a more complex TSV file (motion-capture dataset) and visualizing a few variables using `plot.line`, `plot.scatter`, and `plot.hist`.

This exercise helps you build an intuition for how datasets are organized and how to **interrogate data directly from code, without switching to Excel.

## 🧭 Extra - [Handling Time in Pandas](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week2/timestamps_pandas.py)

Timestamps are evertwhere - from wearable devices to behavioral recordings.

This notebook introduces pandas' `Timestamp` and `DatetimeIndex` objects and walks through how to:

- convert strings and numbers to datetime (`to_datetime`),
- handle Unix time and time zones,
- extract attributes like year, month, day, hour, etc.,
- and compute time differences between two measurement points.

### Video recording
Please find the recorded pod meeting [here](https://drive.google.com/file/d/1-nWBPvSfb8lkDVZOIiYlpGz3vc3qwE3w/view?usp=drive_link)
