###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""Module for the manipulation of J coupling data."""

# Python module imports.
import sys
from warnings import warn

# relax module imports.
from lib.check_types import is_float
from pipe_control import pipes
from pipe_control.interatomic import consistent_interatomic_data, create_interatom, interatomic_loop, return_interatom
from pipe_control.mol_res_spin import exists_mol_res_spin_data, return_spin
from lib.errors import RelaxError, RelaxNoJError, RelaxNoSequenceError
from lib.io import extract_data, open_write_file, strip, write_data
from lib.warnings import RelaxWarning


def check_pipe_setup(pipe=None, sequence=False, j=False):
    """Check that the current data pipe has been setup sufficiently.

    @keyword pipe:      The data pipe to check, defaulting to the current pipe.
    @type pipe:         None or str
    @keyword sequence:  A flag which when True will invoke the sequence data check.
    @type sequence:     bool
    @keyword j:         A flag which if True will check that J couplings exist.
    @type j:            bool
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Test if the current data pipe exists.
    pipes.test(pipe)

    # Test if sequence data exists.
    if sequence and not exists_mol_res_spin_data(pipe):
        raise RelaxNoSequenceError(pipe)

    # Test if J coupling data exists.
    if j:
        # Search for interatomic data.
        data = False
        for interatom in interatomic_loop():
            if hasattr(interatom, 'j_coupling'):
                data = True
                break

        # No data.
        if not data:
            raise RelaxNoJError()


def copy(pipe_from=None, pipe_to=None):
    """Copy the J coupling data from one data pipe to another.

    @keyword pipe_from: The data pipe to copy the J coupling data from.  This defaults to the current data pipe.
    @type pipe_from:    str
    @keyword pipe_to:   The data pipe to copy the J coupling data to.  This defaults to the current data pipe.
    @type pipe_to:      str
    """

    # Defaults.
    if pipe_from == None and pipe_to == None:
        raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")
    elif pipe_from == None:
        pipe_from = pipes.cdp_name()
    elif pipe_to == None:
        pipe_to = pipes.cdp_name()

    # Check the pipe setup.
    check_pipe_setup(pipe=pipe_from, sequence=True, j=True)
    check_pipe_setup(pipe=pipe_to, sequence=True)

    # Get the data pipes.
    dp_from = pipes.get_pipe(pipe_from)
    dp_to = pipes.get_pipe(pipe_to)

    # Test that the interatomic data is consistent between the two data pipe.
    consistent_interatomic_data(pipe1=pipe_to, pipe2=pipe_from)

    # Loop over the interatomic data.
    for i in range(len(dp_from.interatomic)):
        # Alias the containers.
        interatom_from = dp_from.interatomic[i]
        interatom_to = dp_to.interatomic[i]

        # No data or errors.
        if not hasattr(interatom_from, 'j_coupling') or not hasattr(interatom_from, 'j_coupling_err'):
            continue

        # Copy the value and error from pipe_from.
        if hasattr(interatom_from, 'j_coupling'):
            interatom_to.j_coupling = interatom_from.j_coupling
        if hasattr(interatom_from, 'j_coupling_err'):
            interatom_to.j_coupling_err = interatom_from.j_coupling_err


def delete():
    """Delete all J coupling data."""

    # Check the pipe setup.
    check_pipe_setup(sequence=True, j=True)

    # The interatomic data.
    for interatom in interatomic_loop():
        # The data.
        if hasattr(interatom, 'j_coupling'):
            del interatom.j_coupling

        # The error.
        if hasattr(interatom, 'j_coupling_err'):
            del interatom.j_coupling_err


def display():
    """Display the J coupling data."""

    # Check the pipe setup.
    check_pipe_setup(sequence=True, j=True)

    # Call the write method with sys.stdout as the file.
    write(file=sys.stdout)


def read(file=None, dir=None, file_data=None, spin_id1_col=None, spin_id2_col=None, data_col=None, error_col=None, sign_col=None, sep=None):
    """Read the J coupling data from file.

    @keyword file:          The name of the file to open.
    @type file:             str
    @keyword dir:           The directory containing the file (defaults to the current directory if None).
    @type dir:              str or None
    @keyword file_data:     An alternative to opening a file, if the data already exists in the correct format.  The format is a list of lists where the first index corresponds to the row and the second the column.
    @type file_data:        list of lists
    @keyword spin_id1_col:  The column containing the spin ID strings of the first spin.
    @type spin_id1_col:     int
    @keyword spin_id2_col:  The column containing the spin ID strings of the second spin.
    @type spin_id2_col:     int
    @keyword data_col:      The column containing the J coupling data in Hz.
    @type data_col:         int or None
    @keyword error_col:     The column containing the J coupling errors.
    @type error_col:        int or None
    @keyword sign_col:      The optional column containing the sign of the J coupling.
    @type sign_col:         int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True)

    # Either the data or error column must be supplied.
    if data_col == None and error_col == None:
        raise RelaxError("One of either the data or error column must be supplied.")

    # Extract the data from the file, and remove comments and blank lines.
    file_data = extract_data(file, dir, sep=sep)
    file_data = strip(file_data, comments=False)

    # Loop over the J coupling data.
    data = []
    for line in file_data:
        # Invalid columns.
        if spin_id1_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no first spin ID column can be found." % line))
            continue
        if spin_id2_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no second spin ID column can be found." % line))
            continue
        if data_col and data_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no data column can be found." % line))
            continue
        if error_col and error_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no error column can be found." % line))
            continue
        if sign_col and sign_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no sign column can be found." % line))
            continue

        # Unpack.
        spin_id1 = line[spin_id1_col-1]
        spin_id2 = line[spin_id2_col-1]
        value = None
        if data_col:
            value = line[data_col-1]
        error = None
        if error_col:
            error = line[error_col-1]
        sign = None
        if sign_col:
            sign = line[sign_col-1]

        # Convert the spin IDs.
        if spin_id1[0] in ["\"", "\'"]:
            spin_id1 = eval(spin_id1)
        if spin_id2[0] in ["\"", "\'"]:
            spin_id2 = eval(spin_id2)

        # Convert and check the value.
        if value == 'None':
            value = None
        if value != None:
            try:
                value = float(value)
            except ValueError:
                warn(RelaxWarning("The J coupling value of the line %s is invalid." % line))
                continue

        # The sign data.
        if sign == 'None':
            sign = None
        if sign != None:
            try:
                sign = float(sign)
            except ValueError:
                warn(RelaxWarning("The J coupling sign of the line %s is invalid." % line))
                continue
            if sign not in [1.0, -1.0]:
                warn(RelaxWarning("The J coupling sign of the line %s is invalid." % line))
                continue

        # Convert and check the error.
        if error == 'None':
            error = None
        if error != None:
            try:
                error = float(error)
            except ValueError:
                warn(RelaxWarning("The error value of the line %s is invalid." % line))
                continue

        # Get the spins.
        spin1 = return_spin(spin_id1)
        spin2 = return_spin(spin_id2)

        # Check the spin IDs.
        if not spin1:
            warn(RelaxWarning("The spin ID '%s' cannot be found in the current data pipe, skipping the data %s." % (spin_id1, line)))
            continue
        if not spin2:
            warn(RelaxWarning("The spin ID '%s' cannot be found in the current data pipe, skipping the data %s." % (spin_id2, line)))
            continue

        # Test the error value (cannot be 0.0).
        if error == 0.0:
            raise RelaxError("An invalid error value of zero has been encountered.")

        # Get the interatomic data container.
        interatom = return_interatom(spin_id1, spin_id2)

        # Create the container if needed.
        if interatom == None:
            interatom = create_interatom(spin_id1=spin_id1, spin_id2=spin_id2)

        # Add the data.
        if data_col:
            # Sign conversion.
            if sign != None:
                value = value * sign

            # Add the value.
            interatom.j_coupling = value

        # Add the error.
        if error_col:
            interatom.j_coupling_err = error

        # Append the data for printout.
        data.append([spin_id1, spin_id2])
        if is_float(value):
            data[-1].append("%20.15f" % value)
        else:
            data[-1].append("%20s" % value)
        if is_float(error):
            data[-1].append("%20.15f" % error)
        else:
            data[-1].append("%20s" % error)

    # No data, so fail hard!
    if not len(data):
        raise RelaxError("No J coupling data could be extracted.")

    # Print out.
    print("The following J coupling have been loaded into the relax data store:\n")
    write_data(out=sys.stdout, headings=["Spin_ID1", "Spin_ID2", "Value", "Error"], data=data)


def write(file=None, dir=None, force=False):
    """Write the J coupling data to file.

    @keyword file:      The file name or object to write to.
    @type file:         str or file object
    @keyword dir:       The name of the directory to place the file into (defaults to the current directory).
    @type dir:          str
    @keyword force:     A flag which if True will cause any pre-existing file to be overwritten.
    @type force:        bool
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, j=True)

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Loop over the interatomic data containers and collect the data.
    data = []
    for interatom in interatomic_loop():
        # Skip deselected containers.
        if not interatom.select:
            continue

        # Skip containers with no J coupling.
        if not hasattr(interatom, 'j_coupling'):
            continue

        # Append the spin data.
        data.append([])
        data[-1].append(interatom.spin_id1)
        data[-1].append(interatom.spin_id2)

        # The value.
        data[-1].append(repr(interatom.j_coupling))

        # The error.
        if hasattr(interatom, 'j_coupling_err'):
            data[-1].append(repr(interatom.j_coupling_err))
        else:
            data[-1].append(repr(None))

    # Write out.
    write_data(out=file, headings=["Spin_ID1", "Spin_ID2", "J coupling", "J coupling"], data=data)
