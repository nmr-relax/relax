#! /usr/bin/env python

# Script for manually compiling the C modules for different Python targets.

from os import system


# The target.
target = '~ python3.2'

# The list of build commands to run.
cmd = []

# Python 3.2 installed in the home directory.
if target == '~ python3.2':
    cmd.append("gcc -o maths_fns/c_chi2.os -c -I~/include/python3.2m -I~/lib/python3.2/site-packages/numpy/core/include -fPIC maths_fns/c_chi2.c")
    cmd.append("gcc -o maths_fns/exponential.os -c -I~/include/python3.2m -I~/lib/python3.2/site-packages/numpy/core/include -fPIC maths_fns/exponential.c")
    cmd.append("gcc -o maths_fns/relax_fit.os -c -I~/include/python3.2m -I~/lib/python3.2/site-packages/numpy/core/include -fPIC maths_fns/relax_fit.c")
    cmd.append("gcc -o maths_fns/relax_fit.so -shared maths_fns/c_chi2.os maths_fns/exponential.os maths_fns/relax_fit.os")


# Execute the commands.
for i in range(len(cmd)):
    print(cmd[i])
    system(cmd[i])
