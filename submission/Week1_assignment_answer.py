#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 00:42:28 2025

@author: jinseok
"""

# %% Task 1. Read 'week1.json' and save its content to a variable: 'data'

# answer:
import urllib.request
import json
json_url = 'https://raw.githubusercontent.com/ohspc89/reprorehab2025/students/contents/week1/week1.json'
with urllib.request.urlopen(json_url) as f:
    data = json.loads(f.read())

# %% Task 2. Report the first-level keys of 'data'. How many subjects?
# hint: use `len()` function to get the length of a sequence

# answer: 20000
len(data.keys())

# %% Task 3. Report the second-level keys of 'data'.
# How many days each participant was tracked?
# hint: you can use the first key at the first-level

# answer:
data['sub0'].keys()

# %% Task 4. What were the measures of each day?
# hint: all three days were the same regarding measures

# answer:
data['sub0']['day1']

# %% Task 5. Make a new dictionary, 'sleep_hours'.
# Its structure will be like:
#    {'day1': [hour_slept of all participants on day 1],
#     'day2': [hour_slept of all participants on day 2],
#     'day3': [hour_slept of all participants on day 3]
#    }
# Task 5a: First create three lists, each of which will be the value
# of 'sleep_hours'. Use list comprehensions.

# answer:
day1_value = [value['day1']['hour_slept'] for key, value in data.items()]
day2_value = [value['day2']['hour_slept'] for key, value in data.items()]
day3_value = [value['day3']['hour_slept'] for key, value in data.items()]

# Task 5b: Now make 'sleep_hours'

# answer:
sleep_hours = {'day1': day1_value,
               'day2': day2_value,
               'day3': day3_value}


# %% Task 6. Calculate the mean and the standard deviation of hours slept
# on each day using 'sleep_hours' dictionary of Task 5.
# Make two variables ('means' and 'stds') using list comprehensions.
# hint: import numpy and use numpy.mean() and numpy.std() function

# answer:
import numpy as np
means = [np.mean(value) for key, value in sleep_hours.items()]
stds = [np.std(value) for key, value in sleep_hours.items()]

# %% Task 7. Plot daily sleep hour means using 'means' sequence prepared in Task 6.
# Make sure that your days start from 1. What should you do then?
# requirement: use `range()`

# answer:
import matplotlib.pyplot as plt
plt.plot(range(1, 4), means)
plt.xlabel('Days')
plt.ylabel('Hours slept')
