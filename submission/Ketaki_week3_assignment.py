# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 12:18:12 2025

@author: ketaki
"""

import pandas as pd 

# %% This is exactly the same as what's included in the notebook.
# Data reading prep - run this block!
github_url = 'https://raw.githubusercontent.com/ohspc89/reprorehab2025/students/contents/week3'
suffix = '.csv'

# Do you recognize `.join()` and a list comprehension?
# I am storing the urls of all 4 csv files 
# Loop over numbers 0,1,2,3, add +1 so they become 1,2,3,4
# convert numbers to string so they can be combined 
# zfill will help make our strings 2 digits long 
# join a tuple of strings 
# This was very hard for me to write. I understand the parts separately but I had to copy the code. Did not come intutively to me
fnames = ['/'.join((github_url, f'sub{str(x+1).zfill(2)}'+suffix)) for x in range(4)]
# Give column names
column_names = ['Measure_A', 'Measure_B']

# Save all dataframes in a list
dfs = []
# Loop over file names
for fname in fnames:
  # `.append()` is a method that attaches an input at the end of a list
  dfs.append(pd.read_csv(fname, header=None, names=column_names))

# %% Task 1**. Add new columns: `id` and `time`

# Each DataFrame in `dfs` represents one subject.

# Add an `id` column using `'sub1'`, `'sub2'`, `'sub3'`, `'sub4'` for each subject (*Hint*. Use `F string` with an index, just like what's explained in the notes above).
#Add a `time` column with values `'pre'`, `'test'`, and `'post'`. Convert it into a **categorical variable** using `pd.Categorical()`. Make sure the order of level is: `pre -> test -> post`.

# Complete this block
for i, df in enumerate(dfs):
  df['id'] = [f'sub{i+1}'] * 3     # if i is 0, this should be repeated accounts of 'sub1', *3 is repeating the sub for each of the three rows 
  df['time'] = pd.Categorical(['pre', 'test', 'post'], categories=['pre', 'test', 'post'], ordered=True)  # pd.Categorical(...)
  df = df.iloc[:, [2, 3, 0, 1]] #reordering the columns as id, time, measure a, measure b 
  dfs[i] = df #Saves the updated DataFrame back into the original list dfs
  
# %% Task 2**. Combine all DataFrames

#Concatenate all DataFrames in the list (`dfs`) into one large DataFrame using `pd.concat()`.

#We will set `ignore_index=True` so that row indices reset automatically.

# Complete this code block, and check the value of this variable.
with_id = pd.concat(dfs, ignore_index=True)

# %% Task 3**. Reshape to Long Format

#Use `pd.DataFrame.melt()` to convert your wide DataFrame into *long* format.

# You only need to specify:
# - `id_vars`: the columns you want to keep fixed (e.g., `['id', 'time']`)
# - `value_vars`: the columns you want to "unpivot" (e.g., `['Measure_A', 'Measure_B']`).

# Let the other arguments stay at default.

# Use `pd.DataFrame.melt()` to prepare a long format
long_form = with_id.melt(id_vars= ['id', 'time'],
                         value_vars= ['Measure_A', 'Measure_B']) #making measure a row 

# %% **Task 4**. Reshape Back to Wide Format

# Now reshape the long-form DataFrame back into a wide form using `pd.DataFrame.pivot()`.
# Use `pandas.DataFrame.pivot()`
wide_form = long_form.pivot(index='id',columns=['time', 'variable'], values = 'value')

# """ After pivoting, use this provided code to make your columns more readable and reset the index."""

# Copying from the learning materials - run it please!
wide_form.columns = ['-'.join((x[1], x[0])) for x in wide_form.columns]
# If you skip this command, 'id' will stay as index.
wide_form = wide_form.reset_index()

"""Run the code block below to prepare `back_to_long`."""

back_to_long = wide_form.melt(id_vars='id')
# Use `.sort_values(by='id')` to sort by the column: id
# Use `.reset_index(drop=True)` to reset the row numbers
back_to_long = back_to_long.sort_values(by='id').reset_index(drop=True)

# %% Task 5**. Split the "variable" column

# Using `back_to_long`, separate the information contained in the `variable` column.

# - Use `.str.split('-', expand=True)` to split into two new columns: `variable` and `time`.
# - Assign them as new columns within the same DataFrame.
# """

# # Complete the code
# splits each string wherever there is a -, so 'Measure_A-pre' → ['Measure_A', 'pre']
back_to_long[['variable', 'time']] = back_to_long['variable'].str.split('-', expand=True)

# %% Task 6**. Convert `time` back to categorical

#Use `pd.Categorical()` again to ensure `time` follows the correct order: `['pre', 'test', 'post']`

# Complete the code
back_to_long['time'] = pd.Categorical (back_to_long['time'], categories=['pre', 'test', 'post'], ordered=True)   # desired order

# %% Task 7**. Sort the DataFrame
back_to_long = back_to_long.sort_values(
    by=['id', 'variable', 'time']
).reset_index(drop=True).iloc[:, [0, 3, 1, 2]]

# %% Task 8. Practice filtering (wide format)
# 8a. Select columns that end with `"pre"` using `.str.endswith('pre')`
pre_columns=wide_form.loc[:,wide_form.columns.str.endswith('pre')]
print(pre_columns)

# 8b. Check "Measure_A' values of 'sub1' at all time points. Use `.str.startswith()`.
measurea_values=wide_form.loc[wide_form['id'] == 'sub1', wide_form.columns.str.startswith('Measure_A')]
print(measurea_values)

# %% Task 9. Practice filtering (long format)
# 9a. Filter out rows whose 'time' is 'pre' and whose 'variable' ends with 'B'.
# Use `.str.match()` and `.str.endswith()`
long_form.loc[(long_form['time'].str.match('pre') & long_form['variable'].str.endswith('B'))]

# 9b. Take rows whose 'value' is less than 4.0
select_values = long_form.loc[long_form['value'] < 4.0]
print(select_values)



  