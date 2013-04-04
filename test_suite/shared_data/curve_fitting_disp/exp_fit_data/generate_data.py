# Script for generating Sparky peak lists for a simple exponential model set.

# Python module imports.
from math import exp

# relax module imports.
from lib.software.sparky import write_list


# The data (res name, res num, R2eff, R2eff, I0, I0).
res_data = [
    ['Asp', 1, 15, 10, 20000, 25000],
    ['Gly', 2, 12, 11, 50000, 51000],
    ['Lys', 3, 17, 9, 100000, 96000]
]

# Create some data structures for the sparky function.
res_names = []
res_nums = []
atom1_names = []
atom2_names = []
w1 = []
w2 = []
for i in range(len(res_data)):
    res_names.append(res_data[i][0])
    res_nums.append(res_data[i][1])
    atom1_names.append('N')
    atom2_names.append('H')
    w1.append(0.0)
    w2.append(0.0)

# The relaxation times to use (seconds).
times = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12]
for time in times:
    # The file names.
    file1 = 'nu_1kHz_relaxT_%.2f' % time
    file2 = 'nu_2kHz_relaxT_%.2f' % time

    # Calculate the peak intensities.
    heights1 = []
    heights2 = []
    for i in range(len(res_data)):
        # Append the intensities.
        heights1.append(res_data[i][4] * exp(-res_data[i][2] * time))
        heights2.append(res_data[i][5] * exp(-res_data[i][3] * time))

    # Write out the file.
    write_list(file_prefix=file1, res_names=res_names, res_nums=res_nums, atom1_names=atom1_names, atom2_names=atom2_names, w1=w1, w2=w2, data_height=heights1)
    write_list(file_prefix=file2, res_names=res_names, res_nums=res_nums, atom1_names=atom1_names, atom2_names=atom2_names, w1=w1, w2=w2, data_height=heights2)
