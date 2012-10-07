#! /usr/bin/env python

# Script for manually compiling the C modules for different Python targets.

from os import system
import sys


# The target.
target = sys.argv[1]
path = '/data/python/'

# The list of build commands to run.
cmd = []

# Python.h.
include = '%s/include/python%s/' % (path, target)
if target == '3.2':
    include = '%s/include/python3.2m/' % path
elif target == '3.3':
    include = '%s/include/python3.3m/' % path

# numpy includes.
numpy_include = '%s/lib/python%s/site-packages/numpy/core/include/' % (path, target)

# Python 3.2 installed in the home directory.
cmd.append("gcc -o maths_fns/c_chi2.os -c -I%s -I%s -fPIC maths_fns/c_chi2.c" % (include, numpy_include))
cmd.append("gcc -o maths_fns/exponential.os -c -I%s -I%s -fPIC maths_fns/exponential.c" % (include, numpy_include))
cmd.append("gcc -o maths_fns/relax_fit.os -c -I%s -I%s -fPIC maths_fns/relax_fit.c" % (include, numpy_include))
cmd.append("gcc -o maths_fns/relax_fit.so -shared maths_fns/c_chi2.os maths_fns/exponential.os maths_fns/relax_fit.os")


# Execute the commands.
for i in range(len(cmd)):
    print(cmd[i])
    system(cmd[i])
