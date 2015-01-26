from __future__ import absolute_import
###############################################################################
#                                                                             #
# Copyright (C) 2003-2015 Edward d'Auvergne                                   #
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
"""Module for handling the molecule, residue, and spin sequence data."""

# Python module imports.
import sys
from warnings import warn

# relax module imports.
from lib.check_types import is_float
from lib.errors import RelaxError, RelaxInvalidSeqError
from lib.io import extract_data, open_write_file, strip, write_data
from lib.selection import spin_id_to_data_list
from lib.warnings import RelaxWarning, RelaxFileEmptyWarning


# The 3 letter to 1 letter amino acid code table.
AA_CODES = {
    "ALA": "A",
    "ARG": "R",
    "ASN": "N",
    "ASP": "D",
    "CYS": "C",
    "GLU": "E",
    "GLN": "Q",
    "GLY": "G",
    "HIS": "H",
    "ILE": "I",
    "LEU": "L",
    "LYS": "K",
    "MET": "M",
    "PHE": "F",
    "PRO": "P",
    "SER": "S",
    "THR": "T",
    "TRP": "W",
    "TYR": "Y",
    "VAL": "V",
}


def aa_codes_three_to_one(code):
    """Convert the given three letter amino acid code to the corresponding one letter code.

    Any non-standard residues will be converted to '*'.


    @param code:    The three letter amino acid code to convert.
    @type code:     str
    @return:        The corresponding one letter amino acid code, or '*'.
    @rtype:         str
    """

    # Convert to uppercase.
    upper_code = code.upper()

    # The code exists.
    if upper_code in AA_CODES:
        return AA_CODES[upper_code]

    # No code.
    return '*'


def read_spin_data(file=None, dir=None, file_data=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None, spin_id=None):
    """Generator function for reading the spin specific data from file.

    Description
    ===========

    This function reads a columnar formatted file where each line corresponds to a spin system. Spin identification is either through a spin ID string or through columns containing the molecule name, residue name and number, and/or spin name and number.


    @keyword file:          The name of the file to open.
    @type file:             str
    @keyword dir:           The directory containing the file (defaults to the current directory if None).
    @type dir:              str or None
    @keyword file_data:     An alternative to opening a file, if the data already exists in the correct format.  The format is a list of lists where the first index corresponds to the row and the second the column.
    @type file_data:        list of lists
    @keyword spin_id_col:   The column containing the spin ID strings.  If supplied, the mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col arguments must be none.
    @type spin_id_col:      int or None
    @keyword mol_name_col:  The column containing the molecule name information.  If supplied, spin_id_col must be None.
    @type mol_name_col:     int or None
    @keyword res_name_col:  The column containing the residue name information.  If supplied, spin_id_col must be None.
    @type res_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information.  If supplied, spin_id_col must be None.
    @type res_num_col:      int or None
    @keyword spin_name_col: The column containing the spin name information.  If supplied, spin_id_col must be None.
    @type spin_name_col:    int or None
    @keyword spin_num_col:  The column containing the spin number information.  If supplied, spin_id_col must be None.
    @type spin_num_col:     int or None
    @keyword data_col:      The column containing the data.
    @type data_col:         int or None
    @keyword error_col:     The column containing the errors.
    @type error_col:        int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all spins.
    @type spin_id:          None or str
    @return:                A list of the spin specific data is yielded.  The format is a list consisting of the spin ID string, the data value (if data_col is give), and the error value (if error_col is given).  If both data_col and error_col are None, then the spin ID string is simply yielded.
    @rtype:                 str, list of [str, float], or list of [str, float, float]
    """

    # Argument tests.
    col_args = [spin_id_col, mol_name_col, res_name_col, res_num_col, spin_name_col, spin_num_col, data_col, error_col]
    col_arg_names = ['spin_id_col', 'mol_name_col', 'res_name_col', 'res_num_col', 'spin_name_col', 'spin_num_col', 'data_col', 'error_col']
    for i in range(len(col_args)):
        if col_args[i] == 0:
            raise RelaxError("The '%s' argument cannot be zero, column numbering starts at one." % col_arg_names[i])
    if spin_id_col and (mol_name_col or res_name_col or res_num_col or spin_name_col or spin_num_col):
        raise RelaxError("If the 'spin_id_col' argument has been supplied, then the mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col must all be set to None.")

    # Minimum number of columns.
    min_col_num = max([_f for _f in [spin_id_col, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col] if _f])

    # Extract the data from the file.
    if not file_data:
        # Extract.
        file_data = extract_data(file, dir)

        # Strip the data of all comments and empty lines.
        if spin_id_col != None:
            file_data = strip(file_data, comments=False)
        else:
            file_data = strip(file_data)

    # No data!
    if not file_data:
        warn(RelaxFileEmptyWarning(file))
        return

    # Yield the data, spin by spin.
    missing_data = True
    for line in file_data:
        # Convert the spin IDs.
        if spin_id_col != None and line[spin_id_col-1][0] in ["\"", "\'"]:
            line[spin_id_col-1] = eval(line[spin_id_col-1])

        # Convert.
        # Validate the sequence.
        try:
            validate_sequence(line, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col)
        except RelaxInvalidSeqError:
            # Extract the message string, without the RelaxError bit.
            msg = sys.exc_info()[1]
            string = msg.__str__()[12:-1]

            # Give a warning.
            warn(RelaxWarning(string))

            # Skip the line.
            continue

        # Get the spin data from the ID.
        if spin_id_col:
            # Invalid spin ID.
            if line[spin_id_col-1] == '#':
                warn(RelaxWarning("Invalid spin ID, skipping the line %s" % line))
                continue

            mol_name, res_num, res_name, spin_num, spin_name = spin_id_to_data_list(line[spin_id_col-1])

        # Convert the spin data.
        else:
            # The molecule.
            mol_name = None
            if mol_name_col != None and line[mol_name_col-1] != 'None':
                mol_name = line[mol_name_col-1]

            # The residue number, catching bad values.
            res_num = None
            if res_num_col != None:
                try:
                    if line[res_num_col-1] == 'None':
                        res_num = None
                    else:
                        res_num = int(line[res_num_col-1])
                except ValueError:
                    warn(RelaxWarning("Invalid residue number, skipping the line %s" % line))
                    continue

            # The residue name.
            res_name = None
            if res_name_col != None and line[res_name_col-1] != 'None':
                res_name = line[res_name_col-1]

            # The spin number, catching bad values.
            spin_num = None
            if spin_num_col != None:
                try:
                    if line[spin_num_col-1] == 'None':
                        spin_num = None
                    else:
                        spin_num = int(line[spin_num_col-1])
                except ValueError:
                    warn(RelaxWarning("Invalid spin number, skipping the line %s" % line))
                    continue

            # The spin name.
            spin_name = None
            if spin_name_col != None and line[spin_name_col-1] != 'None':
                spin_name = line[spin_name_col-1]

        # Convert the data.
        value = None
        if data_col != None:
            try:
                # None.
                if line[data_col-1] == 'None':
                    value = None

                # A float.
                else:
                    value = float(line[data_col-1])

            # Bad data.
            except ValueError:
                warn(RelaxWarning("Invalid data, skipping the line %s" % line))
                continue

        # Convert the errors.
        error = None
        if error_col != None:
            try:
                # None.
                if line[error_col-1] == 'None':
                    error = None

                # A float.
                else:
                    error = float(line[error_col-1])

            # Bad data.
            except ValueError:
                warn(RelaxWarning("Invalid errors, skipping the line %s" % line))
                continue

        # Right, data is OK and exists.
        missing_data = False

        # Yield the data.
        if data_col and error_col:
            yield mol_name, res_num, res_name, spin_num, spin_name, value, error
        elif data_col:
            yield mol_name, res_num, res_name, spin_num, spin_name, value
        elif error_col:
            yield mol_name, res_num, res_name, spin_num, spin_name, error
        else:
            yield mol_name, res_num, res_name, spin_num, spin_name

    # Hmmm, no data!
    if missing_data:
        raise RelaxError("No corresponding data could be found within the file.")


def validate_sequence(data, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None):
    """Test if the sequence data is valid.

    The only function this performs is to raise a RelaxError if the data is invalid.


    @param data:            The sequence data.
    @type data:             list of lists.
    @keyword spin_id_col:   The column containing the spin ID strings.
    @type spin_id_col:      int or None
    @param mol_name_col:    The column containing the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column containing the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column containing the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column containing the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column containing the spin number information.
    @type spin_num_col:     int or None
    """

    # Spin ID.
    if spin_id_col:
        if len(data) < spin_id_col:
            raise RelaxInvalidSeqError(data, "the Spin ID data is missing")

    # Molecule name data.
    if mol_name_col:
        if len(data) < mol_name_col:
            raise RelaxInvalidSeqError(data, "the molecule name data is missing")

    # Residue number data.
    if res_num_col:
        # No data in column.
        if len(data) < res_num_col:
            raise RelaxInvalidSeqError(data, "the residue number data is missing")

        # Bad data in column.
        try:
            res_num = eval(data[res_num_col-1])
            if not (res_num == None or isinstance(res_num, int)):
                raise ValueError
        except:
            raise RelaxInvalidSeqError(data, "the residue number data '%s' is invalid" % data[res_num_col-1])

    # Residue name data.
    if res_name_col:
        if len(data) < res_name_col:
            raise RelaxInvalidSeqError(data, "the residue name data is missing")

    # Spin number data.
    if spin_num_col:
        # No data in column.
        if len(data) < spin_num_col:
            raise RelaxInvalidSeqError(data, "the spin number data is missing")

        # Bad data in column.
        try:
            res_num = eval(data[res_num_col-1])
            if not (res_num == None or isinstance(res_num, int)):
                raise ValueError
        except:
            raise RelaxInvalidSeqError(data, "the spin number data '%s' is invalid" % data[res_num_col-1])

    # Spin name data.
    if spin_name_col:
        if len(data) < spin_name_col:
            raise RelaxInvalidSeqError(data, "the spin name data is missing")

    # Data.
    if data_col:
        if len(data) < data_col:
            raise RelaxInvalidSeqError(data, "the data is missing")

    # Errors
    if error_col:
        if len(data) < error_col:
            raise RelaxInvalidSeqError(data, "the error data is missing")


def write_spin_data(file, dir=None, sep=None, spin_ids=None, mol_names=None, res_nums=None, res_names=None, spin_nums=None, spin_names=None, force=False, data=None, data_name=None, error=None, error_name=None, float_format="%20.15g"):
    """Generator function for reading the spin specific data from file.

    Description
    ===========

    This function writes a columnar formatted file where each line corresponds to a spin system.  Spin identification is either through a spin ID string or through columns containing the molecule name, residue name and number, and/or spin name and number.


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
    @keyword error:         A list of the errors to write out.  The first dimension corresponds to the spins.  A second dimension can also be given if multiple data sets across multiple columns are desired.  These will be inter-dispersed between the data columns, if the data is given.  If the data arg is not None, then this must have the same dimensions as that object.
    @type error:            list or list of lists
    @keyword error_name:    A name corresponding to the error argument.  If the error argument is a list of lists, then this must also be a list with the same length at the second dimension of the error arg.
    @type error_name:       str or list of str
    @keyword float_format:  A float formatting string to use for the data and error whenever a float is found.
    @type float_format:     str
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


    # Init.
    headings = []
    file_data = []

    # Headers - the spin ID info.
    for i in range(len(args)):
        if args[i]:
            headings.append(arg_names[i])

    # Headers - the data.
    if data:
        # List of lists.
        if isinstance(data[0], list):
            # Loop over the list.
            for i in range(len(data[0])):
                # The data.
                headings.append(data_name[i])

                # The error.
                if error:
                    headings.append(error_name[i])

        # Simple list.
        else:
            # The data.
            headings.append(data_name)

            # The error.
            if error:
                headings.append(error_name)

    # Headers - only errors.
    elif error:
        # List of lists.
        if isinstance(error[0], list):
            for i in range(len(error[0])):
                headings.append(error_name[i])

        # Simple list.
        else:
            headings.append(error_name)

    # No headings.
    if headings == []:
        headings = None

    # Spin specific data.
    for spin_index in range(N):
        # Append a new data row.
        file_data.append([])

        # The spin ID info.
        for i in range(len(args)):
            if args[i]:
                value = args[i][spin_index]
                if not isinstance(value, str):
                    value = repr(value)
                file_data[-1].append(value)

        # The data.
        if data:
            # List of lists.
            if isinstance(data[0], list):
                # Loop over the list.
                for i in range(len(data[0])):
                    # The data.
                    if is_float(data[spin_index][i]):
                        file_data[-1].append(float_format % data[spin_index][i])
                    else:
                        file_data[-1].append(repr(data[spin_index][i]))

                    # The error.
                    if error:
                        if is_float(error[spin_index][i]):
                            file_data[-1].append(float_format % error[spin_index][i])
                        else:
                            file_data[-1].append(repr(error[spin_index][i]))

            # Simple list.
            else:
                # The data.
                if is_float(data[spin_index]):
                    file_data[-1].append(float_format % data[spin_index])
                else:
                    file_data[-1].append(repr(data[spin_index]))

                # The error.
                if error:
                    if is_float(error[spin_index]):
                        file_data[-1].append(float_format % error[spin_index])
                    else:
                        file_data[-1].append(repr(error[spin_index]))

        # Only errors.
        elif error:
            # List of lists.
            if isinstance(error[0], list):
                for i in range(len(error[0])):
                    file_data[-1].append(repr(error[spin_index][i]))

            # Simple list.
            else:
                file_data[-1].append(repr(error[spin_index]))

    # No data to write, so do nothing!
    if file_data == [] or file_data == [[]]:
        return

    # Open the file for writing.
    file = open_write_file(file_name=file, dir=dir, force=force)

    # Write out the file data.
    write_data(out=file, headings=headings, data=file_data, sep=sep)
