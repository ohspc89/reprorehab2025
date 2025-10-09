# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 21:45:18 2025

@author: ketak
"""
# %% Task 1. Read 'week1.json' and save its content to a variable: 'data'

import urllib.request   # This is package to read files using URL
import json
json_url = "https://raw.githubusercontent.com/ohspc89/reprorehab2025/students/contents/week1/week1.json"
with urllib.request.urlopen(json_url) as f:
    data = json.loads (f.read()) 
    print(data)
    
    # %% Task 2. Report the first-level keys of 'data'. How many subjects?
# hint: use `len()` function to get the length of a sequence
    num_subjects = len (data.keys())
    print(num_subjects)
    
    
    # %% Task 3. Report second-level keys and number of days
    # How many days each participant was tracked?
# hint: you can use the first key at the first-level
first_subj = list(data.keys())[0]        # first level is likely the first subject
second_level_keys = data[first_subj].keys()  # check second level keys for first subject
print("Second-level keys:", second_level_keys)

# %% Task 4. What were the measures of each day?
# hint: all three days were the same regarding measures

first_subj = list(data.keys())[0] #checking the first participant 
first_day = list(data[first_subj].keys())[0]
measures_perday = data[first_subj][first_day].keys()
print ("Measures of each day", measures_perday)

# %% Task 5. Make a new dictionary, 'sleep_hours'.
# Its structure will be like:
#    {'day1': [hour_slept of all participants on day 1],
#     'day2': [hour_slept of all participants on day 2],
#     'day3': [hour_slept of all participants on day 3]
#    }
# Task 5a: create lists for each day
day1_sleep = [data[participant]['day1']['hour_slept'] for participant in data]
day2_sleep = [data[participant]['day2']['hour_slept'] for participant in data]
day3_sleep = [data[participant]['day3']['hour_slept'] for participant in data]
# Task 5b: create the dictionary
sleep_hours = {
    'day1': day1_sleep,
    'day2': day2_sleep,
    'day3': day3_sleep
}

# %% Task 6. Calculate the mean and the standard deviation of hours slept
# on each day using 'sleep_hours' dictionary of Task 5.
# Make two variables ('means' and 'stds') using list comprehensions.
# hint: import numpy and use `numpy.mean()` and `numpy.std()`

#import ...
#means = ...
#stds = ...

import numpy as np
days = ['day1', 'day2', 'day3']

means = [np.mean(sleep_hours[day]) for day in days]
stds  = [np.std(sleep_hours[day])  for day in days]

# %% Task 7. Plot daily sleep hour means using 'means' sequence prepared in Task 6.
# Make sure that your days start from 1. What should you do then?
# requirement: use `range()`

#import matplotlib.pyplot as plt
#plt.plot(...)       # provide X and Y
#plt.xlabel(...)     # provide x-axis label
#plt.ylabel(...)     # provide y-axis label

x = range(1, 4)  # starts with day 1, we have 3 days so stop value becomes 4 meaning everything before 4 is included 
import matplotlib.pyplot as plt

plt.plot(range(1, 4), means)
plt.xlabel('Day')
plt.ylabel('Average sleep hours')






