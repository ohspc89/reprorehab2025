#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 20:33:13 2025

@author: trishakesar
"""

import pandas as pd

# open a simple csv file called R01_Clinical_SS_Speed_Py.csv and save it as 
# variable data

filepath="/Users/trishakesar/Documents/Captain_Trisha/DS_Python_CEU_Fall20/2025data/"
data = pd.read_csv(filepath+"R01_Clinical_SS_Speed_Py.csv") 

# print the first 5 rows and last 5 rows of the data
print(data.head())
print (data.tail())
print(data.columns)


# subtract all columns from baseline and create new columns "data_change"
data_change = data.copy()

# subject columns for all post-training timepoints (P3, P6,FU_3wk, FU_6wk 
# from column 1 in data and save as new columns data_change
data_change['P3_change'] = data_change['P3'] - data_change['Pre']
data_change['P6_change'] = data_change['P6'] - data_change['Pre']
data_change['P12_change'] = data_change['P12'] - data_change['Pre']
data_change['FU_3wk_change'] = data_change['FU_3wk'] - data_change['Pre']
data_change['FU_6wk_change'] = data_change['FU_6wk'] - data_change['Pre']

#print the new data_change file to see if this worked
print(data_change)

data_change.mean(axis=0)
data_change.std(axis=0)

#now we need to check by visualizing our data 

import matplotlib as plt
import seaborn as sns
sns.pairplot(data_change)
sns.boxplot(data=data_change)
plt.title('Boxplot of SS Speed')
plt.xlabel('Timepoint')
plt.ylabel('Gait Speed') 
plt.show()

#make a boxplot of only some of the columns not all data but only timepoints
data_change_subset = data_change[['Pre', 'P3', 'P6','P12', 'FU_3wk', 'FU_6wk']]
#sns.boxplot(data=data_change_subset)
#plt.xlabel('Timepoint')
#plt.ylabel('Gait Speed') 

#make a boxplot of only some of the columns not all data but only change columns
sns.boxplot(data=data_change_subset)
data_change_subset = data_change[['P3_change', 'P6_change','P12_change', 'FU_3wk_change', 'FU_6wk_change']]
sns.stripplot(data=data_change_subset, color='black', alpha=0.5)
# Add in points to show each observation

#make a boxplot of only some of the columns not all data but only change columns
sns.boxplot(data=data_change_subset)
data_change_subset = data_change[['P3_change', 'P6_change','P12_change', 'FU_3wk_change', 'FU_6wk_change']]
sns.stripplot(data=data_change_subset, color='black', alpha=0.5)

#sns.lineplot(data=data_change_subset, markers=True, dashes=False)

#save data_change as a new csv file called R01_Clinical_SS_Speed_Change_Py.csv
data_change.to_csv(filepath+"R01_Clin_SS_Speed_Change_Py.csv", index=False)

#save boxplot and lineplot as png files
plt.savefig(filepath+"boxplot_SS_speed_changes.png")
plt.savefig(filepath+"lineplot_SS_speed_changes.png")
plt.close()