# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 20:34:49 2025

@author: Ryan
"""
# %%
import pandas as pd

#First_Ladies
first_ladies = pd.read_csv(
    'https://raw.githubusercontent.com/ohspc89/reprorehab2025/students/contents/week3/first_ladies.csv')
first_ladies.head()

# Martha! (You should have watched 'Batman vs. Superman)
first_ladies.loc[first_ladies["First_name"] == "Martha", :]

# What was the maiden name of the wife of Mr. George W. Bush?
# pandas.DataFrame.loc[(condition 1) & (condition 2) & ..., columns]
first_ladies.loc[(first_ladies["Last_name"] == "Bush") & (first_ladies["year_start"] > 2000), "Maiden_name"]

# Count how many first ladies are there with distinct first names
# `first_name_count` is a pandas.Series.
first_name_counts = first_ladies.First_name.value_counts()
# Filter: more than once!
more_than_once = first_name_counts.loc[first_name_counts > 1]
# Now, give me rows of the first ladies whose first names are not unique!
first_ladies.loc[first_ladies["First_name"].isin(more_than_once.index), :].head(8)

# Sort by the last name - see how `ascending=False` works
first_ladies.sort_values(by='Last_name', ascending=False).head(6)

# You can sort by multiple columns in order
# Sort first by 'First_name' (from Z to A), and then by 'year_start' (earlier years first)
first_ladies.sort_values(by=['First_name', 'year_start'], ascending=[False, True]).head(6)

# DataFrame
repeated_treatment = pd.DataFrame({'Subject': ['sub01'] * 5 + ['sub02'] * 5,
                                   'Timepoint': ['pre', 'post', 'treat1', 'treat2', 'treat3'] * 2,
                                   'Dose': [0.0, 0.0, 1.1, 2.2, 3.3, 2.0, 2.0, 0.8, 2.5, 3.8]})
# Timepoint is displayed in the following order:
# pre -> post -> treat1 -> treat2 -> treat3
repeated_treatment

# Set the Timepoint order to be more chronological
# (ex. pre -> treat1 -> treat2 -> treat3 -> post)
tp_level = ['pre', 'treat1', 'treat2', 'treat3', 'post']
# Set `categories` to the level you predefined, and `ordered` to True
repeated_treatment['Timepoint'] = pd.Categorical(repeated_treatment['Timepoint'],
                                                 categories=tp_level, ordered=True)
# You now see the new Timepoint order implemented
repeated_treatment.sort_values(by=['Subject','Timepoint'])

# @title Transformed: `rt_v2`
rt_v2 = repeated_treatment.pivot(index='Subject', columns='Timepoint', values="Dose")
rt_v2.columns=['Dose-'+x for x in ['pre', 'treat1', 'treat2', 'treat3', 'post']]
rt_v2 = rt_v2.reset_index()

# If we have a DataFrame in wide format...
rt_v2

# ... column-wise calculation is easy.
# ex. What's the mean of pre-post dose across subjects?
(rt_v2['Dose-pre'] - rt_v2['Dose-post']).mean()

# Multiply (increase, decrease, divide by, ...)
rt_v2['Dose-treat2'] = rt_v2['Dose-treat2'] * 3
rt_v2

# Use `.assign` to create new columns easily
rt_v2 = rt_v2.assign(prepost_ratio = rt_v2["Dose-pre"]/rt_v2["Dose-post"],
                     treat_ratio = rt_v2["Dose-treat2"]/(rt_v2["Dose-treat1"] + rt_v2["Dose-treat3"]))
rt_v2

# Applying the same function to string elements of a column
# Use `.str`.
# `.str.capitalize()`: Capitalization | `.str.lower()`: to lowercase | `.str.upper()`: to uppercase
rt_v2['Subject'].str.capitalize()

# `.str.replace()`: replace substring ex. 'Sub01' -> 'Subject01'
rt_v2['Subject'].str.replace('b', 'bject')

#@title Transformed (2): `rt_v2`
# Changing values for a new example
rt_v2['Subject_label'] = ['StudyA_01', 'StudyB_01']
rt_v2.drop('Subject', axis=1, inplace=True)
cols = list(rt_v2.columns)
rt_v2 = rt_v2[[cols[-1]]+cols[:-1]]

# Subject labels are now joined with '_'. ex. 'sub_StudyA_01'
rt_v2

# `.str.split()`: splits strings.

# Split by '_': a list is generated
rt_v2['Subject_label'].str.split('_')

# If you want to keep certain elements, use `.str` one more time.
# For example, if we want the third element of the list of splitted strings:
rt_v2['Subject_label'].str.split('_').str[1]

# You can use 'expand=True' to generate new columns using splitted strings.
# The number of columns to be created should match the number of splitted strings.
rt_v2[['Study_type', 'Subject_order']] = rt_v2['Subject_label'].str.split('_', expand=True)
# Check how 'Study_type' and 'Subject_order' columns are prepared
rt_v2

# Let's have we have the following metadata: biological sex information
metadata = pd.DataFrame({'Subject_label': ['StudyA_01', 'StudyB_01'],
                         'Sex': pd.Categorical(['F', 'M'], categories=['F', 'M'], ordered=True)})
metadata

# Merge this with the original data using the "key" column
rt_v2.merge(metadata, on="Subject_label")

#@title Transformed (3): `rt_v2`
new_row = pd.Series(['StudyA_02', 1.2, 1.2, 6.8, 3.1, 0.9, 1.3, 1.630435, 'StudyA', '02'],
                    index=rt_v2.columns)
rt_v2 = pd.concat([rt_v2, new_row.to_frame().T]).reset_index(drop=True)

# What if your dataset has more rows than your metadata?
rt_v2

# pandas.merge defaults to "INNER JOIN", so it will only return "complete" rows.
rt_v2.merge(metadata, on='Subject_label')

# You can use "OUTER JOIN" to make ALL rows to be populated, even with NAs.
# See how 'Sex' is NaN for 'StudyA_02'.
rt_v2.merge(metadata, how='outer', on='Subject_label')

# If metadata has more rows (4 > 3)
metadata = pd.DataFrame({'Subject_label': ['StudyA_01', 'StudyB_01', 'StudyA_02', 'StudyB_02'],
                         'Sex': pd.Categorical(['F', 'M', 'M', 'F'], categories=['F', 'M'], ordered=True)})
# rows with metadata but not raw data will be populated with many more NAs.
rt_v2.merge(metadata, how='outer', on='Subject_label')

# %%
# @title Reading 4 files as dataframes and saving them in a list: `dfs`

# Data reading prep
github_url = 'https://raw.githubusercontent.com/ohspc89/reprorehab2025/students/contents/week3'
suffix = '.csv'
# Do you recognize `.join()` and a list comprehension?
fnames = ['/'.join((github_url, f'sub{str(x+1).zfill(2)}'+suffix)) for x in range(4)]
# Give column names
column_names = ['Measure_A', 'Measure_B']

# Save all dataframes in a list
dfs = []
# Loop over file names
for fname in fnames:
  # `.append()` is a method that attaches an input at the end of a list
  dfs.append(pd.read_csv(fname, header=None, names=column_names))
  
# An element of `dfs`.
dfs[0]

# `ignore_index=True` does the same trick as `.reset_index(drop=True)`.
pd.concat(dfs, axis=0, ignore_index=True)

# @title Preparing a long dataframe

# Adding a new column: 'id' and reorder columns
for i, df in enumerate(dfs):
  df['id'] = ['sub'+str(i+1).zfill(2)]*3
  df['time'] = ['pre', 'test', 'post']
  df = df.iloc[:, [2, 3, 0, 1]]
  dfs[i] = df

# So now we can see that "id" column can help you
with_id = pd.concat(dfs, axis=0, ignore_index=True)

# Use `pd.DataFrame.melt()` to prepare a long format
#   id_vars : scalar, tuple, list, or ndarray, optional
#       Column(s) to use as identifier variables.
#   value_vars : scalar, tuple, list, or ndarray, optional
#       Column(s) to unpivot. If not specified, uses all columns that
#       are not set as id_vars.
#   var_name : scalar, default None
#       Name to use for the 'variable' column. If None it uses
#       frame.columns.name or 'variable'.
#   value_name : scalar, default 'value'
#       Name to use for the 'value' column, can't be an existing column label.
long_form = with_id.melt(id_vars=['id', 'time'], value_vars=['Measure_A', 'Measure_B'],
                         var_name='measure', value_name='value')

# This is long format
long_form.head()

# Using `pandas.DataFrame.pivot()`
wide_form = long_form.pivot(index='id', columns=['time', 'measure'], values='value')
wide_form

# Note that columns are not plain texts, but tuples.
# Also, 'id' is no longer a distinct column - it's used as the row index.
wide_form.columns

# You can rename the labels
wide_form.columns = ['-'.join((x[1], x[0])) for x in wide_form.columns]
# If you skip this command, 'id' will stay as index.
wide_form = wide_form.reset_index()
wide_form

# Ok, it's now Index with plain strings.
wide_form.columns

# wide format works well with `pandas.DataFrame.plot()` methods.
wide_form.plot.scatter(x='Measure_A-pre', y='Measure_A-post', color=['r', 'b', 'g', 'c'])

back_to_long = wide_form.melt(id_vars='id')
# Use `.sort_values(by='id')` to sort by the column: id
# Use `.reset_index(drop=True)` to reset the row numbers
back_to_long = back_to_long.sort_values(by='id').reset_index(drop=True)
back_to_long.head(8)

# Use `pd.melt()`. You just provide one more input: `pandas.DataFrame`
long_form_v2 = pd.melt(with_id, id_vars=['id', 'time'])
# Here you can check the default options used (`var_name='variable'`, `value_name='value'`)
long_form_v2.head()

# See the difference: what if you only use 'id' column as the `id_vars`?
# Rows will not be unique anmore.
long_form_v3 = pd.melt(with_id, id_vars='id', value_vars=['Measure_A', 'Measure_B'])
long_form_v3.head()

# %%

import pandas as pd

# Data reading prep - run this block!
github_url = 'https://raw.githubusercontent.com/ohspc89/reprorehab2025/students/contents/week3'
suffix = '.csv'
# Do you recognize `.join()` and a list comprehension?
fnames = ['/'.join((github_url, f'sub{str(x+1).zfill(2)}'+suffix)) for x in range(4)]
# Give column names
column_names = ['Measure_A', 'Measure_B']
# Save all dataframes in a list
dfs = []
# Loop over file names
for fname in fnames:
  # `.append()` is a method that attaches an input at the end of a list
  dfs.append(pd.read_csv(fname, header=None, names=column_names))
  
#Task 1 Add new columns: 'id' & 'time'
# Complete this block
# old for i, df in enumerate(dfs):
  #df['id'] = ['sub1'] + ['sub2'] + ['sub3']
  #df['time'] = ['pre', 'test', 'post']
  #df = df.iloc[:, [2, 3, 0, 1]]
  #dfs[i] = df
  
for i, df in enumerate(dfs):
    df['id'] = f'sub{i+1}'  # Use the index to create 'sub1', 'sub2', 'sub3', 'sub4'
    df['time'] = pd.Categorical(['pre', 'test', 'post'], 
                                 categories=['pre', 'test', 'post'], 
                                 ordered=True)
    df = df.iloc[:, [2, 3, 0, 1]]
    dfs[i] = df
    
# Task 2 Complete this code block
with_id = pd.concat(dfs, axis=0, ignore_index=True)

#Task 3 # Use `pd.DataFrame.melt()` to prepare a long format
#   id_vars : scalar, tuple, list, or ndarray, optional
#       Column(s) to use as identifier variables.
#   value_vars : scalar, tuple, list, or ndarray, optional
#       Column(s) to unpivot. If not specified, uses all columns that
#       are not set as id_vars.
#   var_name : scalar, default None
#       Name to use for the 'variable' column. If None it uses
#       frame.columns.name or 'variable'.
#   value_name : scalar, default 'value'
#       Name to use for the 'value' column, can't be an existing column label.
long_form = with_id.melt(id_vars=['id', 'time'],
                         value_vars=['Measure_A', 'Measure_B'],
                         )

# Task 4 Use pandas.DataFrame.pivot() to prepare a wide dataframe.
# Use `pandas.DataFrame.pivot()`
wide_form = long_form.pivot_table(index='id', columns=['time', 'variable'], values='value')
wide_form

# Copying from the learning materials - run it please!
wide_form.columns = ['-'.join((x[1], x[0])) for x in wide_form.columns]
# If you skip this command, 'id' will stay as index.
wide_form = wide_form.reset_index()

back_to_long = wide_form.melt(id_vars='id')
# Use `.sort_values(by='id')` to sort by the column: id
# Use `.reset_index(drop=True)` to reset the row numbers
back_to_long = back_to_long.sort_values(by='id').reset_index(drop=True)

print(back_to_long.head(10))
print(back_to_long['variable'].unique())

#Task 5: Modify one column and make a new column in back_to_long: variable and time. Use .str.split() to split strings of variable column and use expand=True to populate new columns.
# Complete the code
back_to_long[['variable', 'time']] = back_to_long['variable'].str.split('-', expand=True)

#Task 6. Make time column a categorical one. Set the level identical to what's described in task 1.
# Complete the code
back_to_long['time'] = pd.Categorical(
    back_to_long['time'],
    categories=['pre', 'test', 'post'],
    ordered=True
    )

#Task 7 Let's sort values so that you will get a dataframe like this:
    #You only need to provide the value for by in .sort_values().
   # Complete the code
back_to_long.sort_values(by='id').reset_index(drop=True).iloc[:, [0, 3, 1, 2]]

#Task 8. Using wide_form, complete the following tasks
# 8a. Only take columns whose names end with 'pre'. Use `.str.endswith()`.
wide_form.loc[:, wide_form.columns.str.endswith('pre')]

# 8b. Check "Measure_A' values of 'sub1' at all time points. Use `.str.startswith()`.
wide_form.loc[wide_form['id'] == 'sub1', wide_form.columns.str.startswith('Measure_A')]

#Task 9. Using back_to_long, complete the following tasks.
# 9a. Filter out rows whose 'time' is 'pre' and whose 'variable' ends with 'B'.
# Use `.str.match()` and `.str.endswith()`.
long_form.loc[(long_form['time'] == 'pre') & (long_form['variable'].str.endswith('B'))]

# 9b. Take rows whose 'value' is less than 4.0
long_form.loc[(long_form['value'] <4.0)]
