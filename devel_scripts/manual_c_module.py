#! /usr/bin/env python3
###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

# Script for manually compiling the C modules for different Python targets.

from os import system
import sys


# The target.
target = sys.argv[1]
path = '/data/python/'
if len(sys.argv) == 3:
    path = sys.argv[2]

# The list of build commands to run.
cmd = []

# Python.h.
include = '%s/include/python%s/' % (path, target)
if target in ['3.2', '3.3', '3.4', '3.5']:
    include = '%s/include/python%sm/' % (path, target)

# Python 3.2 installed in the home directory.
cmd.append("gcc -o target_functions/c_chi2.os -c -I%s -fPIC target_functions/c_chi2.c" % include)
cmd.append("gcc -o target_functions/exponential.os -c -I%s -fPIC target_functions/exponential.c" % include)
cmd.append("gcc -o target_functions/exponential_inv.os -c -I%s -fPIC target_functions/exponential_inv.c" % include)
cmd.append("gcc -o target_functions/exponential_sat.os -c -I%s -fPIC target_functions/exponential_sat.c" % include)
cmd.append("gcc -o target_functions/relax_fit.os -c -I%s -fPIC target_functions/relax_fit.c" % include)
cmd.append("gcc -o target_functions/relax_fit.so -shared target_functions/c_chi2.os target_functions/exponential.os target_functions/exponential_inv.os target_functions/exponential_sat.os target_functions/relax_fit.os")


# Execute the commands.
for i in range(len(cmd)):
    print(cmd[i])
    system(cmd[i])
