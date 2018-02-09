import numpy as np
import peakutils

thresh = 0.67
min_dist = 10

data_180 = np.loadtxt('../data/data_180.txt')
data_150 = np.loadtxt('../data/data_150.txt')
data_120 = np.loadtxt('../data/data_120.txt')

total_time = len(data_150)/75

peaks_150 = peakutils.indexes(data_150, thresh, min_dist)
no_peaks_150 = len(peaks_150)

peaks_180 = peakutils.indexes(data_180, thresh, min_dist)
no_peaks_180 = len(peaks_180)

peaks_120 = peakutils.indexes(data_120, thresh, min_dist)
no_peaks_120 = len(peaks_120)

bpm_120 = (no_peaks_120/total_time) * 60
bpm_150 = (no_peaks_150/total_time) * 60
bpm_180 = (no_peaks_180/total_time) * 60

print("120 BPM is: "+str(bpm_120))
print("150 BPM is: "+str(bpm_150))
print("180 BPM is: "+str(bpm_180))