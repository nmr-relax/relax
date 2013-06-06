"""Script for simulating relaxation curves for an on resonance R1rho-type experiment.

To run the script, simply type:

$ ../../../../relax generate.py
"""

# Python module imports.
from math import exp

# relax module imports.
from lib.software.sparky import write_list


# Setup for 2 spin systems.
rx = [2.25, 24.0]    # The relaxation rates.
i0 = [100000.0, 20000.0]    # Initial peak intensities.
times = [0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.15]    # The relaxation delay times in seconds.

# Setup for the Sparky peak list.
res_names = ['Trp', 'Trp']
res_nums = [1, 1]
atom1_names = ['N', 'NE1']
atom2_names = ['HN', 'HE1']
w1 = [122.454, 111.978]
w2 = [8.397, 8.720]

# The simulated intensities.
intensities = []
for i in range(len(times)):
    intensities.append([])
    for j in range(len(rx)):
        intensities[i].append(i0[j] * exp(-rx[j]*times[i]))
print("Peak intensities:  %s" % intensities)

# Loop over the relaxation times.
for i in range(len(times)):
    # Create a Sparky .list file.
    write_list(file_prefix='ncyc_%s' % (i+1), dir=None, res_names=res_names, res_nums=res_nums, atom1_names=atom1_names, atom2_names=atom2_names, w1=w1, w2=w2, data_height=intensities[i])

