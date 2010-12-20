###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007-2009 Edward d'Auvergne                        #
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
"""Module for reading/writing/displaying the results in a data pipe."""

# Python module imports.
from os.path import dirname
from re import search
from string import split
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from relax_errors import RelaxError, RelaxFileEmptyError
from relax_io import extract_data, get_file_path, open_read_file, open_write_file, strip
from specific_fns.setup import get_specific_fn


def check_xml(file_path, file):
    """Check the XML results file.

    @param file_path:   The path of the file.
    @type file_path:    str
    @param file:        The file object representing the results file.
    @type file:         file object
    """

    # Header line.
    lines = []
    lines.append(file.readline())
    lines.append(file.readline())

    # Be nice and go back to the start of the file.
    file.seek(0)

    # A saved state!.
    if search("<relax", lines[1]):
        raise RelaxError("The file '%s' is a relax saved state and not a results file." % file_path)


def determine_format(file):
    """Determine the format of the results file.

    @keyword file:  The file object representing the results file.
    @type file:     file object
    @return:        The results file format.  This can be 'xml' or 'columnar'.
    @rtype:         str or None
    """

    # Header line.
    header = file.readline()
    header = header[:-1]    # Strip the trailing newline.

    # Be nice and go back to the start of the file.
    file.seek(0)

    # XML.
    if search("<\?xml", header):
        return 'xml'

    # Columnar.
    if split(header)[0:3] == ['Num', 'Name', 'Selected']:
        return 'columnar'


def display():
    """Displaying the results/contents of the current data pipe."""

    # Test if the current data pipe exists.
    pipes.test()

    # Write the results.
    ds.to_xml(sys.stdout)


def read(file='results', directory=None):
    """Function for reading the data out of a file."""

    # Test if the current data pipe exists.
    pipes.test()

    # Make sure that the data pipe is empty.
    if not cdp.is_empty():
        raise RelaxError("The current data pipe is not empty.")

    # Get the full file path, for later use.
    file_path = get_file_path(file_name=file, dir=directory)

    # Open the file.
    file = open_read_file(file_name=file_path)

    # Determine the format of the file.
    format = determine_format(file)

    # XML results.
    if format == 'xml':
        # Is this a results or save file?
        check_xml(file_path, file)

        # Execute the data store XML parser.
        ds.from_xml(file, dir=dirname(file_path), pipe_to=pipes.cdp_name())

    # Columnar results.
    elif format == 'columnar':
        read_function = get_specific_fn('read_columnar_results', pipes.get_type(), raise_error=False)

        # Extract the data from the file.
        file_data = extract_data(file=file)

        # Strip data.
        file_data = strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Read the results.
        read_function(file_data)

    # Unknown results file.
    else:
        raise RelaxError("The format of the results file " + repr(file_path) + " cannot be determined.")


def write(file="results", directory=None, force=False, compress_type=1, verbosity=1):
    """Create the results file."""

    # Test if the current data pipe exists.
    pipes.test()

    # The special data pipe name directory.
    if directory == 'pipe_name':
        directory = pipes.cdp_name()

    # Open the file for writing.
    results_file = open_write_file(file_name=file, dir=directory, force=force, compress_type=compress_type, verbosity=verbosity)

    # Write the results.
    ds.to_xml(results_file, pipes=pipes.cdp_name())

    # Close the results file.
    results_file.close()
