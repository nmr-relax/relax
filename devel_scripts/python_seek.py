#! /usr/bin/env python3

###############################################################################
#                                                                             #
# Copyright (C) 2013-2014,2019 Edward d'Auvergne                              #
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

"""Script for finding all Python binaries on the system and to print out various package versions.

This requires access to a shell and the locate, grep, and other programs.
"""


# Python module imports.
from os import X_OK, access, readlink
from os.path import abspath, dirname, isabs, isfile, islink, join
from subprocess import PIPE, Popen
import sys

# The default module list.
MOD_LIST = [
    'python',
    'minfx',
    'bmrblib',
    'numpy',
    'scipy',
    'wx',
    'mpi4py',
    'epydoc'
]

MOD_ALL_LIST = [
    'python',
    'minfx',
    'bmrblib',
    'Numeric',
    'Scientific',
    'numpy',
    'scipy',
    'matplotlib',
    'wx',
    'mpi4py',
    'epydoc',
]


class Python_info:
    """Find all Python versions and the supported modules."""

    def __init__(self, debug=True):
        """Set up and run."""

        # The modules to find.
        self.modules()

        # Loop over the binaries.
        for py_exec in self.get_py_exec_list():
            # Printout.
            print("Testing %s:" % py_exec)

            # Test the Python binary.
            python = Popen(py_exec, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)
            python.stdin.close()
            err_lines = python.stderr.readlines()
            for line in err_lines:
                print(line.decode().strip())
            if err_lines:
                continue

            # Determine the Python exception catching syntax.
            python = Popen(py_exec, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)
            cmd = "try:\n    import no_such_python_module\nexcept ImportError, err:\n    pass"
            python.stdin.write(cmd.encode())
            python.stdin.close()
            err_lines = python.stderr.readlines()
            except_text = "except ImportError, err"
            for line in err_lines:
                if "SyntaxError: invalid syntax" in line.decode():
                    except_text = "except ImportError as err"

            # Loop over each module to check.
            for module in self.module_list:
                # The python code to execute.
                commands = """
from re import search
import sys
import traceback

version = '-'
try:
    import %s
    if hasattr(%s, 'version'):
        if hasattr(%s.version, '__call__'): # wxPython
            version = %s.version()
        if hasattr(%s.version, 'version'):  # numpy, scipy
            version = %s.version.version
    if hasattr(%s, '__version__'):          # minfx, bmrblib, epydoc, matplotlib, mpi4py, Numeric, Scientific
        version = %s.__version__
    else:
        version = 'unknown'
%s:
    text = repr(err)
    if hasattr(err, '__str__'):
        text = err.__str__()
    print(text)
    if search('No module named', text):
        version = '-'
    else:
        version = text

print(version)
""" % (module, module, module, module, module, module, module, module, except_text)

                # Special case - The Python version.
                if module == 'python':
                    commands = """
python_version = 'None'
try:
    import platform
    python_version = platform.python_version()
except:
    import sys
    if hasattr(sys, 'version_info'):
        python_version = '%s.%s.%s' % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
    elif hasattr(sys, 'version'):
        if sys.version[3] == ' ':
            python_version = sys.version[:3]
        elif sys.version[5] == ' ':
            python_version = sys.version[:5]
        else:
            python_version = sys.version

print(python_version)
"""

                # Execute the Python binary.
                python = Popen(py_exec, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)
                python.stdin.write(commands.encode())
                #print(commands)

                # Close the pipe.
                python.stdin.close()

                # Extract the contents of STDOUT.
                line = None
                for line in python.stdout.readlines():
                    line = line.decode()
                    #rint(repr(line))

                # Store the last line as the version
                if line:
                    version = line[:-1]
                else:
                    version = '?'

                # Extract the contents of STDERR.
                if debug:
                    for line in python.stderr.readlines():
                        line = line.decode()

                        # Write.
                        sys.stderr.write(line)

                # Write the version info.
                print("    %-15s %-20s" % (module+':', version))


    def get_py_exec_list(self):
        """Find all Python executables.

        @return:    The list of all executable Python binaries on the system.
        @rtype:     list of str
        """

        # Run the locate command and filter the results.
        cmd = "locate python | grep '\/python$\|\/python...$' | grep bin"
        pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

        # Close the pipe.
        pipe.stdin.close()

        # Store the Python binaries.
        binaries = []
        for line in pipe.stdout.readlines():
            # The file name.
            file = line[:-1].decode()

            # Recursively follow and expand links.
            while True:
                if islink(file):
                    orig = readlink(file)
                    if not isabs(orig):
                        orig = join(dirname(file), orig)
                    file = orig
                    continue
                else:
                    break

            # Check if the path is a file.
            if not isfile(file):
                continue

            # Check for if the file is executable.
            if not access(file, X_OK):
                continue

            # Convert to an absolute path.
            file = abspath(file)

            # Add the file, avoiding duplicates.
            if file not in binaries:
                binaries.append(file)

        # Sort the list.
        binaries.sort()

        # Return the file list.
        return binaries


    def modules(self):
        """Determine the modules to find."""

        # Arguments supplied, so use these.
        if len(sys.argv) > 1:
            # The special 'all' argument.
            if sys.argv[1] == 'all':
                self.module_list = MOD_ALL_LIST

            # Individual modules.
            else:
                # Initialise the list.
                self.module_list = []

                # Loop over the arguments.
                for i in range(1, len(sys.argv)):
                    self.module_list.append(sys.argv[i])

        # Use the defaults.
        else:
            self.module_list = MOD_LIST


# Execute.
Python_info(debug=False)
