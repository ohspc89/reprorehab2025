# Week 5: Plotting in Python (Matplotlib & Seaborn)

After reviewing this week's material, you will be able to:
- Create and customize figures using **Matplotlib** & **Seaborn**
- Control **figure layouts** using `subplots()` and `GridSpec`
- Add **legends**, **titles**, and **annotations**
- Draw **scatterplots**, **histograms**, and **2D histograms**
- Work with **multiple axes** and secondary y-axes
- Save figures as publication-ready images (`.png`)

## 🧩 Slies: [Plotting with Matplotlib](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week5/Plotting%20with%20Matplotlib.pdf)
These slides walk through:
- Setting up Spyder to view interactive plots (Qt backend)
- Anatomy of a Matplotlib figure (`Figure`, `Axes`)
- How to use `plt.subplots()` for multiple plots
- Examples of line, scatter, and histogram plots
- Layout customization with **GridSpec**

## 📘 Main Notebook: [Plotting with Matplotlib](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week5/plotting_with_matplotlib.py)
This notebook introduces the foundation of Matplotlib plotting through practical examples using real world datasets (PysioNet gait and RR interval data).

### Topics Covered
- Create figures using `plt.subplots()`
- Customize titles, axis labels, and spines
- Add vertical/horizontal lines and annotations (`ax.axvline`, `ax.text`)
- Adjust axis limits with `ax.set_xlim()` and `ax.set_ylim()`
- Draw multiple histograms in one figure (`2 x 4` layout)
- Compare histogram styles
- Add titles, labels, and legends for each subplot
- Learn to use `fig.suptitle()` and `plt.tight_layout()`
- Combine plots of different shapes and sizes (e.g., 2:1 top ratio, full-width bottom)
- Mix multiple visualization types (`lineplot`, `hexbin`, etc.)
- Practice organizing visual information effectively 

## 🧮 Assignment: [Week5_Assignment](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week5/Week5_assignment.py)

- Task 1: Timeseries with moving average & normalization
- Task 2: Scatterplot & Histogram
- Task 3: Custom Layout (GridSpec)

## 🧭 Extra: [Seaborn: Statistical Data Visualization](https://github.com/ohspc89/reprorehab2025/blob/students/contents/week5/visualization_seaborn.py)
This script introduces **Seaborn**, a high-level interface built on top of Matplotlib.

### Topics Covered
- Plotting EEG data from PhysioNet
- Cleaning column names using `.strip()`
- Visualizing timestamp intervals using `sns.histplot`, `sns.kdeplot`, and `sns.ecdfplot`
- Formatting axis tick labels using `ticker.FuncFormatter`
- Working with time zones (`Europe/Rome`) and datetime formatting
- Comparing **long** vs. **wide** data formats for plotting
- Creating multi-panel figures using **FacetGrid**
