from __future__ import absolute_import
###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# Module docstring.
"""Module containing advanced IO functions for relax.

This includes IO redirection, automatic loading and writing of compressed files (both Gzip and BZ2 compression), reading and writing of files, processing of the contents of files, etc.
"""

# Python module imports.
import sys
try:
    import bz2
except ImportError:
    bz2 = None
    message = sys.exc_info()[1]
    bz2_module_message = message.args[0]
from os import devnull
from os import F_OK, X_OK, access, altsep, getenv, makedirs, pathsep, remove, sep
from os.path import expanduser, basename, splitext, isfile
from re import search, split
from sys import stdin, stdout, stderr
from warnings import warn

# relax module imports.
from lib.check_types import is_filetype
from lib.compat import bz2_open, gz_open
from lib.errors import RelaxError, RelaxFileError, RelaxFileOverwriteError, RelaxMissingBinaryError, RelaxNoInPathError, RelaxNonExecError
from lib.warnings import RelaxWarning



def delete(file_name, dir=None, fail=True):
    """Deleting the given file, taking into account missing compression extensions.

    @param file_name:       The name of the file to delete.
    @type file_name:        str
    @keyword dir:           The directory containing the file.
    @type dir:              None or str
    @keyword fail:          A flag which if True will cause RelaxFileError to be raised.
    @type fail:             bool
    @raises RelaxFileError: If the file does not exist, and fail is set to true.
    """

    # File path.
    file_path = get_file_path(file_name, dir)

    # Test if the file exists and determine the compression type.
    if access(file_path, F_OK):
        pass
    elif access(file_path + '.bz2', F_OK):
        file_path = file_path + '.bz2'
    elif access(file_path + '.gz', F_OK):
        file_path = file_path + '.gz'
    elif fail:
        raise RelaxFileError(file_path)
    else:
        return

    # Remove the file.
    remove(file_path)


def determine_compression(file_path):
    """Function for determining the compression type, and for also testing if the file exists.

    @param file_path:   The full file path of the file.
    @type file_path:    str
    @return:            A tuple of the compression type and full path of the file (including its extension).  A value of 0 corresponds to no compression.  Bzip2 compression corresponds to a value of 1.  Gzip compression corresponds to a value of 2.
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
        raise RelaxFileError(file_path)

    # Return the compression type.
    return compress_type, file_path


def extract_data(file=None, dir=None, file_data=None, sep=None):
    """Return all data in the file as a list of lines where each line is a list of line elements.

    @keyword file:          The file to extract the data from.
    @type file:             str or file object
    @keyword dir:           The path where the file is located.  If None and the file argument is a string, then the current directory is assumed.
    @type dir:              str or None
    @keyword file_data:     If the file data has already been extracted from the file, it can be passed into this function using this argument.  If data is supplied here, then the file_name and dir args are ignored.
    @type file_data:        list of str
    @keyword sep:           The character separating the columns in the file data.  If None, then whitespace is assumed.
    @type sep:              str
    @return:                The file data.
    @rtype:                 list of lists of str
    """

    # Data not already extracted from the file.
    if not file_data:
        # Open the file.
        if isinstance(file, str):
            file = open_read_file(file_name=file, dir=dir)

        # Read lines.
        file_data = file.readlines()

    # Create a data structure from the contents of the file split by either whitespace or the separator, sep.
    data = []
    for i in range(len(file_data)):
        if sep:
            row = file_data[i].split(sep)
        else:
            row = file_data[i].split()
        data.append(row)

    # Close the file.
    if not file_data:
        file.close()

    # Return the data.
    return data


def file_root(file_path):
    """Return the root file name, striped of path and extension details.

    @param file_path:   The full path to the file.
    @type file_path:    str
    @return:            The file root (with all directories and the extension stripped away).
    @rtype:             str
    """

    # Loop over all file extensions, stopping when none are left.
    ext = None
    while ext != '':
        file_path, ext = splitext(file_path)

    # Return the file root with the directories stripped.
    return basename(file_path)


def get_file_path(file_name=None, dir=None):
    """Generate and expand the full file path.

    @keyword file_name: The name of the file to extract the data from.
    @type file_name:    str
    @keyword dir:       The path where the file is located.  If None, then the current directory is assumed.
    @type dir:          str
    @return:            The full file path.
    @rtype:             str
    """

    # File name.
    file_path = file_name

    # Add the directory.
    if dir:
        file_path = dir + sep + file_path

    # Expand any ~ characters.
    if file_path:    # Catch a file path of None, as expanduser can't handle this.
        file_path = expanduser(file_path)

    # Return the file path.
    return file_path


def io_streams_restore(verbosity=1):
    """Restore all IO streams to the Python defaults.

    @keyword verbosity: The verbosity level.
    @type verbosity:    int
    """

    # Print out.
    if verbosity:
        print("Restoring the sys.stdin IO stream to the Python STDIN IO stream.")
        print("Restoring the sys.stdout IO stream to the Python STDOUT IO stream.")
        print("Restoring the sys.stderr IO stream to the Python STDERR IO stream.")

    # Restore streams.
    sys.stdin  = sys.__stdin__
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def io_streams_log(file_name=None, dir=None, verbosity=1):
    """Turn on logging, sending both STDOUT and STDERR streams to a file.

    @keyword file_name: The name of the file.
    @type file_name:    str
    @keyword dir:       The path where the file is located.  If None, then the current directory is assumed.
    @type dir:          str
    @keyword verbosity: The verbosity level.
    @type verbosity:    int
    """

    # Log file.
    log_file, file_path = open_write_file(file_name=file_name, dir=dir, force=True, verbosity=verbosity, return_path=True)

    # Logging IO streams.
    log_stdin  = stdin
    log_stdout = None
    log_stderr = SplitIO()

    # Print out.
    if verbosity:
        print("Redirecting the sys.stdin IO stream to the Python stdin IO stream.")
        print("Redirecting the sys.stdout IO stream to the log file '%s'." % file_path)
        print("Redirecting the sys.stderr IO stream to both the Python stderr IO stream and the log file '%s'." % file_path)

    # Set the logging IO streams.
    log_stdout = log_file
    log_stderr.split(stderr, log_file)

    # IO stream redirection.
    sys.stdin  = log_stdin
    sys.stdout = log_stdout
    sys.stderr = log_stderr


def io_streams_tee(file_name=None, dir=None, compress_type=0, verbosity=1):
    """Turn on teeing to split both STDOUT and STDERR streams and sending second part to a file.

    @keyword file_name:     The name of the file.
    @type file_name:        str
    @keyword dir:           The path where the file is located.  If None, then the current directory is assumed.
    @type dir:              str
    @keyword compress_type: The compression type.  The integer values correspond to the compression type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.
    @type compress_type:    int
    @keyword verbosity:     The verbosity level.
    @type verbosity:        int
    """

    # Tee file.
    tee_file, file_path = open_write_file(file_name=file_name, dir=dir, force=True, compress_type=compress_type, verbosity=verbosity, return_path=1)

    # Tee IO streams.
    tee_stdin  = stdin
    tee_stdout = SplitIO()
    tee_stderr = SplitIO()

    # Print out.
    if verbosity:
        print("Redirecting the sys.stdin IO stream to the Python stdin IO stream.")
        print("Redirecting the sys.stdout IO stream to both the Python stdout IO stream and the log file '%s'." % file_path)
        print("Redirecting the sys.stderr IO stream to both the Python stderr IO stream and the log file '%s'." % file_path)

    # Set the tee IO streams.
    tee_stdout.split(stdout, tee_file)
    tee_stderr.split(stderr, tee_file)

    # IO stream redirection.
    sys.stdin  = tee_stdin
    sys.stdout = tee_stdout
    sys.stderr = tee_stderr


def mkdir_nofail(dir=None, verbosity=1):
    """Create the given directory, or exit without raising an error if the directory exists.

    @keyword dir:       The directory to create.
    @type dir:          str
    @keyword verbosity: The verbosity level.
    @type verbosity:    int
    """

    # No directory given.
    if dir == None:
        return

    # Expand any ~ characters.
    dir = expanduser(dir)

    # Make the directory.
    try:
        makedirs(dir)
    except OSError:
        if verbosity:
            print("Directory ." + sep + dir + " already exists.\n")


def open_read_file(file_name=None, dir=None, verbosity=1):
    """Open the file 'file' and return all the data.

    @keyword file_name: The name of the file to extract the data from.
    @type file_name:    str
    @keyword dir:       The path where the file is located.  If None, then the current directory is assumed.
    @type dir:          str
    @keyword verbosity: The verbosity level.
    @type verbosity:    int
    @return:            The open file object.
    @rtype:             file object
    """

    # A file descriptor object.
    if is_filetype(file_name):
        # Nothing to do here!
        return file_name

    # Invalid file name.
    if not file_name and not isinstance(file_name, str):
        raise RelaxError("The file name " + repr(file_name) + " " + repr(type(file_name)) + " is invalid and cannot be opened.")

    # File path.
    file_path = get_file_path(file_name, dir)

    # Test if the file exists and determine the compression type.
    compress_type, file_path = determine_compression(file_path)

    # Open the file for reading.
    try:
        # Print out.
        if verbosity:
            print("Opening the file " + repr(file_path) + " for reading.")

        # Uncompressed text.
        if compress_type == 0:
            file_obj = open(file_path, 'r')

        # Bzip2 compressed text.
        elif compress_type == 1:
            file_obj = bz2_open(file=file_path, mode='r')

        # Gzipped compressed text.
        elif compress_type == 2:
            file_obj = gz_open(file=file_path, mode='r')

    # Cannot open.
    except IOError:
        message = sys.exc_info()[1]
        raise RelaxError("Cannot open the file " + repr(file_path) + ".  " + message.args[1] + ".")

    # Return the opened file.
    return file_obj


def open_write_file(file_name=None, dir=None, force=False, compress_type=0, verbosity=1, return_path=False):
    """Function for opening a file for writing and creating directories if necessary.

    @keyword file_name:     The name of the file to extract the data from.
    @type file_name:        str
    @keyword dir:           The path where the file is located.  If None, then the current directory is assumed.
    @type dir:              str
    @keyword force:         Boolean argument which if True causes the file to be overwritten if it already exists.
    @type force:            bool
    @keyword compress_type: The compression type.  The integer values correspond to the compression type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.  If no compression is given but the file name ends in '.gz' or '.bz2', then the compression will be automatically set.
    @type compress_type:    int
    @keyword verbosity:     The verbosity level.
    @type verbosity:        int
    @keyword return_path:   If True, the function will return a tuple of the file object and the full file path.
    @type return_path:      bool
    @return:                The open, writable file object and, if the return_path is True, then the full file path is returned as well.
    @rtype:                 writable file object (if return_path, then a tuple of the writable file and the full file path)
    """

    # No file name?
    if file_name == None:
        raise RelaxError("The name of the file must be supplied.")

    # A file descriptor object.
    if is_filetype(file_name):
        # Nothing to do here!
        return file_name

    # Something pretending to be a file object.
    if hasattr(file_name, 'write'):
        # Nothing to do here!
        return file_name

    # The null device.
    if search('devnull', file_name):
        # Print out.
        if verbosity:
            print("Opening the null device file for writing.")

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

    # If no compression is supplied, determine the compression to be used from the file extension.
    if compress_type == 0:
        if search('.bz2$', file_path):
            compress_type = 1
        elif search('.gz$', file_path):
            compress_type = 2

    # Bzip2 compression.
    if compress_type == 1 and not search('.bz2$', file_path):
        # Bz2 module exists.
        if bz2:
            file_path = file_path + '.bz2'

        # Switch to gzip compression.
        else:
            warn(RelaxWarning("Cannot use Bzip2 compression, using gzip compression instead.  " + bz2_module_message + "."))
            compress_type = 2

    # Gzip compression.
    if compress_type == 2 and not search('.gz$', file_path):
        file_path = file_path + '.gz'

    # Fail if the file already exists and the force flag is set to 0.
    if access(file_path, F_OK) and not force:
        raise RelaxFileOverwriteError(file_path, 'force flag')

    # Open the file for writing.
    try:
        # Print out.
        if verbosity:
            print("Opening the file " + repr(file_path) + " for writing.")

        # Uncompressed text.
        if compress_type == 0:
            file_obj = open(file_path, 'w')

        # Bzip2 compressed text.
        elif compress_type == 1:
            file_obj = bz2_open(file=file_path, mode='w')

        # Gzipped compressed text.
        elif compress_type == 2:
            file_obj = gz_open(file=file_path, mode='w')

    # Cannot open.
    except IOError:
        message = sys.exc_info()[1]
        raise RelaxError("Cannot open the file " + repr(file_path) + ".  " + message.args[1] + ".")

    # Return the opened file.
    if return_path:
        return file_obj, file_path
    else:
        return file_obj


def sort_filenames(filenames=None, rev=False):
    """Sort the given list in alphanumeric order.  Should be equivalent to unix 'ls -n' command.

    @keyword filenames: The list of file names to sort.
    @type filenames:    list of str
    @keyword rev:       Flag which if True will cause the list to be reversed.
    @type rev:          bool
    @return:            The sorted list of file names.
    @rtype:             list of str
    """

    # Define function to convert to integers if text is digit.
    convert = lambda text: int(text) if text.isdigit() else text

    # Define function to create key for sorting.
    alphanum_key = lambda key: [ convert(c) for c in split('([0-9]+)', key) ]

    # Now sort according to key.
    filenames.sort( key=alphanum_key )

    # Reverse the list if needed.
    if rev:
        return reversed(filenames)
    else:
        return filenames


def strip(data, comments=True):
    """Remove all comment and empty lines from the file data structure.

    @param data:        The file data to clean up.
    @type data:         list of lists of str
    @keyword comments:  A flag which if True will cause comments to be deleted.
    @type comments:     bool
    @return:            The input data with the empty and comment lines removed.
    @rtype:             list of lists of str
    """

    # Initialise the new data array.
    new = []

    # Loop over the data.
    for i in range(len(data)):
        # Empty lines.
        if len(data[i]) == 0:
            continue

        # Comment lines.
        if comments and search("^#", data[i][0]):
            continue

        # Data lines.
        new.append(data[i])

    # Return the new data structure.
    return new


def swap_extension(file=None, ext=None):
    """Swap one file name extension for another.

    @keyword file:  The name of the original file.
    @type file:     str
    @keyword ext:   The new file name extension to use.
    @type ext:      str
    @return:        The name of the file with the new file name extension.
    @rtype:         str
    """

    # The file root.
    new_file = file_root(file)

    # Add the new extension.
    new_file += '.'
    new_file += ext

    # Return the new file name.
    return new_file


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
    if isfile(binary):
        # Test that the binary exists.
        if not access(binary, F_OK):
            raise RelaxMissingBinaryError(binary)

        # Test that if the binary is executable.
        if not access(binary, X_OK):
            raise RelaxNonExecError(binary)

    # The path to the binary has not been given.
    else:
        # Get the PATH environmental variable.
        path = getenv('PATH')

        # Split PATH by the path separator.
        path_list = path.split(pathsep)

        # Test that the binary exists within the system path (and exit this function instantly once it has been found).
        for path in path_list:
            if access(path + sep + binary, F_OK) or access(path + sep + binary +".exe", F_OK):
                return

        # The binary is not located in the system path!
        raise RelaxNoInPathError(binary)


def write_data(out=None, headings=None, data=None, sep=None):
    """Write out a table of the data to the given file handle.

    @keyword out:       The file handle to write to.
    @type out:          file handle
    @keyword headings:  The optional headings to print out.
    @type headings:     list of str or None
    @keyword data:      The data to print out.
    @type data:         list of list of str
    @keyword sep:       The column separator which, if None, defaults to whitespace.
    @type sep:          str or None
    """

    # No data to print out.
    if data in [None, []]:
        return

    # The number of rows and columns.
    num_rows = len(data)
    num_cols = len(data[0])

    # Pretty whitespace formatting.
    if sep == None:
        # Determine the widths for the headings.
        widths = []
        for j in range(num_cols):
            if headings != None:
                if j == 0:
                    widths.append(len(headings[j]) + 2)
                else:
                    widths.append(len(headings[j]))

            # No headings.
            else:
                widths.append(0)

        # Determine the maximum column widths for nice whitespace formatting.
        for i in range(num_rows):
            for j in range(num_cols):
                size = len(data[i][j])
                if size > widths[j]:
                    widths[j] = size

        # Convert to format strings.
        formats = []
        for j in range(num_cols):
            formats.append("%%-%ss" % (widths[j] + 4))

        # The headings.
        if headings != None:
            out.write(formats[0] % ("# " + headings[0]))
            for j in range(1, num_cols):
                out.write(formats[j] % headings[j])
            out.write('\n')

        # The data.
        for i in range(num_rows):
            # The row.
            for j in range(num_cols):
                out.write(formats[j] % data[i][j])
            out.write('\n')

    # Non-whitespace formatting.
    else:
        # The headings.
        if headings != None:
            out.write('#')
            for j in range(num_cols):
                # The column separator.
                if j > 0:
                    out.write(sep)

                # The heading.
                out.write(headings[j])
            out.write('\n')

        # The data.
        for i in range(num_rows):
            # The row.
            for j in range(num_cols):
                # The column separator.
                if j > 0:
                    out.write(sep)

                # The heading.
                out.write(data[i][j])
            out.write('\n')



class DummyFileObject:
    def __init__(self):
        """Set up the dummy object to act as a file object."""

        # Initialise an object for adding the string from all write calls to.
        self.data = ''

        # Set the closed flag.
        self.closed = False


    def close(self):
        """A method for 'closing' this object."""

        # Set the closed flag.
        self.closed = True


    def write(self, str):
        """Mimic the file object write() method so that this class can be used as a file object.

        @param str:     The string to be written.
        @type str:      str
        """

        # Check if the file is closed.
        if self.closed:
            raise ValueError('I/O operation on closed file')

        # Append the string to the data object.
        self.data = self.data + str


    def readlines(self):
        """Mimic the file object readlines() method.

        This method works even if this dummy file object is closed!


        @return:    The contents of the file object separated by newline characters.
        @rtype:     list of str
        """

        # Split up the string.
        lines = self.data.split('\n')

        # Remove the last line if empty.
        if lines[-1] == '':
            lines.pop()

        # Loop over the lines, re-adding the newline character to match the file object readlines() method.
        for i in range(len(lines)):
            lines[i] = lines[i] + '\n'

        # Return the file lines.
        return lines



class SplitIO:
    def __init__(self):
        """Class for splitting an IO stream to two outputs."""


    def flush(self):
        """Flush all streams."""

        # Call the streams' methods.
        self.stream1.flush()
        self.stream2.flush()


    def isatty(self):
        """Check that both streams are TTYs.

        @return:    True, only if both streams are TTYs.
        @rtype:     bool
        """

        # Check both streams.
        return self.stream1.isatty() & self.stream2.isatty()


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
