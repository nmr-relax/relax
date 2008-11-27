###############################################################################
#                                                                             #
# Copyright (C) 2003-2006 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

import __builtin__

# BZ2 compression module.
try:
    from bz2 import BZ2File
    __builtin__.bz2_module = 1
except ImportError, message:
    __builtin__.bz2_module = 0
    __builtin__.bz2_module_message = message.args[0]

# Gzip compression module.
from gzip import GzipFile

# Devnull.
try:
    from os import devnull
    __builtin__.devnull_import = 1
except ImportError, message:
    __builtin__.devnull_import = 0
    __builtin__.devnull_import_message = message.args[0]

from os import F_OK, X_OK, access, altsep, getenv, makedirs, pathsep, remove, sep, stat
from os.path import expanduser
from re import match, search
from string import split
import sys
from sys import stdin, stdout, stderr


class IO:
    def __init__(self, relax):
        """Class containing the file operations.

        IO streams
        ~~~~~~~~~~

        Standard python IO streams:

        sys.stdin  = self.python_stdin
        sys.stdout = self.python_stdout
        sys.stderr = self.python_stderr

        Logging IO streams:

        sys.stdin  = self.log_stdin  = self.python_stdin
        sys.stdout = self.log_stdout = self.log_file
        sys.stderr = self.log_stdout = (self.python_stderr, self.log_file)

        Tee IO streams:

        sys.stdin  = self.tee_stdin  = self.python_stdin
        sys.stdout = self.tee_stdout = (self.python_stdout, self.tee_file)
        sys.stderr = self.tee_stdout = (self.python_stderr, self.tee_file)
        """

        self.relax = relax

        # Standard python IO streams.
        self.python_stdin  = stdin
        self.python_stdout = stdout
        self.python_stderr = stderr

        # Logging IO streams.
        self.log_stdin  = stdin
        self.log_stdout = None
        self.log_stderr = SplitIO()

        # Tee IO streams.
        self.tee_stdin  = stdin
        self.tee_stdout = SplitIO()
        self.tee_stderr = SplitIO()


    def delete(self, file_name=None, dir=None):
        """Function for deleting the given file."""

        # File path.
        file_path = self.file_path(file_name, dir)

        # Test if the file exists and determine the compression type.
        if access(file_path, F_OK):
            pass
        elif access(file_path + '.bz2', F_OK):
            file_path = file_path + '.bz2'
        elif access(file_path + '.gz', F_OK):
            file_path = file_path + '.gz'
        else:
            raise RelaxFileError, file_path

        # Remove the file.
        remove(file_path)


    def extract_data(self, file_name=None, dir=None, file_data=None, sep=None, compress_type=0):
        """Open the file 'file' and return all the data."""

        # Data not already extracted from the file.
        if not file_data:
            # Open the file.
            file = self.open_read_file(file_name=file_name, dir=dir, compress_type=compress_type)

            # Read lines.
            file_data = file.readlines()

        # Create a data structure from the contents of the file split by either whitespace or the separator, sep.
        data = []
        for i in xrange(len(file_data)):
            if sep:
                row = split(file_data[i], sep)
            else:
                row = split(file_data[i])
            data.append(row)
        return data

        # Close the file.
        if not file_data:
            file.close()


    def file_path(self, file_name=None, dir=None):
        """Generate and expand the full file path."""

        # File name.
        file_path = file_name

        # Add the directory.
        if dir:
            file_path = dir + '/' + file_path

        # Expand any ~ characters.
        file_path = expanduser(file_path)

        # Return the file path.
        return file_path


    def log(self, file_name=None, dir=None, compress_type=0, print_flag=1):
        """Function for turning logging on."""

        # Log file.
        self.log_file, file_path = self.open_write_file(file_name=file_name, dir=dir, force=1, compress_type=compress_type, print_flag=print_flag, return_path=1)

        # Print out.
        if print_flag:
            print "Redirecting the sys.stdin IO stream to the python stdin IO stream."
            print "Redirecting the sys.stdout IO stream to the log file '%s'." % file_path
            print "Redirecting the sys.stderr IO stream to both the python stderr IO stream and the log file '%s'." % file_path

        # Set the logging IO streams.
        self.log_stdout = self.log_file
        self.log_stderr.split(self.python_stderr, self.log_file)

        # IO stream redirection.
        sys.stdin  = self.log_stdin
        sys.stdout = self.log_stdout
        sys.stderr = self.log_stderr


    def logging_off(self, file_name=None, dir=None, print_flag=1):
        """Function for turning logging and teeing off."""

        # Print out.
        if print_flag:
            print "Redirecting the sys.stdin IO stream to the python stdin IO stream."
            print "Redirecting the sys.stdout IO stream to the python stdout IO stream."
            print "Redirecting the sys.stderr IO stream to the python stderr IO stream."

        # IO stream redirection.
        sys.stdin  = self.python_stdin
        sys.stdout = self.python_stdout
        sys.stderr = self.python_stderr


    def mkdir(self, dir=None, print_flag=1):
        """Create the given directory, or exit if the directory exists."""

        # No directory given.
        if dir == None:
            return

        # Make the directory.
        try:
            makedirs(dir)
        except OSError:
            if print_flag:
                print "Directory ./" + dir + " already exists.\n"


    def open_read_file(self, file_name=None, dir=None, compress_type=0, print_flag=1):
        """Open the file 'file' and return all the data."""

        # File path.
        file_path = self.file_path(file_name, dir)

        # Test if the file exists and determine the compression type.
        if access(file_path, F_OK):
            compress_type = 0
            if search('.bz2$', file_path):
                compress_type = 1
            elif search('.gz$', file_path):
                compress_type = 2
        elif access(file_path + '.bz2', F_OK):
            file_path = file_path + '.bz2'
            compress_type = 1
        elif access(file_path + '.gz', F_OK):
            file_path = file_path + '.gz'
            compress_type = 2
        else:
            raise RelaxFileError, file_path

        # Open the file for reading.
        try:
            if print_flag:
                print "Opening the file " + `file_path` + " for reading."
            if compress_type == 0:
                file = open(file_path, 'r')
            elif compress_type == 1:
                if bz2_module:
                    file = BZ2File(file_path, 'r')
                else:
                    raise RelaxError, "Cannot open the file " + `file_path` + ", try uncompressing first.  " + bz2_module_message + "."
            elif compress_type == 2:
                file = GzipFile(file_path, 'r')
        except IOError, message:
            raise RelaxError, "Cannot open the file " + `file_path` + ".  " + message.args[1] + "."

        # Return the opened file.
        return file


    def open_write_file(self, file_name=None, dir=None, force=0, compress_type=0, print_flag=1, return_path=0):
        """Function for opening a file for writing and creating directories if necessary."""

        # The null device.
        if search('devnull', file_name):
            # Devnull could not be imported!
            if not devnull_import:
                raise RelaxError, devnull_import_message + ".  To use devnull, please upgrade to Python >= 2.4."

            # Print out.
            if print_flag:
                print "Opening the null device file for writing."

            # Open the null device.
            file = open(devnull, 'w')

            # Return the file.
            if return_path:
                return file, None
            else:
                return file

        # Create the directories.
        self.mkdir(dir, print_flag=0)

        # File path.
        file_path = self.file_path(file_name, dir)

        # Bzip2 compression.
        if compress_type == 1 and not search('.bz2$', file_path):
            # Bz2 module exists.
            if bz2_module:
                file_path = file_path + '.bz2'

            # Switch to gzip compression.
            else:
                print "Cannot use bz2 compression, using gzip compression instead.  " + bz2_module_message + "."
                compress_type = 2

        # Gzip compression.
        if compress_type == 2 and not search('.gz$', file_path):
            file_path = file_path + '.gz'

        # Fail if the file already exists and the force flag is set to 0.
        if access(file_path, F_OK) and not force:
            raise RelaxFileOverwriteError, (file_path, 'force flag')

        # Open the file for writing.
        try:
            if print_flag:
                print "Opening the file " + `file_path` + " for writing."
            if compress_type == 0:
                file = open(file_path, 'w')
            elif compress_type == 1:
                file = BZ2File(file_path, 'w')
            elif compress_type == 2:
                file = GzipFile(file_path, 'w')
        except IOError, message:
            raise RelaxError, "Cannot open the file " + `file_path` + ".  " + message.args[1] + "."

        # Return the opened file.
        if return_path:
            return file, file_path
        else:
            return file


    def strip(self, data):
        """Function to remove all comment and empty lines from the file data structure."""

        # Initialise the new data array.
        new = []

        # Loop over the data.
        for i in xrange(len(data)):
            # Empty lines.
            if len(data[i]) == 0:
                continue

            # Comment lines.
            elif match("#", data[i][0]):
                continue

            # Data lines.
            else:
                new.append(data[i])

        # Return the new data structure.
        return new


    def tee(self, file_name=None, dir=None, compress_type=0, print_flag=1):
        """Function for turning logging on."""

        # Tee file.
        self.tee_file, file_path = self.open_write_file(file_name=file_name, dir=dir, force=1, compress_type=compress_type, print_flag=print_flag, return_path=1)

        # Print out.
        if print_flag:
            print "Redirecting the sys.stdin IO stream to the python stdin IO stream."
            print "Redirecting the sys.stdout IO stream to both the python stdout IO stream and the log file '%s'." % file_path
            print "Redirecting the sys.stderr IO stream to both the python stderr IO stream and the log file '%s'." % file_path

        # Set the tee IO streams.
        self.tee_stdout.split(self.python_stdout, self.tee_file)
        self.tee_stderr.split(self.python_stderr, self.tee_file)

        # IO stream redirection.
        sys.stdin  = self.tee_stdin
        sys.stdout = self.tee_stdout
        sys.stderr = self.tee_stderr


    def test_binary(self, binary):
        """Function for testing that the binary string corresponds to a valid executable file."""

        # Path separator RE string.
        if altsep:
            path_sep = '[' + sep + altsep + ']'
        else:
            path_sep = sep

        # The full path of the program has been given (if a directory separatory has been supplied).
        if search(path_sep, binary):
            # Test that the binary exists.
            if not access(binary, F_OK):
                raise RelaxMissingBinaryError, binary

            # Test that if the binary is executable.
            if not access(binary, X_OK):
                raise RelaxNonExecError, binary

        # The path to the binary has not been given.
        else:
            # Get the PATH environmental variable.
            path = getenv('PATH')

            # Split PATH by the path separator.
            path_list = split(path, pathsep)

            # Test that the binary exists within the system path (and exit this function instantly once it has been found).
            for path in path_list:
                if access(path + sep + binary, F_OK):
                    return

            # The binary is not located in the system path!
            raise RelaxNoInPathError, binary


class SplitIO:
    def __init__(self):
        """Class for splitting an IO stream to two outputs."""


    def split(self, stream1, stream2):
        """Function for setting the streams."""

        # Arguments.
        self.stream1 = stream1
        self.stream2 = stream2


    def write(self, text):
        """Replacement write function."""

        # Write to stream1.
        self.stream1.write(text)

        # Write to stream2.
        self.stream2.write(text)
