#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 00:42:28 2025

@author: jinseok
"""

# %% Task 1. Read 'week1.json' and save its content to a variable: 'data'

import urllib.request   # This is package to read files using URL
import ...              # You need to import one more library
json_url = "https://raw.githubusercontent.com/ohspc89/reprorehab2025/students/contents/week1/week1.json"
# Complete '...' below.
# Here, instead of `json.load()` method introduced in the discussion,
# use `json.loads()` method.
# This is because we're reading text files using url.
with urllib.request.urlopen(json_url) as f:
    data = ...(f.read())
    
    
# %% Task 2. Report the first-level keys of 'data'. How many subjects?
# hint: use `len()` function to get the length of a sequence

len(...)


# %% Task 3. Report the second-level keys of 'data'.
# How many days each participant was tracked?
# hint: you can use the first key at the first-level


# %% Task 4. What were the measures of each day?
# hint: all three days were the same regarding measures


# %% Task 5. Make a new dictionary, 'sleep_hours'.
# Its structure will be like:
#    {'day1': [hour_slept of all participants on day 1],
#     'day2': [hour_slept of all participants on day 2],
#     'day3': [hour_slept of all participants on day 3]
#    }
# Task 5a: First create three lists, each of which will be the value
# of 'sleep_hours'. Use list comprehensions.

day1_value = ...
day2_value = ...
day3_value = ...

# Task 5b: Now make 'sleep_hours'

sleep_hours = ...


# %% Task 6. Calculate the mean and the standard deviation of hours slept
# on each day using 'sleep_hours' dictionary of Task 5.
# Make two variables ('means' and 'stds') using list comprehensions.
# hint: import numpy and use `numpy.mean()` and `numpy.std()`

import ...
means = ...
stds = ...


# %% Task 7. Plot daily sleep hour means using 'means' sequence prepared in Task 6.
# Make sure that your days start from 1. What should you do then?
# requirement: use `range()`

import matplotlib.pyplot as plt
plt.plot(...)       # provide X and Y
plt.xlabel(...)     # provide x-axis label
plt.ylabel(...)     # provide y-axis label
