#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 09:51:49 2025

@author: rmazorow


In this demo, we will work with a 3D motion capture file. This file contains 
XYZ motion capture data from 1 marker that was saved as 7 different markers. A 
new marker was generated in the data file every time the true marker left the 
visual field and re-entered; therefore, there are gaps in motion capture data.

First, we open the file, ignoring irrelevant headers. Second, we combine all 7 
"markers" into one true marker. Third, we plot the updated results. Fourth, we 
interpolate the data to fill in missing values. Last, we will explore different 
mathematical manipulations that can be done with position data.
"""

# import packages
import pandas as pd
import os

# To properly read in the files, we want to make sure that your working directory
# is the week 4 demo. This allows us to simply refer to files in that folder.
# Replace the path below with your computer path.
os.chdir('/Users/rmazorow/Documents/reprorehab2025/contents/week4/Rocky Demo/')



# STEP 1: Open file for demo
filename = 'MotionCapture_Ex.csv';
# This will open all rows of the csv files.
file1 = pd.read_csv(filename)
# This allows us to skip the extra header rows.
# I skipped 7 instead of 8 so that row 8 became the column names.
file1 = pd.read_csv(filename, skiprows=7)
# Notice that we cannot have duplicate names, so .# was added to duplicates.
file1.columns

# If we plot the current X data we can see the actual gaps in data.
# Since this should all be one marker, we want to merge the 7 variables into one
# that resembles this figure.
# Here we use pandas plot function.
file1.plot.line(x='Time (Seconds)', y=['X','X.1','X.2','X.3','X.4','X.5','X.6'])



# STEP 2: Combine data into one marker with XYZ values
# First we want to create a new dataframe to hold the single marker data. We
# could instead modify the original and then remove columns, but I prefer to 
# start with an empty variable.
# In the line below, we create a dataframe that contains a copy of the time
# column from our input file.
motion = pd.DataFrame({'time': file1['Time (Seconds)'].copy()})

# Next we generate the XYZ columns by looking across the rows for the 7 markers 
# in file1 and choosing the first numeric values for each row. If all row values
# are NA or NaN (not a number), then NA will be saved in that row. 
# The function df.fillna() performs this operation for us.
motion['X'] = file1['X'].fillna(file1['X.1']).fillna(file1['X.2']).fillna(file1['X.3']).fillna(file1['X.4']).fillna(file1['X.5']).fillna(file1['X.6'])
motion['Y'] = file1['Y'].fillna(file1['Y.1']).fillna(file1['Y.2']).fillna(file1['Y.3']).fillna(file1['Y.4']).fillna(file1['Y.5']).fillna(file1['Y.6'])
motion['Z'] = file1['Z'].fillna(file1['Z.1']).fillna(file1['Z.2']).fillna(file1['Z.3']).fillna(file1['Z.4']).fillna(file1['Z.5']).fillna(file1['Z.6'])



# STEP 3: Plot the new marker data
# We can see that the data was successfully combined into 1 marker.
# Here we use pandas plot function again. 
#   x = 'time'              => plot time as x-axis
#   y = ['X','Y','Z']       => plot X,Y,Z versus time
#   subplots = True         => plot each variable defined in y in separate plots
#   xlabel = 'Time (s)'     => define label for x-axis
#   ylabel = 'Position (m)' => define label for y-axis
#   color = ['k','r','b']   => assign colors to each y variable (black, red, blue)
motion.plot.line(subplots=True,
                 x='time', y=['X','Y','Z'],
                 xlabel='Time (s)',
                 ylabel='Position (m)',
                 color = ['k','r','b'])



# STEP 4: Interpolate data
# We have not discussed this so far, but since we have a view mocap researchers,
# I wanted to show how we can use df.interpolate() to fill in missing data (NAs)
# in the middle of true data. This will not fill in NAs at the start or end of
# a collection. In this case, I tell python to interpolate using a cubic spline
# along the rows of each column (axis = 0). If you wanted to go along the columns,
# then use axis = 1.
motion = motion.interpolate(method='cubic', axis = 0)

# We can plot again to see that there are no longer gaps in our data
motion.plot.line(subplots=True,
                 x='time', y=['X','Y','Z'],
                 xlabel='Time (s)',
                 ylabel='Position (m)',
                 color = ['k','r','b'])



# STEP 5: Mathematical Maniputations
# This data is collected in meters, but we can convert it into cm
motion[['X','Y','Z']] = motion[['X','Y','Z']].multiply(100, axis=0)

# Calculate and plot speed
# Speed can be calculated by change in distance / change in time
# Change in time is calcualted by 1/sampling rate
samplingRate = 120
timePerSample = 1/samplingRate
# Change in distance can be calculated using the df.diff() function
motion['speedX'] = (motion['X'].diff())/timePerSample
# Plot the speed in the x direction
motion.plot.line( x='time', y='speedX',
                 xlabel='Time (s)',
                 ylabel='Speed (cm/s)')

# Calculate total distance traveled
# We use df.diff() again to calculate the distance in the X, Y, and Z directions
# between each sample (row2 = row2 - row1). We then calculate the euclidean 
# distance across all 3 dimensions before summing across the columns, ignoring 
# the NA values.
import numpy as np
totalDist = np.nansum(np.sqrt(motion['X'].diff()**2 + motion['Y'].diff()**2 + motion['Z'].diff()**2))
