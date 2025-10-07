You can submit your week1 assignment here.

Make sure you 'pull' this repo first from your forked repo.
Then push your completed assignment to your forked repo.
Finally, make a pull request to this repo.

Please name your submission with your name on (ex. week1-Jin.py).

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 23:08:25 2025

@author: blay6
"""

# %% Task 1. Read 'week1.json' and save its content to a variable: 'data'

import urllib.request
import json

json_url = "https://raw.githubusercontent.com/ohspc89/reprorehab2025/students/contents/week1/week1.json"

with urllib.request.urlopen(json_url) as f:
    data = json.loads(f.read())

print(data.keys())
print(data['sub19999'])
alist=[1,2,3,4,5]
alist[3]
print('alist')
# %% Task 2. Report the first-level keys of 'data'. How many subjects?
# hint: use `len()` function to get the length of a sequence

print(len(data))

# %% Task 3. Report the second-level keys of 'data'.
# How many days each participant was tracked?
# hint: you can use the first key at the first-level
 
#refers to the value within sub0 which is 3 days
print(data['sub0']['day1']['hour_slept'])

# %% Task 4. What were the measures of each day?
# hint: all three days were the same regarding measures

list(data.keys())
Reece = list(data.keys())
print(Reece[0])
list2= [[1,2,3],[4,5,6]]
list2[0][3]

print(data['sub0']['day1'].keys())
# %% Task 5. Make a new dictionary, 'sleep_hours'.
# Its structure will be like:
#    {'day1': [hour_slept of all participants on day 1],
#     'day2': [hour_slept of all participants on day 2],
#     'day3': [hour_slept of all participants on day 3]
#    }
# Task 5a: First create three lists, each of which will be the value
# of 'sleep_hours'. Use list comprehensions.

# sleep_hours = ...
# Day 1 hours slept
day1_value = [data[sub]['day1']['hour_slept'] for sub in data]

# Day 2 hours slept
day2_value = [data[sub]['day2']['hour_slept'] for sub in data]

# Day 3 hours slept
day3_value = [data[sub]['day3']['hour_slept'] for sub in data]

# Task 5b: Now make 'sleep_hours'

sleep_hours = {
    'day1': day1_value,
    'day2': day2_value,
    'day3': day3_value
}

# %% Task 6. Calculate the mean and the standard deviation of hours slept
# on each day using 'sleep_hours' dictionary of Task 5.
# Make two variables ('means' and 'stds') using list comprehensions.
# hint: import numpy and use `numpy.mean()` and `numpy.std()`


import numpy as np

# Calculate means for each day
means = [np.mean(sleep_hours[day]) for day in ['day1', 'day2', 'day3']]

# Calculate standard deviations for each day
stds = [np.std(sleep_hours[day]) for day in ['day1', 'day2', 'day3']]
print(means)
print(stds)


# %% Task 7. Plot daily sleep hour means using 'means' sequence prepared in Task 6.
# Make sure that your days start from 1. What should you do then?
# requirement: use `range()`

import matplotlib.pyplot as plt

plt.plot(range(1, 4), means)
plt.xlabel("Day")
plt.ylabel("Mean hours slept")
plt.title("Mean Daily Sleep Hours")
