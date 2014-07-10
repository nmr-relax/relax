#!/usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
# Copyright (C) 2014 Troels E. Linnet                                         #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

"""Python script for obtaining profiling statistics for multiple models between the current and an alternative version of relax.

There are 2 ways to use this script.  The first is to modify the path variable in this script and then run it as:

$ ./disp_profile_single.py

The second is to run this by supplying the relax path:

$ ./disp_profile_single.py /data/relax/tags/3.2.1
"""

# Python module imports.
from numpy import average, arange, array, float64, std, zeros
from os import pardir
from os.path import join
from re import search
from subprocess import PIPE, Popen
import sys

# Modify the system path to add the base directory of the current relax version.
sys.path.append(join(pardir, pardir, pardir, pardir))

# relax module imports.
import info


# The number of iterations to run each script for the statistics.
N = 10

# The models / The current scripts. / Iterations / Multiplication factors (to scale for different nr_iter values).
models = [
    ['No Rex', 'profiling_norex.py', 100, 1],
    ['LM63', 'profiling_lm63.py', 100, 1],
    ['LM63 3-site', 'profiling_lm63_3site.py', 100, 1],
    ['CR72', 'profiling_cr72.py', 100, 1],
    ['CR72 full', 'profiling_cr72_full.py', 100, 1],
    ['IT99',  'profiling_it99.py', 100, 1],
    ['TSMFK01', 'profiling_tsmfk01.py', 100, 1],
    ['B14', 'profiling_b14.py', 100, 1],
    ['B14 full', 'profiling_b14_full.py', 100, 1],
    ['NS CPMG 2-site expanded', 'profiling_ns_cpmg_2site_expanded.py', 100, 1],
    ['NS CPMG 2-site 3D', 'profiling_ns_cpmg_2site_3D.py', 10, 10],
    ['NS CPMG 2-site 3D full', 'profiling_ns_cpmg_2site_3D_full.py', 10, 10],
    ['NS CPMG 2-site star', 'profiling_ns_cpmg_2site_star.py', 10, 10],
    ['NS CPMG 2-site star full', 'profiling_ns_cpmg_2site_star_full.py', 10, 10],
    ['MMQ CR72', 'profiling_mmq_cr72.py', 100, 1],
    ['NS MMQ 2-site', 'profiling_ns_mmq_2site.py', 10, 10],
    ['NS MMQ 3-site linear', 'profiling_ns_mmq_3site_linear.py', 10, 10],
    ['NS MMQ 3-site', 'profiling_ns_mmq_3site.py', 10, 10],
    ['M61', 'profiling_m61.py', 100, 1],
    ['DPL94', 'profiling_dpl94.py', 100, 1],
    ['TP02', 'profiling_tp02.py', 100, 1],
    ['TAP03', 'profiling_tap03.py', 100, 1],
    ['MP05', 'profiling_mp05.py', 100, 1],
    ['NS R1rho 2-site', 'profiling_ns_r1rho_2site.py', 10, 10],
    ['NS R1rho 3-site linear', 'profiling_ns_r1rho_3site_linear.py', 10, 10],
    ['NS R1rho 3-site', 'profiling_ns_r1rho_3site.py', 10, 10],
]

# Path to the relax version.
path = '.'
if len(sys.argv) == 2:
    path = sys.argv[1]
current = False
if path == '.':
    current = True
    path = join(pardir, pardir, pardir, pardir)

# The Python executable name.
python = 'python'


# Print out the system information for the record.
info.print_sys_info()

# Initialise structures for the timing statistics.
timings = {}
for i in range(len(models)):
    # Alias.
    model, script, iter, scaling_factor = models[i]
    timings[model] = zeros((2, N), float64)

# Loop over the execution iterations.
for exec_iter in range(N):
    # Printout.
    print("\n\nExecution iteration %i\n" % (exec_iter+1))

    # Loop over each model.
    for i in range(len(models)):
        model, script, iter, scaling_factor = models[i]
        # The command to run.
        if current:
            cmd = "%s %s" % (python, script)
        else:
            cmd = "%s %s %s" % (python, script, path_new)

        # Printout.
        print("$ %s" % cmd)

        # Execute the current script.
        pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

        # Close the pipe.
        pipe.stdin.close()

        # Write all errors to stderr.
        err_lines = pipe.stderr.readlines()
        for line in err_lines:
            # Decode Python 3 byte arrays.
            if hasattr(line, 'decode'):
                line = line.decode()

            # Write.
            sys.stderr.write(line)

        # Process the output.
        index = 0
        for line in pipe.stdout.readlines():
            # Decode Python 3 byte arrays.
            if hasattr(line, 'decode'):
                line = line.decode()

            # Find the profiling stats for the target function method.
            if not search('func_', line):
                continue

            # Printout for the record.
            print(line[:-1])

            # Split the line.
            row = line.split()

            # The timing.
            timings[model][index, exec_iter] = float(row[3])

            # Increment the index.
            index += 1

# Statistics.
ave = {}
ave_cluster = {}
sd = {}
sd_cluster = {}

# Loop over the models.
for i in range(len(models)):
    # Alias.
    model, script, iter, scaling_factor = models[i]

    # The averages (scaled for different nr_iter).
    ave[model] = average(timings[model][0]) * scaling_factor
    ave_cluster[model] = average(timings[model][1]) * scaling_factor

    # The SD.
    sd[model] = std(timings[model][0]) * scaling_factor
    sd_cluster[model] = std(timings[model][1]) * scaling_factor

# Print background for analysis
fields = array([600. * 1E6, 800. * 1E6, 900. * 1E6])
relax_times = fields / (100 * 100. *1E6 )
cpmg_points = []
cpmg_points_nr = 0

spin_lock_offsets = range(10)
spin_lock_fields = [431.0, 651.2, 800.5, 984.0, 1341.11]
r1rho_points = []
r1rho_points_nr = 0

for i in range(len(fields)):
    ncyc = arange(2, 1000. * relax_times[i], 4)
    cpmg_point = ncyc / relax_times[i]
    cpmg_points_nr += len(cpmg_point)
    cpmg_points.append(cpmg_point)
    for j in range(len(spin_lock_offsets)):
        spin_lock_fields_oi = spin_lock_fields
        r1rho_points_nr += len(spin_lock_fields_oi)

# To nearest 10
cpmg_points_nr_near = int(round(cpmg_points_nr, -1))
cpmg_points_nr_near_per_frq = cpmg_points_nr_near / len(fields)

r1rho_points_nr_near = int(round(r1rho_points_nr, -1))
r1rho_points_nr_near_per_frq = r1rho_points_nr_near / len(fields)

print cpmg_points_nr_near, cpmg_points_nr_near_per_frq
print("""
##########################
#Background for analysis:#
##########################

For CPMG statistics:
--------------------
%i fields, with each %i nr of cpmg points.
Total number of dispersion points per spin is: %i

For R1rho experiments:
----------------------
%i fields, with each %i nr of spin lock offsets, where each offset has been measured at %i different spin lock fields.
Per field, there is %i dispersion points.
Total number of dispersion points per spin is: %i

"""%(len(fields), cpmg_points_nr_near_per_frq, cpmg_points_nr_near,
len(fields), len(spin_lock_offsets), len(spin_lock_fields), r1rho_points_nr_near_per_frq, r1rho_points_nr_near ))

# Final printout.
print("\n100 single spins analysis:")
for model, script, iter, scaling_factor in models:
    print("http://wiki.nmr-relax.com/%-25s  %7.3f+/-%.3f seconds" % (model.replace(' ', '_'), ave[model], sd[model]))

print("\nCluster of 100 spins analysis:")
for model, script, iter, scaling_factor in models:
    print("http://wiki.nmr-relax.com/%-25s  %7.3f+/-%.3f seconds" % (model.replace(' ', '_'), ave_cluster[model], sd_cluster[model]))
