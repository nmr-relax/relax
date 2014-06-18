#!/usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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

# Python script for obtaining profiling statistics for multiple models between the current and an alternative version of relax.

# Python module imports.
from numpy import average, float64, std, zeros
from os import sep
from re import search
from shutil import copyfile
from subprocess import PIPE, Popen
import sys


# The number of iterations to run each script for the statistics.
N = 10

# The models.
models = [
    'CR72',
    'TSMFK01',
    'B14',
    'NS CPMG 2-site expanded',
    'NS CPMG 2-site 3D'
]

# The current scripts.
scripts = [
    'profiling_cr72.py',
    'profiling_tsmfk01.py',
    'profiling_b14.py',
    'profiling_ns_cpmg_2site_expanded.py',
    'profiling_ns_cpmg_2site_3D.py'
]

# Multiplication factors (to scale for different nr_iter values).
scaling_factor = [
    1.0,
    1.0,
    1.0,
    1.0,
    10.0
]

# Path to relax 3.2.2, or any other version.
alt_path = '/data/relax/tags/3.2.2'

# The Python executable name.
python = 'python'


# Copy the current scripts to the base directory of the alternative relax version.
for script in scripts:
    copyfile(script, alt_path+sep+script)

# Initialise structures for the timing statistics.
timings_new = {}
timings_alt = {}
for model in models:
    timings_new[model] = zeros((2, N), float64)
    timings_alt[model] = zeros((2, N), float64)
timings = [timings_new, timings_alt]

# Loop over the execution iterations.
for exec_iter in range(N):
    # Printout.
    print("\n\nExecution iteration %i\n" % (exec_iter+1))

    # Loop over each model.
    for i in range(len(models)):
        # The commands to run.
        cmds = [
            "%s %s" % (python, scripts[i]),
            "%s %s %s" % (python, alt_path+sep+scripts[i], alt_path),
        ]

        # Loop over the commands.
        for cmd_index in range(2):
            # Printout.
            print("$ %s" % cmds[cmd_index])

            # Execute the current script.
            pipe = Popen(cmds[cmd_index], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

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
                timings[cmd_index][models[i]][index, exec_iter] = float(row[3])

                # Increment the index.
                index += 1

# Statistics.
ave_new = {}
ave_new_cluster = {}
ave_alt = {}
ave_alt_cluster = {}
sd_new = {}
sd_new_cluster = {}
sd_alt = {}
sd_alt_cluster = {}
speed_up = {}
speed_up_cluster = {}

# Loop over the models.
for i in range(len(models)):
    # Alias.
    model = models[i]

    # The averages (scaled for different nr_iter).
    ave_new[model] = average(timings_new[model][0]) * scaling_factor[i]
    ave_new_cluster[model] = average(timings_new[model][1]) * scaling_factor[i]
    ave_alt[model] = average(timings_alt[model][0]) * scaling_factor[i]
    ave_alt_cluster[model] = average(timings_alt[model][1]) * scaling_factor[i]

    # The SD.
    sd_new[model] = std(timings_new[model][0]) * scaling_factor[i]
    sd_new_cluster[model] = std(timings_new[model][1]) * scaling_factor[i]
    sd_alt[model] = std(timings_alt[model][0]) * scaling_factor[i]
    sd_alt_cluster[model] = std(timings_alt[model][1]) * scaling_factor[i]

    # The speed up.
    speed_up[model] = ave_alt[model] / ave_new[model]
    speed_up_cluster[model] = ave_alt_cluster[model] / ave_new_cluster[model]

# Final printout.
print("\n\n100 single spins analysis:")
for model in models:
    print("%-10s:  %.3f+/-%.3f -> %.3f+/-%.3f, %.3fx faster." % (model, ave_alt[model], sd_alt[model], ave_new[model], sd_new[model], speed_up[model]))
print("\nCluster of 100 spins analysis:")
for model in models:
    print("%-10s:  %.3f+/-%.3f -> %.3f+/-%.3f, %.3fx faster." % (model, ave_alt_cluster[model], sd_alt_cluster[model], ave_new_cluster[model], sd_new_cluster[model], speed_up_cluster[model]))
