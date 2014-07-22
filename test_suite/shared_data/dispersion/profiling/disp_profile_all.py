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

There are 3 ways to use this script.  The first is to modify the path_new and path_old variables in this script, where path_new is the newer relax version, and then run it as:

$ ./disp_profile_all.py

The second is to run this by supplying the path of the alternate relax version:

$ ./disp_profile_all.py /data/relax/tags/3.2.1

The final way is to supply the path for both relax versions, where the first argument is the newer version of relax:

$ ./disp_profile_all.py /data/relax/tags/3.2.2 /data/relax/tags/3.2.1
"""

# Python module imports.
from numpy import average, arange, array, float64, std, zeros
from os import pardir, path, sep
from re import search
from shutil import copyfile
from subprocess import PIPE, Popen
import sys

# Modify the system path to add the base directory of the current relax version.
sys.path.append(path.join(pardir, pardir, pardir, pardir))

# relax module imports.
import info


# The number of iterations to run each script for the statistics.
N = 10

# The models / The current scripts. / Iterations / Multiplication factors (to scale for different nr_iter values).
models = [
    ['No Rex', 'profiling_norex.py', 100, 1],
    ['LM63', 'profiling_lm63.py', 100, 1],
    ['CR72', 'profiling_cr72.py', 100, 1],
    ['CR72 full', 'profiling_cr72_full.py', 100, 1],
    ['IT99',  'profiling_it99.py', 100, 1],
    ['TSMFK01', 'profiling_tsmfk01.py', 100, 1],
    ['B14', 'profiling_b14.py', 100, 1],
    ['B14 full', 'profiling_b14_full.py', 100, 1],
    ['NS CPMG 2-site 3D', 'profiling_ns_cpmg_2site_3D.py', 10, 10],
    ['NS CPMG 2-site 3D full', 'profiling_ns_cpmg_2site_3D_full.py', 10, 10],
    ['NS CPMG 2-site expanded', 'profiling_ns_cpmg_2site_expanded.py', 100, 1],
    ['NS CPMG 2-site star', 'profiling_ns_cpmg_2site_star.py', 10, 10],
    ['NS CPMG 2-site star full', 'profiling_ns_cpmg_2site_star_full.py', 10, 10],
    ['M61', 'profiling_m61.py', 100, 1],
    ['DPL94', 'profiling_dpl94.py', 100, 1],
    ['TP02', 'profiling_tp02.py', 100, 1],
    ['TAP03', 'profiling_tap03.py', 100, 1],
    ['MP05', 'profiling_mp05.py', 100, 1],
    ['NS R1rho 2-site', 'profiling_ns_r1rho_2site.py', 10, 10],
]

# Paths to the two relax versions.
path_new = '.'
path_old = '/data/relax/tags/3.2.2'
if len(sys.argv) == 3:
    path_new = sys.argv[1]
    path_old = sys.argv[2]
elif len(sys.argv) == 2:
    path_old = sys.argv[1]
current = False
if path_new == '.':
    current = True
    path_new = path.join(pardir, pardir, pardir, pardir)

# The Python executable name.
python = 'python'


# First print out the system information for the record.
info.print_sys_info()

# Then a printout of the relax versions to be compared.
data = [
    ['New', path_new],
    ['Old', path_old]
]
sys.stdout.write("\n\n")
for iter, path in data:
    # Intro text.
    sys.stdout.write("\n%s relax version:  " % iter)

    # The command to obtain the version.
    cmd = "cd %s; ./relax -v" % path
    pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

    # Close the pipe.
    pipe.stdin.close()

    # Write out the output.
    for line in pipe.stdout.readlines():
        sys.stdout.write(line[:-1])
sys.stdout.write("\n\n\n\n")

# Initialise structures for the timing statistics.
timings_new = {}
timings_alt = {}
for i in range(len(models)):
    # Alias.
    model, script, iter, scaling_factor = models[i]
    timings_new[model] = zeros((2, N), float64)
    timings_alt[model] = zeros((2, N), float64)
timings = [timings_new, timings_alt]

# Loop over the execution iterations.
for exec_iter in range(N):
    # Printout.
    print("\n\nExecution iteration %i\n" % (exec_iter+1))

    # Loop over each model.
    for i in range(len(models)):
        model, script, iter, scaling_factor = models[i]
        # The commands to run.
        cmds = []
        if current:
            cmds.append("%s %s" % (python, script))
        else:
            cmds.append("%s %s %s" % (python, script, path_new))
        cmds.append("%s %s %s" % (python, script, path_old))

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
                timings[cmd_index][model][index, exec_iter] = float(row[3])

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
    model, script, iter, scaling_factor = models[i]

    # The averages (scaled for different nr_iter).
    ave_new[model] = average(timings_new[model][0]) * scaling_factor
    ave_new_cluster[model] = average(timings_new[model][1]) * scaling_factor
    ave_alt[model] = average(timings_alt[model][0]) * scaling_factor
    ave_alt_cluster[model] = average(timings_alt[model][1]) * scaling_factor

    # The SD.
    sd_new[model] = std(timings_new[model][0]) * scaling_factor
    sd_new_cluster[model] = std(timings_new[model][1]) * scaling_factor
    sd_alt[model] = std(timings_alt[model][0]) * scaling_factor
    sd_alt_cluster[model] = std(timings_alt[model][1]) * scaling_factor

    # The speed up.
    speed_up[model] = ave_alt[model] / ave_new[model]
    speed_up_cluster[model] = ave_alt_cluster[model] / ave_new_cluster[model]

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
for i in range(len(models)):
    # Alias.
    model, script, iter, scaling_factor = models[i]
    print("%-25s  %7.3f+/-%.3f -> %7.3f+/-%.3f, %7.3fx faster." % (model+':', ave_alt[model], sd_alt[model], ave_new[model], sd_new[model], speed_up[model]))

print("\nCluster of 100 spins analysis:")
for i in range(len(models)):
    # Alias.
    model, script, iter, scaling_factor = models[i]
    if model == 'IT99':
        comment = "IT99: Cluster of only 1 spin analysis, since v. 3.2.2 had a bug with clustering analysis.:"
    else:
        comment = ""
    print("%-25s  %7.3f+/-%.3f -> %7.3f+/-%.3f, %7.3fx faster. %s" % (model+':', ave_alt_cluster[model], sd_alt_cluster[model], ave_new_cluster[model], sd_new_cluster[model], speed_up_cluster[model], comment) )
