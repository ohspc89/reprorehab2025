#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 11:24:32 2025

@author: rmazorow
"""

# import packages
import pandas as pd

# Open file for demo 1
filename = '/Users/rmazorow/Documents/reprorehab2025/contents/week4/Rocky Demo/Cognitive_Ex.xlsx';
sheet1 = pd.read_excel(filename, sheet_name='TrailsAB')
sheet2 = pd.read_excel(filename, sheet_name='Trails3')


#Use `pandas.DataFrame.pivot()`
sheet2_wide = sheet2.pivot(index='SubID', columns='Session',values='Score')

# Rename coumns
sheet2_wide.columns = ['_S'.join(('Trails3', str(c))) for c in sheet2_wide.columns]
# If you skip this command, 'id' will stay as index.
sheet2_wide = sheet2_wide.reset_index()

# Merge tables
cogn = pd.merge(sheet1,sheet2_wide,on='SubID')
allTrails = cogn.iloc[:,-6:]

# Correlation
correlation_matrix = allTrails.corr()

# Plot heatmap
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure()    #figsize=(6, 5)) # Adjust figure size as needed
# annot=True: Displays the correlation values on the heatmap cells.
# cmap='coolwarm': Sets the color map. 'coolwarm' is a good choice for correlations as it shows positive correlations in one color range and negative in another, with white/light colors for near-zero correlations. Other options include 'viridis', 'plasma', 'magma', etc.
# fmt=".2f": Formats the annotation values to two decimal places.
# linewidths=.5: Adds lines between cells for better visual separation.
# square=True: fixes shape to square
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, square=True)
plt.title('Correlation Matrix of Trails Tests')


# What if just upper?
import numpy as np
# 3. Generate a mask for the upper triangle
# np.ones_like(corr_matrix, dtype=bool) creates a boolean array of the same shape as corr_matrix filled with True values.
# np.triu(..., k=1) then sets all elements below the main diagonal (and the diagonal itself, if k=0) to False. With k=1, the diagonal is also excluded, resulting in a mask for only the strict upper triangle.
# The k=0 argument does not show the diagonal
mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=0)
# 4. Plot the heatmap with the mask
sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, square=True)
plt.title('Upper Triangle of Correlation Matrix')
