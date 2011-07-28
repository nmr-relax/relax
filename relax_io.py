###############################################################################
#                                                                             #
# Copyright (C) 2003-2011 Edward d'Auvergne                                   #
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
from os import F_OK, X_OK, access, altsep, getenv, makedirs, pathsep, remove, sep
from os.path import expanduser, basename, splitext
from re import match, search
from string import split
import sys
from sys import stdin, stdout, stderr
from warnings import warn

# relax module imports.
import generic_fns
from generic_fns.mol_res_spin import generate_spin_id_data_array
from relax_errors import RelaxError, RelaxFileError, RelaxFileOverwriteError, RelaxInvalidSeqError, RelaxMissingBinaryError, RelaxNoInPathError, RelaxNonExecError
from relax_warnings import RelaxWarning, RelaxFileEmptyWarning



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
        raise RelaxFileError(file_path)

    # Return the compression type.
    return compress_type, file_path


def extract_data(file=None, dir=None, file_data=None, sep=None):
    """Return all data in the file as a list of lines where each line is a list of line elements.

    @param file:            The file to extract the data from.
    @type file:             str or file object
    @param dir:             The path where the file is located.  If None and the file argument is a
                            string, then the current directory is assumed.
    @type dir:              str or None
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
        if isinstance(file, str):
            file = open_read_file(file_name=file, dir=dir)

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

    root, ext = splitext(file_path)
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
        file_path = dir + sep + file_path

    # Expand any ~ characters.
    if file_path:    # Catch a file path of None, as expanduser can't handle this.
        file_path = expanduser(file_path)

    # Return the file path.
    return file_path


def io_streams_restore(verbosity=1):
    """Restore all IO streams to the Python defaults.

    @param verbosity:   The verbosity level.
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

    @param file_name:   The name of the file.
    @type file_name:    str
    @param dir:         The path where the file is located.  If None, then the current directory is
                        assumed.
    @type dir:          str
    @param verbosity:   The verbosity level.
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
        print("Redirecting the sys.stdin IO stream to the python stdin IO stream.")
        print(("Redirecting the sys.stdout IO stream to the log file '%s'." % file_path))
        print(("Redirecting the sys.stderr IO stream to both the python stderr IO stream and the log file '%s'." % file_path))

    # Set the logging IO streams.
    log_stdout = log_file
    log_stderr.split(stderr, log_file)

    # IO stream redirection.
    sys.stdin  = log_stdin
    sys.stdout = log_stdout
    sys.stderr = log_stderr


def io_streams_tee(file_name=None, dir=None, compress_type=0, verbosity=1):
    """Turn on teeing to split both STDOUT and STDERR streams and sending second part to a file.

    @param file_name:       The name of the file.
    @type file_name:        str
    @param dir:             The path where the file is located.  If None, then the current directory
                            is assumed.
    @type dir:              str
    @param compress_type:   The compression type.  The integer values correspond to the compression
                            type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.
    @type compress_type:    int
    @param verbosity:       The verbosity level.
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
        print("Redirecting the sys.stdin IO stream to the python stdin IO stream.")
        print(("Redirecting the sys.stdout IO stream to both the python stdout IO stream and the log file '%s'." % file_path))
        print(("Redirecting the sys.stderr IO stream to both the python stderr IO stream and the log file '%s'." % file_path))

    # Set the tee IO streams.
    tee_stdout.split(stdout, tee_file)
    tee_stderr.split(stderr, tee_file)

    # IO stream redirection.
    sys.stdin  = tee_stdin
    sys.stdout = tee_stdout
    sys.stderr = tee_stderr


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
            print(("Directory ." + sep + dir + " already exists.\n"))


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
    if isinstance(file_name, file):
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
        if verbosity:
            print(("Opening the file " + repr(file_path) + " for reading."))
        if compress_type == 0:
            file_obj = open(file_path, 'r')
        elif compress_type == 1:
            if dep_check.bz2_module:
                file_obj = BZ2File(file_path, 'r')
            else:
                raise RelaxError("Cannot open the file " + repr(file_path) + ", try uncompressing first.  " + dep_check.bz2_module_message + ".")
        elif compress_type == 2:
            file_obj = GzipFile(file_path, 'r')
    except IOError, message:
        raise RelaxError("Cannot open the file " + repr(file_path) + ".  " + message.args[1] + ".")

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
    if isinstance(file_name, file):
        # Nothing to do here!
        return file_name

    # Something pretending to be a file object.
    if hasattr(file_name, 'write'):
        # Nothing to do here!
        return file_name

    # The null device.
    if search('devnull', file_name):
        # Devnull could not be imported!
        if not dep_check.devnull_import:
            raise RelaxError(dep_check.devnull_import_message + ".  To use devnull, please upgrade to Python >= 2.4.")

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
        raise RelaxFileOverwriteError(file_path, 'force flag')

    # Open the file for writing.
    try:
        if verbosity:
            print(("Opening the file " + repr(file_path) + " for writing."))
        if compress_type == 0:
            file_obj = open(file_path, 'w')
        elif compress_type == 1:
            file_obj = BZ2File(file_path, 'w')
        elif compress_type == 2:
            file_obj = GzipFile(file_path, 'w')
    except IOError, message:
        raise RelaxError("Cannot open the file " + repr(file_path) + ".  " + message.args[1] + ".")

    # Return the opened file.
    if return_path:
        return file_obj, file_path
    else:
        return file_obj


def read_spin_data(file=None, dir=None, file_data=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None, spin_id=None):
    """Generator function for reading the spin specific data from file.

    Description
    ===========

    This function reads a columnar formatted file where each line corresponds to a spin system.
    Spin identification is either through a spin ID string or through columns containing the
    molecule name, residue name and number, and/or spin name and number.


    @keyword file:          The name of the file to open.
    @type file:             str
    @keyword dir:           The directory containing the file (defaults to the current directory
                            if None).
    @type dir:              str or None
    @keyword file_data:     An alternative to opening a file, if the data already exists in the
                            correct format.  The format is a list of lists where the first index
                            corresponds to the row and the second the column.
    @type file_data:        list of lists
    @keyword spin_id_col:   The column containing the spin ID strings.  If supplied, the
                            mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col
                            arguments must be none.
    @type spin_id_col:      int or None
    @keyword mol_name_col:  The column containing the molecule name information.  If supplied,
                            spin_id_col must be None.
    @type mol_name_col:     int or None
    @keyword res_name_col:  The column containing the residue name information.  If supplied,
                            spin_id_col must be None.
    @type res_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information.  If supplied,
                            spin_id_col must be None.
    @type res_num_col:      int or None
    @keyword spin_name_col: The column containing the spin name information.  If supplied,
                            spin_id_col must be None.
    @type spin_name_col:    int or None
    @keyword spin_num_col:  The column containing the spin number information.  If supplied,
                            spin_id_col must be None.
    @type spin_num_col:     int or None
    @keyword data_col:      The column containing the data.
    @type data_col:         int or None
    @keyword error_col:     The column containing the errors.
    @type error_col:        int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all
                            spins.
    @type spin_id:          None or str
    @return:                A list of the spin specific data is yielded.  The format is a list
                            consisting of the spin ID string, the data value (if data_col is give),
                            and the error value (if error_col is given).  If both data_col and
                            error_col are None, then the spin ID string is simply yielded.
    @rtype:                 str, list of [str, float], or list of [str, float, float]
    """

    # Argument tests.
    col_args = [spin_id_col, mol_name_col, res_name_col, res_num_col, spin_name_col, spin_num_col, data_col, error_col]
    col_arg_names = ['spin_id_col', 'mol_name_col', 'res_name_col', 'res_num_col', 'spin_name_col', 'spin_num_col', 'data_col', 'error_col']
    for i in range(len(col_args)):
        if col_args[i] == 0:
            raise RelaxError, "The '%s' argument cannot be zero, column numbering starts at one." % col_arg_names[i]
    if spin_id_col and (mol_name_col or res_name_col or res_num_col or spin_name_col or spin_num_col):
        raise RelaxError, "If the 'spin_id_col' argument has been supplied, then the mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col must all be set to None."

    # Minimum number of columns.
    min_col_num = max(spin_id_col, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col)

    # Extract the data from the file.
    if not file_data:
        # Extract.
        file_data = extract_data(file, dir)

        # Strip the data of all comments and empty lines.
        file_data = strip(file_data)

    # No data!
    if not file_data:
        warn(RelaxFileEmptyWarning(file))
        return

    # Yield the data, spin by spin.
    missing_data = True
    for line in file_data:
        # Skip missing data.
        if len(line) < min_col_num:
            continue

        # Validate the sequence.
        try:
            generic_fns.sequence.validate_sequence(line, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col)
        except RelaxInvalidSeqError, msg:
            # Extract the message string, without the RelaxError bit.
            string = msg.__str__()[12:-1]

            # Give a warning.
            warn(RelaxWarning(string))

            # Skip the line.
            continue

        # Generate the spin ID string.
        if spin_id_col:
            id = line[spin_id_col-1]
        else:
            id = generate_spin_id_data_array(data=line, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col)

        # Convert the data.
        value = None
        if data_col:
            value = eval(line[data_col-1])
        error = None
        if error_col:
            error = eval(line[error_col-1])

        # Right, data is OK and exists.
        missing_data = False

        # Yield the data.
        if data_col and error_col:
            yield [id, value, error]
        elif data_col:
            yield [id, value]
        elif error_col:
            yield [id, error]
        else:
            yield id

    # Hmmm, no data!
    if missing_data:
        raise RelaxError("No corresponding data could be found within the file.")


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
            raise RelaxMissingBinaryError(binary)

        # Test that if the binary is executable.
        if not access(binary, X_OK):
            raise RelaxNonExecError(binary)

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
        raise RelaxNoInPathError(binary)


def write_spin_data(file, dir=None, sep=None, spin_ids=None, mol_names=None, res_nums=None, res_names=None, spin_nums=None, spin_names=None, force=False, data=None, data_name=None, data_length=20, data_format=None, error=None, error_name=None, error_length=20, error_format=None):
    """Generator function for reading the spin specific data from file.

    Description
    ===========

    This function writes a columnar formatted file where each line corresponds to a spin system.
    Spin identification is either through a spin ID string or through columns containing the
    molecule name, residue name and number, and/or spin name and number.


    @param file:            The name of the file to write the data to (or alternatively an already opened file object).
    @type file:             str or file object
    @keyword dir:           The directory to place the file into (defaults to the current directory if None and the file argument is not a file object).
    @type dir:              str or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_ids:      The list of spin ID strings.
    @type spin_ids:         None or list of str
    @keyword mol_names:     The list of molecule names.
    @type mol_names:        None or list of str
    @keyword res_nums:      The list of residue numbers.
    @type res_nums:         None or list of int
    @keyword res_names:     The list of residue names.
    @type res_names:        None or list of str
    @keyword spin_nums:     The list of spin numbers.
    @type spin_nums:        None or list of int
    @keyword spin_names:    The list of spin names.
    @type spin_names:       None or list of str
    @keyword force:         A flag which if True will cause an existing file to be overwritten.
    @type force:            bool
    @keyword data:          A list of the data to write out.  The first dimension corresponds to the spins.  A second dimension can also be given if multiple data sets across multiple columns are desired.
    @type data:             list or list of lists
    @keyword data_name:     A name corresponding to the data argument.  If the data argument is a list of lists, then this must also be a list with the same length as the second dimension of the data arg.
    @type data_name:        str or list of str
    @keyword data_length:   The length of the data columns.
    @type data_length:      int
    @keyword data_format:   The optional python formatting string for the data columns, e.g. "%-30s".
    @type data_format:      None or str
    @keyword error:         A list of the errors to write out.  The first dimension corresponds to the spins.  A second dimension can also be given if multiple data sets across multiple columns are desired.  These will be inter-dispersed between the data columns, if the data is given.  If the data arg is not None, then this must have the same dimensions as that object.
    @type error:            list or list of lists
    @keyword error_name:    A name corresponding to the error argument.  If the error argument is a list of lists, then this must also be a list with the same length at the second dimension of the error arg.
    @type error_name:       str or list of str
    @keyword error_length:  The length of the error columns.
    @type error_length:     int
    @keyword error_format:  The optional python formatting string for the error columns, e.g. "%-30s".
    @type error_format:     None or str
    """

    # Data argument tests.
    if data:
        # Data is a list of lists.
        if isinstance(data[0], list):
            # Data and data_name don't match.
            if not isinstance(data_name, list):
                raise RelaxError("The data_name arg '%s' must be a list as the data argument is a list of lists." % data_name)

            # Error doesn't match.
            if error and (len(data) != len(error) or len(data[0]) != len(error[0])):
                raise RelaxError("The data arg:\n%s\n\ndoes not have the same dimensions as the error arg:\n%s." % (data, error))

        # Data is a simple list.
        else:
            # Data and data_name don't match.
            if not isinstance(data_name, str):
                raise RelaxError("The data_name arg '%s' must be a string as the data argument is a simple list." % data_name)

            # Error doesn't match.
            if error and len(data) != len(error):
                raise RelaxError("The data arg:\n%s\n\ndoes not have the same dimensions as the error arg:\n%s." % (data, error))

    # Error argument tests.
    if error:
        # Error is a list of lists.
        if isinstance(error[0], list):
            # Error and error_name don't match.
            if not isinstance(error_name, list):
                raise RelaxError("The error_name arg '%s' must be a list as the error argument is a list of lists." % error_name)

        # Error is a simple list.
        else:
            # Error and error_name don't match.
            if not isinstance(error_name, str):
                raise RelaxError("The error_name arg '%s' must be a string as the error argument is a simple list." % error_name)

    # Number of spins check.
    args = [spin_ids, mol_names, res_nums, res_names, spin_nums, spin_names]
    arg_names = ['spin_ids', 'mol_names', 'res_nums', 'res_names', 'spin_nums', 'spin_names']
    N = None
    first_arg = None
    first_arg_name = None
    for i in range(len(args)):
        if isinstance(args[i], list):
            # First list match.
            if N == None:
                N = len(args[i])
                first_arg = args[i]
                first_arg_name = arg_names[i]

            # Length check.
            if len(args[i]) != N:
                raise RelaxError("The %s and %s arguments do not have the same number of spins ('%s' vs. '%s' respectively)." % (first_arg_name, arg_names[i], len(first_arg), len(args[i])))

    # Nothing?!?
    if N == None:
        raise RelaxError("No spin ID data is present.")

    # Data and error length check.
    if data and len(data) != N:
        raise RelaxError("The %s and data arguments do not have the same number of spins ('%s' vs. '%s' respectively)." % (first_arg_name, len(first_arg), len(data)))
    if error and len(error) != N:
        raise RelaxError("The %s and error arguments do not have the same number of spins ('%s' vs. '%s' respectively)." % (first_arg_name, len(first_arg), len(error)))

    # The spin arguments.
    args = [spin_ids, mol_names, res_nums, res_names, spin_nums, spin_names]
    arg_names = ['spin_id', 'mol_name', 'res_num', 'res_name', 'spin_num', 'spin_name']

    # No special separator character.
    if sep == None:
        sep = ''

    # Open the file.
    file = open_write_file(file_name=file, dir=dir, force=force)

    # The spin ID column lengths.
    len_args = [10] * 6
    for i in range(len(args)):
        # Different separator.
        if sep:
            len_args[i] = 0
            continue

        # Minimum width of the header name lengths.
        if args[i] and len(arg_names[i]) > len_args[i]:
            len_args[i] = len(arg_names[i]) + 2

        # Minimum width of the spin ID data.
        for spin_index in range(N):
            if args[i] and len(repr(args[i][spin_index])) > len_args[i]:
                len_args[i] = len(repr(args[i][spin_index])) + 1

    # Data and error formatting strings.
    if sep:
        data_length = ''
    data_head_format = "%%-%ss" % data_length
    if not data_format:
        data_format = "%%%ss" % data_length
    error_head_format = "%%-%ss" % error_length
    if not error_format:
        error_format = "%%%ss" % error_length


    # Header.
    #########

    # Init.
    file.write("\n")
    prefix = '# '
    shift = -2

    # The spin ID info.
    for i in range(len(args)):
        if args[i]:
            file.write(("%s%%-%ss%s" % (prefix, len_args[i]+shift, sep)) % arg_names[i])
            prefix = ' '
            shift = 0

    # The data.
    if data:
        # List of lists.
        if isinstance(data[0], list):
            # Loop over the list.
            for i in range(len(data[0])):
                # The data.
                file.write((prefix+data_head_format+sep) % data_name[i])

                # The error.
                if error:
                    file.write((prefix+error_head_format+sep) % error_name[i])

        # Simple list.
        else:
            # The data.
            file.write((prefix+data_head_format+sep) % data_name)

            # The error.
            if error:
                file.write((prefix+error_head_format+sep) % error_name)

    # Only errors.
    elif error:
        # List of lists.
        if isinstance(error[0], list):
            for i in range(len(error[0])):
                file.write((prefix+error_head_format+sep) % error_name[i])

        # Simple list.
        else:
            file.write((prefix+error_head_format+sep) % error_name)

    # Terminate the line.
    file.write("\n")


    # Spin specific data.
    #####################

    # Loop over the spins.
    for spin_index in range(N):
        # The prefix.
        prefix = ''

        # The spin ID info.
        for i in range(len(args)):
            if args[i]:
                file.write(("%s%%-%ss%s" % (prefix, len_args[i], sep)) % args[i][spin_index])
                prefix = ' '

        # The data.
        if data:
            # List of lists.
            if isinstance(data[0], list):
                # Loop over the list.
                for i in range(len(data[0])):
                    # The data.
                    file.write((prefix+data_format+sep) % data[spin_index][i])

                    # The error.
                    if error:
                        file.write((prefix+error_format+sep) % error[spin_index][i])

            # Simple list.
            else:
                # The data.
                file.write((prefix+data_format+sep) % data[spin_index])

                # The error.
                if error:
                    file.write((prefix+error_format+sep) % error[spin_index])

        # Only errors.
        elif error:
            # List of lists.
            if isinstance(error[0], list):
                for i in range(len(error[0])):
                    file.write((prefix+error_format+sep) % error[spin_index][i])

            # Simple list.
            else:
                file.write((prefix+error_format+sep) % error[spin_index])

        # End of the line.
        file.write("\n")



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
        lines = split(self.data, '\n')

        # Loop over the lines, re-adding the newline character to match the file object readlines() method.
        for i in xrange(len(lines)):
            lines[i] = lines[i] + '\n'

        # Return the file lines (except the last as it is empty).
        return lines[:-1]



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
