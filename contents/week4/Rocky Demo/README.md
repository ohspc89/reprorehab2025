# Week 4: Pandas Demo with Rocky

## Demo 1
In this demo, we will work with a 3D motion capture file. This file contains XYZ motion capture data from 1 marker that was saved as 7 different markers. A new marker was generated in the data file every time the true marker left the visual field and re-entered; therefore, there are gaps in motion capture data.

First, we open the file, ignoring irrelevant headers. Second, we combine all 7 "markers" into one true marker. Third, we plot the updated results. Fourth, we interpolate the data to fill in missing values. Last, we will explore different mathematical manipulations that can be done with position data.
