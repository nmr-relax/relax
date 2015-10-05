#! /usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2013-2015 Edward d'Auvergne                                   #
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

"""Find all unused imports within all relax *.py files using the pylint program."""

# Python module imports.
from os import getcwd, path, sep, walk
from re import search
from subprocess import PIPE, Popen
import sys


# An exception list.
EXCEPTIONS = {
    'dep_check.py': ['bmrblib', 'bz2', 'cProfile', 'ctypes', 'epydoc', 'gzip', 'io', 'matplotlib', 'mpi4py', 'optparse', 'profile', 'pymol', 'readline', 'relax_fit', 'runpy', 'scipy', 'Structure', 'wx'],
    'lib/compat.py': ['IOBase', 'pickle', 'queue', 'StringIO', 'TextTestResult'],
    'lib/xml.py': ['array', 'float32', 'float64', 'inf', 'int16', 'int32'],
    'test_suite/shared_data/dispersion/profiling/profiling_b14.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_b14_full.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_cr72.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_cr72_full.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_dpl94.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_it99.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_lm63.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_lm63_3site.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_mmq_cr72.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_mp05.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_norex.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_cpmg_2site_3D.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_cpmg_2site_3D_full.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_cpmg_2site_expanded.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_cpmg_2site_star.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_cpmg_2site_star_full.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_mmq_2site.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_mmq_3site_linear.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_r1rho_2site.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_r1rho_3site.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_r1rho_3site_linear.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_ns_mmq_3site.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_tap03.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_tsmfk01.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_tp02.py': ['cluster', 'single'],
    'test_suite/shared_data/dispersion/profiling/profiling_m61.py': ['cluster', 'single'],
    'test_suite/unit_tests/_lib/_geometry/test_rotations.py': ['axis_angle_to_euler_xyx', 'axis_angle_to_euler_xyz', 'axis_angle_to_euler_xzx', 'axis_angle_to_euler_xzy', 'axis_angle_to_euler_yxy', 'axis_angle_to_euler_yxz', 'axis_angle_to_euler_yzx', 'axis_angle_to_euler_yzy', 'axis_angle_to_euler_zxy', 'axis_angle_to_euler_zxz', 'axis_angle_to_euler_zyx', 'axis_angle_to_euler_zyz', 'euler_to_axis_angle_xyx', 'euler_to_axis_angle_xyz', 'euler_to_axis_angle_xzx', 'euler_to_axis_angle_xzy', 'euler_to_axis_angle_yxy', 'euler_to_axis_angle_yxz', 'euler_to_axis_angle_yzx', 'euler_to_axis_angle_yzy', 'euler_to_axis_angle_zxy', 'euler_to_axis_angle_zxz', 'euler_to_axis_angle_zyx', 'euler_to_axis_angle_zyz', 'euler_to_R_xyx', 'euler_to_R_xyz', 'euler_to_R_xzx', 'euler_to_R_xzy', 'euler_to_R_yxy', 'euler_to_R_yxz', 'euler_to_R_yzx', 'euler_to_R_yzy', 'euler_to_R_zxy', 'euler_to_R_zxz', 'euler_to_R_zyx', 'euler_to_R_zyz', 'R_to_euler_xyx', 'R_to_euler_xyz', 'R_to_euler_xzx', 'R_to_euler_xzy', 'R_to_euler_yxy', 'R_to_euler_yxz', 'R_to_euler_yzx', 'R_to_euler_yzy', 'R_to_euler_zxy', 'R_to_euler_zxz', 'R_to_euler_zyx', 'R_to_euler_zyz'],
    'test_suite/unit_tests/_lib/test_regex.py': ['regex']
}

# Hacks for circular imports - these should rather be fixed.
EXCEPTIONS['test_suite/unit_tests/_lib/test___init__.py'] = EXCEPTIONS['test_suite/unit_tests/_lib/_geometry/test_rotations.py']
EXCEPTIONS['test_suite/unit_tests/_lib/_geometry/test___init__.py'] = EXCEPTIONS['test_suite/unit_tests/_lib/_geometry/test_rotations.py']


# The directory to use.
if len(sys.argv) == 2:
    directory = sys.argv[1]
else:
    directory = getcwd()

# Walk through the current dir.
for root, dirs, files in walk(directory):
    # Skip SVN directories.
    if search("svn", root):
        continue

    # Loop over the files.
    for file in files:
        # Only check Python files.
        if not search("\.py$", file):
            continue

        # Full path to the file.
        path = root + sep + file

        # Does the file have exceptions?
        exceptions = []
        for key in EXCEPTIONS:
            if search(key, path):
                for exc in EXCEPTIONS[key]:
                    exceptions.append("Unused import %s" % exc)

        # The command.
        cmd = 'pylint %s' % path

        # Execute.
        pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

        # Close the pipe.
        pipe.stdin.close()

        # Only display the import information.
        title_flag = True
        for line in pipe.stdout.readlines():
            if search("Unused import", line):
                # Exceptions.
                skip = False
                for exc in exceptions:
                    if search(exc, line):
                        skip = True
                if skip:
                    continue

                # First write out the file name, once.
                if title_flag:
                    sys.stdout.write("File %s :\n" % path)
                    title_flag = False

                # Then the unused import line.
                sys.stdout.write("    %s\n" % line[:-1])

        # Check for errors.
        err = False
        for line in pipe.stderr.readlines():
            if search("command not found", line):
                err = True
        if err:
            sys.exit()
