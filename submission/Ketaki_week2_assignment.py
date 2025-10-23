# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 10:14:24 2025

@author: ketak
"""

# %% import package 
import pandas as pd

# read data using an url 

# source: Hongn, Bosch, Prado, and Bonomini (2025).
# Wearable Device Dataset from Induced Stress and Structured Exercise Sessions

# %% Read dataset
url= "https://physionet.org/files/wearable-device-dataset/1.0.1/Wearable_Dataset/AEROBIC/S08/ACC.csv?download""https://physionet.org/files/wearable-device-dataset/1.0.1/Wearable_Dataset/AEROBIC/S08/ACC.csv?download"

# Read csv file using the url 
data=pd.read_csv(url)

# %% 
# Task 1. Check the structure of the data using `.head()` and `.info()`.
#         How many rows and columns are there? What's the data type of each column?
#         What are the names of the columns? Do you see why the names are such?

#Check the first 5 rows using the head() function
#Use print() to see the output in the console when running from the Editor

print(data.head())
# Answer:
# 2013-02-25 18:00:59  2013-02-25 18:00:59.1  2013-02-25 18:00:59.2
# 0                 32.0                   32.0                   32.0
# 1                -53.0                  -30.0                   16.0
# 2                -54.0                  -30.0                   16.0
# 3                -54.0                  -31.0                   15.0
# 4                -54.0                  -30.0                   18.0

# Print a concise summary of your dataframe using .info() function 

print(data.info())
#Answer:
# 2013-02-25 18:00:59  2013-02-25 18:00:59.1  2013-02-25 18:00:59.2
# 0                 32.0                   32.0                   32.0
# 1                -53.0                  -30.0                   16.0
# 2                -54.0                  -30.0                   16.0
# 3                -54.0                  -31.0                   15.0
# 4                -54.0                  -30.0                   18.0
# <class 'pandas.core.frame.DataFrame'>
# RangeIndex: 64951 entries, 0 to 64950
# Data columns (total 3 columns):
#  #   Column                 Non-Null Count  Dtype  
# ---  ------                 --------------  -----  
#  0   2013-02-25 18:00:59    64951 non-null  float64
#  1   2013-02-25 18:00:59.1  64951 non-null  float64
#  2   2013-02-25 18:00:59.2  64951 non-null  float64
# dtypes: float64(3)
# memory usage: 1.5 MB
# None

#Number of columns = 3
#Number of rows = 64951
#Data type of each column= decimals or float64
#Names of columns= looks like date (yy-mm-dd) and timestamps
#Columns names have .1, .2 which means they are duplicates and pandas has renamed them with .1 to show that

# %%
# Task 2. Print the names of the columns.
print(data.columns)
#Answer: 
# Index(['2013-02-25 18:00:59', '2013-02-25 18:00:59.1',
#        '2013-02-25 18:00:59.2'],
#       dtype='object')


# %%
# Task 3. Please change the column names to 'ACC_X', 'ACC_Y', and 'ACC_Z'.
#         (Hint. Use `data.rename(...)` - check out the slides!)
#         Don't forget to add `inplace=True`

data.rename(columns={x:y for x,y in zip(data.columns, ['ACC_X', 'ACC_Y','ACC_Z'])}, inplace=True)
#x → each old column name from data.columns
# y → each new name from ['ACC_X', 'ACC_Y', 'ACC_Z']
# {x: y for x, y in zip(...)} → creates the mapping dictionary
# inplace=True → updates the DataFrame directly

print(data.head())
#Answer: 
#  ACC_X  ACC_Y  ACC_Z
# 0   32.0   32.0   32.0
# 1  -53.0  -30.0   16.0
# 2  -54.0  -30.0   16.0
# 3  -54.0  -31.0   15.0
# 4  -54.0  -30.0   18.0

# %%
# Task 4. Please display the first 10 rows and 3 columns using `.iloc[]`
print(data.iloc[:10, :3])
#Answer: Not sure why it printed the output in two parts? 
# #ACC_X  ACC_Y  ACC_Z
# 0   32.0   32.0   32.0
# 1  -53.0  -30.0   16.0
# 2  -54.0  -30.0   16.0
# 3  -54.0  -31.0   15.0
# 4  -54.0  -30.0   18.0
#    ACC_X  ACC_Y  ACC_Z
# 0   32.0   32.0   32.0
# 1  -53.0  -30.0   16.0
# 2  -54.0  -30.0   16.0
# 3  -54.0  -31.0   15.0
# 4  -54.0  -30.0   18.0
# 5  -55.0  -29.0   16.0
# 6  -54.0  -31.0   15.0
# 7  -55.0  -30.0   15.0
# 8  -56.0  -30.0   16.0
# 9  -52.0  -31.0   18.0

# %%
# Task 5. Please display the values of 'ACC_X' and 'ACC_Y' where 'ACC_X' is greater than 30
#         (Hint. Use `data.loc[]`)
print(data.loc[data['ACC_X'] > 30,['ACC_X','ACC_Y']])
#Answer: 
# ACC_X  ACC_Y
# 0       32.0   32.0
# 47890   39.0  -40.0
# 48765   40.0  -36.0
# 50970   41.0  -51.0
# 51602   37.0  -36.0
# 51952   33.0  -46.0
# 53467   33.0  -33.0
# 53836   31.0  -11.0
# 59634   72.0  -72.0
# 59637   58.0  -56.0

# %%
# Task 6. Run `data.describe()`.
print(data.describe())
#Answer: This is making sense to me now. Could use this to obtain descriptive summaries of my data
#  ACC_X         ACC_Y         ACC_Z
# count  64951.000000  64951.000000  64951.000000
# mean     -47.476836    -28.775246     20.673338
# std       15.454966      8.197455     18.704717
# min     -112.000000   -100.000000    -61.000000
# 25%      -58.000000    -30.000000      8.000000
# 50%      -55.000000    -28.000000     12.000000
# 75%      -33.000000    -25.000000     39.000000
# max       72.000000     67.000000    124.000000

# %%
# Task 7. Get the mean, std, min, and max of each colum using different methods.
#         (Hint. `data.mean()`)
print(data.mean())
#Answer:
# ACC_X   -47.476836
# ACC_Y   -28.775246
# ACC_Z    20.673338


print(data.std())
#Answer: 
# ACC_X    15.454966
# ACC_Y     8.197455
# ACC_Z    18.704717

print(data.min())
print(data.max())
#Answer: 
# ACC_X   -112.0 min values
# ACC_Y   -100.0
# ACC_Z    -61.0
# dtype: float64

# ACC_X     72.0 max values 
# ACC_Y     67.0
# ACC_Z    124.0
# dtype: float64

print(data['ACC_X'].mean())
#Answer: Was testing how to calculate mean for a specific column only 
#-47.47683638435128
