#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 00:42:28 2025

@author: jinseok
"""

ans= 42 #int
#changes
# %% Task 1. Read 'week1.json' and save its content to a variable: 'data'

import urllib.request   # This is package to read files using URL
import matplotlib.pyplot as plt              
import json   # You need to import one more library


xs=range(10) #range variable counts from 0-9
ys=[x**2 for x in xs] #list variable
plt.plot(xs,ys) #calls on matplotlib.pyplot (which we named plt) to plot ys on xs


# %% # %% Task 1. Read 'week1.json' and save its content to a variable: 'data'


json_url = "https://raw.githubusercontent.com/ohspc89/reprorehab2025/students/contents/week1/week1.json"
# Complete '...' below.
# Here, instead of `json.load()` method introduced in the discussion,
# use `json.loads()` method.
# This is because we're reading text files using url.
with urllib.request.urlopen(json_url) as f:
    data = json.loads(f.read())
    
    
# %% Task 2. Report the first-level keys of 'data'. How many subjects?
# hint: use `len()` function to get the length of a sequence

len(data)
#19999 subjects. because it's 0-indexed, 0-1,999 is 2,000 subjects total

# %% Task 3. Report the second-level keys of 'data'.
# How many days each participant was tracked?
# hint: you can use the first key at the first-level

#3 days, I found this by looking at the key. Is there a way to programmatically 
#do this?

 
data['sub1'].keys() #The .keys() function shows the key names of the dataset. 
#day1, day2, day3

# can also do:
data.get('sub1')


# %% Task 4. What were the measures of each day?
# hint: all three days were the same regarding measures

data['sub1']['day1']

data_list = list(data.keys()) #this creates a list of the data keys, just a plain 1D list


#hour_slept, coffee_intake and mean_cortisol_levels

# %% Task 5. Make a new dictionary, 'sleep_hours'.
# Its structure will be like:
#    {'day1': [hour_slept of all participants on day 1],
#     'day2': [hour_slept of all participants on day 2],
#     'day3': [hour_slept of all participants on day 3]
#    }
# Task 5a: First create three lists, each of which will be the value
# of 'sleep_hours'. Use list comprehensions.
#describe a list comprehension
#save each element of the list that you are looking for


day1_value = [data[subject]['day1']['hour_slept'] for subject in data.keys()]
day2_value = [data[subject]['day2']['hour_slept'] for subject in data.keys()]
day3_value = [data[subject]['day3']['hour_slept'] for subject in data.keys()]


# Task 5b: Now make 'sleep_hours'

sleep_hours = {'day1':day1_value, 'day2': day2_value, 'day3':day3_value}


# %% Task 6. Calculate the mean and the standard deviation of hours slept
# on each day using 'sleep_hours' dictionary of Task 5.
# Make two variables ('means' and 'stds') using list comprehensions.
# hint: import numpy and use `numpy.mean()` and `numpy.std()`

import numpy as np


means = {'day1_mean': np.mean(sleep_hours['day1']), 'day2_mean': np.mean(sleep_hours['day2']), 'day3_mean': np.mean(sleep_hours['day3'])}
stds = {'day1_std': np.std(sleep_hours['day1']), 'day2_std': np.std(sleep_hours['day2']), 'day3_std': np.std(sleep_hours['day3'])}

#means = [np.mean(val) for _, val in sleep_hours.items()] #This is a cleaner way to do it using list logic. 
#stds1 = [np.std(val) for _, val in sleep_hours.items()]



# %% Task 7. Plot daily sleep hour means using 'means' sequence prepared in Task 6.
# Make sure that your days start from 1. What should you do then?
# requirement: use `range()`
x_days = range(1,4,1)
mean_values = [means[day] for day in means]

import matplotlib.pyplot as plt
plt.plot(x_days, mean_values)       # provide X and Y
plt.xlabel("Day")     # provide x-axis label
plt.ylabel("Hours of Sleep")     # provide y-axis label
