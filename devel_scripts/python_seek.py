#! /usr/bin/env python

# Script for finding all Python binaries on the system and to print out various package versions.
# This requires access to a shell and the locate, grep, and other programs.


# Python module imports.
from os import X_OK, access, system
from os.path import isfile, islink
from subprocess import PIPE, Popen
import sys


class Python_info:
    """Find all Python versions and the supported modules."""

    def __init__(self, format="    %-10s %-20s", debug=False):
        """Set up and run."""

        # Store the args.
        self.format = format
        self.debug = debug

        # Get a list of all Python binaries.
        files = self.get_files()

        # Loop over the binaries.
        for file in files:
            # Printout.
            print("Testing %s:" % file)

            # Determine and print out the version info.
            self.version_python(file)
            self.version_minfx(file)
            self.version_bmrblib(file)
            self.version_numpy(file)
            self.version_scipy(file)
            self.version_wx(file)
            self.version_mpi4py(file)
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

            # Check if the path is a file.
            if not isfile(file):
                continue

            # Check for if the file is executable.
            if not access(file, X_OK):
                continue

            # Check if the path is a link.
            if islink(file):
                continue

            # Add the file.
            binaries.append(file)

        # Return the file list.
        return binaries


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
