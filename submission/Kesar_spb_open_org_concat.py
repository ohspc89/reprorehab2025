#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 10:12:29 2025

@author: trishakesar
"""
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns

# create file path and assign spb_file variables to multiple files in spb session

gait_filepath="/Users/trishakesar/Documents/Captain_Trisha/DS_Python_CEU_Fall20/2025data/NIA_SPB201_070924/Splitbelt/"
spb_file1="NIA_SPB201_070924_pretied_slow_028mps_01_Step_R.xls"
gait_df1= pd.read_csv(gait_filepath+spb_file1, delim_whitespace=True, header=None)
gait_df1= gait_df1.iloc[5:]   


#print(gait_df.head())

spb_file2="NIA_SPB201_070924_pretied_slow_028mps_02_Step_R.xls"
spb_file3="NIA_SPB201_070924_pretied_Fast_056mps_01_Step_R.xls"
spb_file4="NIA_SPB201_070924_pretied_Fast_056mps_02_Step_R.xls"

#open spb_file2 as second dataframe
gait_df2= pd.read_csv(gait_filepath+spb_file2, delim_whitespace=True, header=None)
gait_df2= gait_df2.iloc[5:]   

gait_df3= pd.read_csv(gait_filepath+spb_file3, delim_whitespace=True, header=None)
gait_df3= gait_df3.iloc[5:]   

gait_df4= pd.read_csv(gait_filepath+spb_file4, delim_whitespace=True, header=None)
gait_df4= gait_df4.iloc[5:]   

# concatenate two dataframes gait_df1 and gait_df2 
gait_concat= pd.concat([gait_df1, gait_df2, gait_df3, gait_df4], axis = 0, ignore_index = True)

gait_concat.to_csv(gait_filepath+"spb_concat.csv", index=False)

#lets plot column concaenated file as a simple time series 
#sns.lineplot(data=gait_concat, x=gait_concat.index, y=3)
#sns.lineplot(x=gait_concat.index, y=gait_concat[2])
#sns.lineplot(x=gait_concat.index, y=gait_concat.iloc[:, 1])
sns.lineplot(x=gait_concat.index, y=gait_concat.iloc[:, 1], marker='o')

plt.title("Gait Data Time Series - Step Length Y ")
plt.xlabel("Step Number")
plt.ylabel("Step Length Y Values")
plt.show()  


