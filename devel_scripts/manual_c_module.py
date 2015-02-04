#! /usr/bin/env python

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
if target == '3.2':
    include = '%s/include/python3.2m/' % path
elif target == '3.3':
    include = '%s/include/python3.3m/' % path
elif target == '3.4':
    include = '%s/include/python3.4m/' % path

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
