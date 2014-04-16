###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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

# relax module imports.
from lib.errors import RelaxInvalidSeqError


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
