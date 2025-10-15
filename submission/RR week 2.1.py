# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 21:10:29 2025

@author: Ryan
"""
#%%
import pandas as pd

data = pd.read_csv('mental_health_wearable_data.csv', sep=',')
data.columns
data.rename(columns={'Heart_Rate_BPM': 'HR_BPM'}, inplace=True)
data.rename(columns={x:y for x,y in zip(data.columns, ['A', 'B', 'C', 'D', 'E'])}, inplace=True)
data.dtypes
data.describe()
data.iloc[:2,2:]
data.plot.hist(column='A', 
              alpha=0.6, edgecolor='k',
              facecolor='pink', title='Heart Rate BPM', legend=False)

# %% Task 1 Check the structure of the data
import pandas as pd
data = pd.read_csv('ACC.csv')
data.head()
data.info()
# 4 rows, 3 columns; all floats
# name of columns: 2013-02-25 18:00:59; .1; .2

# Task 2: Print names of columns
data.columns

# Task 3: Change Columns Names
data.rename(columns={x:y for x, y in zip(data.columns, ['ACC_X', 'ACC_Y', 'ACC_Z'])}, inplace=True) 
data.columns   

#Task 4 Display 1st 10 rows and 3 columons
data.iloc[:10, :]     

#Task 5. Display values of acc_x and y where x is greater than 30
data.loc[data['ACC_X']>30, ['ACC_X', 'ACC_Y']]

#Task 6. Run Data.describe
data.describe()

#Task 7. Get Mean, std, min, mode
data.mean()
data.std()
data.min()
data.max()


# %% Extra Reading a more complicated file 
## Task E1. How many rows would you skip?
import pandas as pd
nskip = 10
data = pd.read_csv('nmB.tsv', sep='\t', skiprows=nskip)

# Task E2 Read dataset using `nskip` you defined earlier
mocap = pd.read_csv('nmB.tsv', sep='\t', skiprows=nskip, engine='c')

#Task E3 1st 100 rows
subset = data.iloc[:100]
subset.shape

#Task E4 Let's draw line plots using columns: 's2 X' & 's3 X'
subset.plot.line(y=['s2 X', 's3 X'])