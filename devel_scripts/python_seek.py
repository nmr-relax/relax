#! /usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
    'epydoc'
]


class Python_info:
    """Find all Python versions and the supported modules."""

    def __init__(self, format="    %-15s %-20s", debug=False):
        """Set up and run."""

        # Store the args.
        self.format = format
        self.debug = debug

        # Get a list of all Python binaries.
        files = self.get_files()

        # The modules to find.
        self.modules()

        # Loop over the binaries.
        for file in files:
            # Printout.
            print("Testing %s:" % file)

            # Determine and print out the version info.
            if 'python' in self.module_list:
                self.version_python(file)
            if 'minfx' in self.module_list:
                self.version_minfx(file)
            if 'bmrblib' in self.module_list:
                self.version_bmrblib(file)
            if 'Numeric' in self.module_list:
                self.version_numeric(file)
            if 'Scientific' in self.module_list:
                self.version_scientific(file)
            if 'numpy' in self.module_list:
                self.version_numpy(file)
            if 'scipy' in self.module_list:
                self.version_scipy(file)
            if 'matplotlib' in self.module_list:
                self.version_matplotlib(file)
            if 'wx' in self.module_list:
                self.version_wx(file)
            if 'mpi4py' in self.module_list:
                self.version_mpi4py(file)
            if 'epydoc' in self.module_list:
                self.version_epydoc(file)


    def execute(self, label=None, file=None, commands=None):
        """Execute Python in a pipe."""

        # Execute the Python binary.
        python = Popen(file, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

        # Execute.
        for command in commands:
            python.stdin.write(command)

        # Close the pipe.
        python.stdin.close()

        # Write to stdout.
        line = None
        for line in python.stdout.readlines():
            # Decode Python 3 byte arrays.
            if hasattr(line, 'decode'):
                line = line.decode()

        # Store the last line as the version
        if line:
            version = line[:-1]
        else:
            version = None

        # Write to stderr.
        if self.debug:
            for line in python.stderr.readlines():
                # Decode Python 3 byte arrays.
                if hasattr(line, 'decode'):
                    line = line.decode()

                # Write.
                sys.stderr.write(line)

        # Write the version info.
        print(self.format % (label, version))


    def get_files(self):
        """Find all Python binaries."""

        # Run the locate command and filter the results.
        cmd = "locate python | grep '\/python$\|\/python...$' | grep bin"
        pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)

        # Close the pipe.
        pipe.stdin.close()

        # Store the Python binaries.
        binaries = []
        for line in pipe.stdout.readlines():
            # The file name.
            file = line[:-1]

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


    def version_bmrblib(self, file=None):
        """Determine and print out the bmrblib module version info."""

        # The commands.
        commands = [
            "try:\n",
            "    import bmrblib\n",
            "    if hasattr(bmrblib, '__version__'):\n",
            "        version = bmrblib.__version__\n",
            "    else:\n",
            "        version = 'Unknown'\n",
            "except:\n",
            "    version = '-'\n",
            "print(version)\n",
        ]

        # Execute and print the version
        self.execute(label="bmrblib:", file=file, commands=commands)


    def version_epydoc(self, file=None):
        """Determine and print out the epydoc module version info."""

        # The commands.
        commands = [
            "try:\n",
            "    import epydoc\n",
            "    version = epydoc.__version__\n",
            "except:\n",
            "    version = '-'\n",
            "print(version)\n",
        ]

        # Execute and print the version
        self.execute(label="epydoc:", file=file, commands=commands)


    def version_matplotlib(self, file=None):
        """Determine and print out the matplotlib module version info."""

        # The commands.
        commands = [
            "try:\n",
            "    import matplotlib\n",
            "    version = matplotlib.__version__\n",
            "except:\n",
            "    version = '-'\n",
            "print(version)\n",
        ]

        # Execute and print the version
        self.execute(label="matplotlib:", file=file, commands=commands)


    def version_minfx(self, file=None):
        """Determine and print out the minfx module version info."""

        # The commands.
        commands = [
            "try:\n",
            "    import minfx\n",
            "    if hasattr(minfx, '__version__'):\n",
            "        version = minfx.__version__\n",
            "    else:\n",
            "        version = 'Unknown'\n",
            "except:\n",
            "    version = '-'\n",
            "print(version)\n",
        ]

        # Execute and print the version
        self.execute(label="minfx:", file=file, commands=commands)


    def version_mpi4py(self, file=None):
        """Determine and print out the mpi4py module version info."""

        # The commands.
        commands = [
            "try:\n",
            "    import mpi4py\n",
            "    version = mpi4py.__version__\n",
            "except:\n",
            "    version = '-'\n",
            "print(version)\n",
        ]

        # Execute and print the version
        self.execute(label="mpi4py:", file=file, commands=commands)


    def version_numeric(self, file=None):
        """Determine and print out the Numeric module version info."""

        # The commands.
        commands = [
            "try:\n",
            "    import Numeric\n",
            "    version = Numeric.__version__\n",
            "except:\n",
            "    version = '-'\n",
            "print(version)\n",
        ]

        # Execute and print the version
        self.execute(label="Numeric:", file=file, commands=commands)


    def version_numpy(self, file=None):
        """Determine and print out the numpy module version info."""

        # The commands.
        commands = [
            "try:\n",
            "    import numpy\n",
            "    version = numpy.version.version\n",
            "except:\n",
            "    version = '-'\n",
            "print(version)\n",
        ]

        # Execute and print the version
        self.execute(label="numpy:", file=file, commands=commands)


    def version_scientific(self, file=None):
        """Determine and print out the Scientific module version info."""

        # The commands.
        commands = [
            "try:\n",
            "    import Scientific\n",
            "    version = Scientific.__version__\n",
            "except:\n",
            "    version = '-'\n",
            "print(version)\n",
        ]

        # Execute and print the version
        self.execute(label="Scientific:", file=file, commands=commands)


    def version_scipy(self, file=None):
        """Determine and print out the scipy module version info."""

        # The commands.
        commands = [
            "try:\n",
            "    import scipy\n",
            "    version = scipy.version.version\n",
            "except:\n",
            "    version = '-'\n",
            "print(version)\n",
        ]

        # Execute and print the version
        self.execute(label="scipy:", file=file, commands=commands)


    def version_wx(self, file=None):
        """Determine and print out the wx module version info."""

        # The commands.
        commands = [
            "try:\n",
            "    import wx\n",
            "    version = wx.version()\n",
            "except:\n",
            "    version = '-'\n",
            "print(version)\n",
        ]

        # Execute and print the version
        self.execute(label="wx:", file=file, commands=commands)


    def version_python(self, file=None):
        """Determine and print out the Python and module version info."""

        # The commands.
        commands = [
            "python_version = 'None'\n",
            "try:\n",
            "    import platform\n",
            "    python_version = platform.python_version()\n",
            "except:\n",
            "    import sys\n",
            "    if hasattr(sys, 'version_info'):\n",
            "        python_version = '%s.%s.%s' % (sys.version_info[0], sys.version_info[1], sys.version_info[2])\n",
            "    elif hasattr(sys, 'version'):\n",
            "        if sys.version[3] == ' ':\n",
            "            python_version = sys.version[:3]\n",
            "        elif sys.version[5] == ' ':\n",
            "            python_version = sys.version[:5]\n",
            "        else:\n",
            "            python_version = sys.version\n",
            "\n",
            "print(python_version)\n",
        ]

        # Execute and print the version
        self.execute(label="Python:", file=file, commands=commands)



# Execute.
Python_info(debug=False)
