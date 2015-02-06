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
"""Module for interfacing with Grace (also known as Xmgrace, Xmgr, and ace)."""

# Python module imports.
from os import system

# relax module imports.
from lib.errors import RelaxError, RelaxNoSequenceError, RelaxNoSimError
from lib.io import get_file_path, open_write_file, test_binary
from pipe_control.mol_res_spin import count_molecules, count_residues, count_spins, exists_mol_res_spin_data
from pipe_control import pipes
from pipe_control.plotting import assemble_data
from specific_analyses.api import return_api
from status import Status; status = Status()


def determine_seq_type(spin_id=None):
    """Determine the spin sequence data type.

    The purpose is to identify systems whereby only spins or only residues exist.

    @keyword spin_id:   The spin identification string.
    @type spin_id:      str
    @return:            The spin sequence data type.  This can be one of 'spin', 'res,' or 'mixed'.
    @rtype:             str
    """

    # Count the molecules, residues, and spins.
    num_mol = count_molecules(spin_id)
    num_res = count_residues(spin_id)
    num_spin = count_spins(spin_id)

    # Only residues.
    if num_mol == 1 and num_spin == 1:
        return 'res'

    # Only spins.
    if num_mol == 1 and num_res == 1:
        return 'spin'

    # Mixed.
    return 'mixed'


def get_data_types():
    """Get all of the data types to plot for the current data pipe.

    @return:    A list of lists of all the allowable data type descriptions and their values.
    @rtype:     list of list of str
    """

    # The specific analysis API object.
    api = return_api()

    # Return an empty list if the required functions are absent.
    if not hasattr(api, 'data_names') or not hasattr(api, 'return_data_desc'):
        return []

    # The data names, if they exist.
    names = api.data_names(set='params')

    # Initialise the list and then add the sequence data.
    data = []
    data.append(["Spin sequence", 'spin'])

    # Loop over the parameters.
    for name in (api.data_names(set='params') + api.data_names(set='generic') + api.data_names(set='min')):
        # Get the description.
        try:
            desc = api.return_data_desc(name)
        except:
            return []

        # No description.
        if not desc:
            text = name

        # The text.
        else:
            text = "'%s':  %s" % (name, desc)

        # Append the description.
        data.append([text, name])

    # Return the data.
    return data


def view(file=None, dir=None, grace_exe='xmgrace'):
    """Execute Grace.

    @keyword file:      The name of the file to open in Grace.
    @type file:         str
    @keyword dir:       The optional directory containing the file.
    @type dir:          str
    @keyword grace_exe: The name of the Grace executable file.  This should be located within the
                        system path.
    @type grace_exe:    str
    """

    # Test the binary file string corresponds to a valid executable.
    test_binary(grace_exe)

    # File path.
    file_path = get_file_path(file, dir)

    # Run Grace.
    system(grace_exe + " \"" + file_path + "\" &")
