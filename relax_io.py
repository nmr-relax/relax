###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module containing advanced IO functions for relax.

This includes IO redirection, automatic loading and writing of compressed files (both Gzip and BZ2
compression), reading and writing of files, processing of the contents of files, etc.
"""

# Dependency check module.
import dep_check

# Python module imports.
if dep_check.bz2_module:
    from bz2 import BZ2File
if dep_check.gzip_module:
    from gzip import GzipFile
if dep_check.devnull_import:
    from os import devnull
from os import F_OK, X_OK, access, altsep, getenv, makedirs, pathsep, remove, sep, stat
from os.path import expanduser, basename, splitext
from re import match, search
from string import split
import sys
from sys import stdin, stdout, stderr

# relax module imports.
from relax_errors import RelaxError, RelaxFileError, RelaxFileOverwriteError, RelaxMissingBinaryError, RelaxNoInPathError, RelaxNonExecError



def determine_compression(file_path):
    """Function for determining the compression type, and for also testing if the file exists.

    @param file_path:   The full file path of the file.
    @type file_path:    str
    @return:            A tuple of the compression type and full path of the file (including its
                        extension).  A value of 0 corresponds to no compression.  Bzip2 compression
                        corresponds to a value of 1.  Gzip compression corresponds to a value of 2.
    @rtype:             (int, str)
    """

    # The file has been supplied without its compression extension.
    if access(file_path, F_OK):
        compress_type = 0
        if search('.bz2$', file_path):
            compress_type = 1
        elif search('.gz$', file_path):
            compress_type = 2

    # The file has been supplied with the '.bz2' extension.
    elif access(file_path + '.bz2', F_OK):
        file_path = file_path + '.bz2'
        compress_type = 1

    # The file has been supplied with the '.gz' extension.
    elif access(file_path + '.gz', F_OK):
        file_path = file_path + '.gz'
        compress_type = 2

    # The file doesn't exist.
    else:
        raise RelaxFileError, file_path

    # Return the compression type.
    return compress_type, file_path


def extract_data(file_name=None, dir=None, file_data=None, sep=None):
    """Open the file 'file' and return all the data.

    @param file_name:       The name of the file to extract the data from.
    @type file_name:        str
    @param dir:             The path where the file is located.  If None, then the current
                            directory is assumed.
    @type dir:              str
    @param file_data:       If the file data has already been extracted from the file, it can be
                            passed into this function using this argument.  If data is supplied
                            here, then the file_name and dir args are ignored.
    @type file_data:        list of str
    @param sep:             The character separating the columns in the file data.  If None, then
                            whitespace is assumed.
    @type sep:              str
    @return:                The file data.
    @rtype:                 list of lists of str
    """

    # Data not already extracted from the file.
    if not file_data:
        # Open the file.
        file = open_read_file(file_name=file_name, dir=dir)

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


def file_root(file_path):
    """Return the root file name, striped of path and extension details.

    @param file_path:   The full path to the file.
    @type file_path:    str
    @return:            The file root (with all directories and the extension stripped away).
    @rtype:             str
    """

    root,ext = splitext(file_path)
    return basename(root)


def get_file_path(file_name=None, dir=None):
    """Generate and expand the full file path.

    @param file_name:   The name of the file to extract the data from.
    @type file_name:    str
    @param dir:         The path where the file is located.  If None, then the current directory is
                        assumed.
    @type dir:          str
    @return:            The full file path.
    @rtype:             str
    """

    # File name.
    file_path = file_name

    # Add the directory.
    if dir:
        file_path = dir + '/' + file_path

    # Expand any ~ characters.
    if file_path:    # Catch a file path of None, as expanduser can't handle this.
        file_path = expanduser(file_path)

    # Return the file path.
    return file_path


def log(file_name=None, dir=None, verbosity=1):
    """Function for turning logging on.

    @param file_name:   The name of the file to extract the data from.
    @type file_name:    str
    @param dir:         The path where the file is located.  If None, then the current directory is
                        assumed.
    @type dir:          str
    @param verbosity:   The verbosity level.
    @type verbosity:    int
    """

    # Log file.
    log_file, file_path = open_write_file(file_name=file_name, dir=dir, force=True, verbosity=verbosity, return_path=True)

    # Print out.
    if verbosity:
        print "Redirecting the sys.stdin IO stream to the python stdin IO stream."
        print "Redirecting the sys.stdout IO stream to the log file '%s'." % file_path
        print "Redirecting the sys.stderr IO stream to both the python stderr IO stream and the log file '%s'." % file_path

    # Set the logging IO streams.
    log_stdout = log_file
    log_stderr.split(python_stderr, log_file)

    # IO stream redirection.
    sys.stdin  = log_stdin
    sys.stdout = log_stdout
    sys.stderr = log_stderr


def mkdir_nofail(dir=None, verbosity=1):
    """Create the given directory, or exit without raising an error if the directory exists.

    @param dir:         The directory to create.
    @type dir:          str
    @param verbosity:   The verbosity level.
    @type verbosity:    int
    """

    # No directory given.
    if dir == None:
        return

    # Make the directory.
    try:
        makedirs(dir)
    except OSError:
        if verbosity:
            print "Directory ./" + dir + " already exists.\n"


def open_read_file(file_name=None, dir=None, verbosity=1):
    """Open the file 'file' and return all the data.

    @param file_name:   The name of the file to extract the data from.
    @type file_name:    str
    @param dir:         The path where the file is located.  If None, then the current directory is
                        assumed.
    @type dir:          str
    @param verbosity:   The verbosity level.
    @type verbosity:    int
    @return:            The open file object.
    @rtype:             file object
    """

    # A file descriptor object.
    if type(file_name) == file:
        # Nothing to do here!
        return file_name

    # File path.
    file_path = get_file_path(file_name, dir)

    # Test if the file exists and determine the compression type.
    compress_type, file_path = determine_compression(file_path)

    # Open the file for reading.
    try:
        if verbosity:
            print "Opening the file " + `file_path` + " for reading."
        if compress_type == 0:
            file_obj = open(file_path, 'r')
        elif compress_type == 1:
            if dep_check.bz2_module:
                file_obj = BZ2File(file_path, 'r')
            else:
                raise RelaxError, "Cannot open the file " + `file_path` + ", try uncompressing first.  " + dep_check.bz2_module_message + "."
        elif compress_type == 2:
            file_obj = GzipFile(file_path, 'r')
    except IOError, message:
        raise RelaxError, "Cannot open the file " + `file_path` + ".  " + message.args[1] + "."

    # Return the opened file.
    return file_obj


def open_write_file(file_name=None, dir=None, force=False, compress_type=0, verbosity=1, return_path=False):
    """Function for opening a file for writing and creating directories if necessary.

    @param file_name:       The name of the file to extract the data from.
    @type file_name:        str
    @param dir:             The path where the file is located.  If None, then the current directory
                            is assumed.
    @type dir:              str
    @param force:           Boolean argument which if True causes the file to be overwritten if it
                            already exists.
    @type force:            bool
    @param compress_type:   The compression type.  The integer values correspond to the compression
                            type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.
    @type compress_type:    int
    @param verbosity:       The verbosity level.
    @type verbosity:        int
    @param return_path:     If True, the function will return a tuple of the file object and the
                            full file path.
    @type return_path:      bool
    @return:                The open, writable file object and, if the return_path is True, then the
                            full file path is returned as well.
    @rtype:                 writable file object (if return_path, then a tuple of the writable file
                            and the full file path)
    """

    # A file descriptor object.
    if type(file_name) == file:
        # Nothing to do here!
        return file_name

    # The null device.
    if search('devnull', file_name):
        # Devnull could not be imported!
        if not dep_check.devnull_import:
            raise RelaxError, dep_check.devnull_import_message + ".  To use devnull, please upgrade to Python >= 2.4."

        # Print out.
        if verbosity:
            print "Opening the null device file for writing."

        # Open the null device.
        file_obj = open(devnull, 'w')

        # Return the file.
        if return_path:
            return file_obj, None
        else:
            return file_obj

    # Create the directories.
    mkdir_nofail(dir, verbosity=0)

    # File path.
    file_path = get_file_path(file_name, dir)

    # Bzip2 compression.
    if compress_type == 1 and not search('.bz2$', file_path):
        # Bz2 module exists.
        if dep_check.bz2_module:
            file_path = file_path + '.bz2'

        # Switch to gzip compression.
        else:
            warn(RelaxWarning("Cannot use Bzip2 compression, using gzip compression instead.  " + dep_check.bz2_module_message + "."))
            compress_type = 2

    # Gzip compression.
    if compress_type == 2 and not search('.gz$', file_path):
        file_path = file_path + '.gz'

    # Fail if the file already exists and the force flag is set to 0.
    if access(file_path, F_OK) and not force:
        raise RelaxFileOverwriteError, (file_path, 'force flag')

    # Open the file for writing.
    try:
        if verbosity:
            print "Opening the file " + `file_path` + " for writing."
        if compress_type == 0:
            file_obj = open(file_path, 'w')
        elif compress_type == 1:
            file_obj = BZ2File(file_path, 'w')
        elif compress_type == 2:
            file_obj = GzipFile(file_path, 'w')
    except IOError, message:
        raise RelaxError, "Cannot open the file " + `file_path` + ".  " + message.args[1] + "."

    # Return the opened file.
    if return_path:
        return file_obj, file_path
    else:
        return file_obj


def strip(data):
    """Function to remove all comment and empty lines from the file data structure.

    @param data:    The file data.
    @type data:     list of lists of str
    @return:        The file data with comment and empty lines removed.
    @rtype:         list of lists of str
    """

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


def test_binary(binary):
    """Function for testing that the binary string corresponds to a valid executable file.

    @param binary:  The name or path of the binary executable file.
    @type binary:   str
    """

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
        file_path = get_file_path(file_name, dir)

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


    def logging_off(self, file_name=None, dir=None, verbosity=1):
        """Function for turning logging and teeing off."""

        # Print out.
        if verbosity:
            print "Redirecting the sys.stdin IO stream to the python stdin IO stream."
            print "Redirecting the sys.stdout IO stream to the python stdout IO stream."
            print "Redirecting the sys.stderr IO stream to the python stderr IO stream."

        # IO stream redirection.
        sys.stdin  = self.python_stdin
        sys.stdout = self.python_stdout
        sys.stderr = self.python_stderr


    def tee(self, file_name=None, dir=None, compress_type=0, verbosity=1):
        """Function for turning logging on."""

        # Tee file.
        self.tee_file, file_path = self.open_write_file(file_name=file_name, dir=dir, force=1, compress_type=compress_type, verbosity=verbosity, return_path=1)

        # Print out.
        if verbosity:
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
