###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Module containing functions for the handling of chemical shifts."""


# Python module imports.
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoSequenceError
from lib.spectrum.peak_list import read_peak_list
from lib.warnings import RelaxNoSpinWarning
from pipe_control import pipes
from pipe_control.mol_res_spin import exists_mol_res_spin_data, generate_spin_id_unique, return_spin


def read(file=None, dir=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, spin_id=None, verbose=True):
    """Read the peak intensity data.

    @keyword file:          The name of the file containing the peak intensities.
    @type file:             str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @keyword spin_id_col:   The column containing the spin ID strings (used by the generic intensity file format).  If supplied, the mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col arguments must be none.
    @type spin_id_col:      int or None
    @keyword mol_name_col:  The column containing the molecule name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type mol_name_col:     int or None
    @keyword res_name_col:  The column containing the residue name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type res_name_col:     int or None
    @keyword res_num_col:   The column containing the residue number information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type res_num_col:      int or None
    @keyword spin_name_col: The column containing the spin name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type spin_name_col:    int or None
    @keyword spin_num_col:  The column containing the spin number information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
    @type spin_num_col:     int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all spins.  If 'auto' is provided for a NMRPipe seriesTab formatted file, the ID's are auto generated in form of Z_Ai.
    @type spin_id:          None or str
    @keyword verbose:       A flag which if True will cause all chemical shift data loaded to be printed out.
    @type verbose:          bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Check the file name.
    if file == None:
        raise RelaxError("The file name must be supplied.")

    # Read the peak list data.
    peak_list = read_peak_list(file=file, dir=dir, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id)

    # Loop over the assignments.
    data = []
    data_flag = False
    dim = peak_list._dim
    for assign in peak_list:
        # Loop over the dimensions of the peak list.
        for i in range(dim):
            # Generate the spin_id.
            spin_id = generate_spin_id_unique(res_num=assign.res_nums[i], spin_name=assign.spin_names[i])

            # Get the spin container.
            spin = return_spin(spin_id)
            if not spin:
                warn(RelaxNoSpinWarning(spin_id))
                continue

            # Skip deselected spins.
            if not spin.select:
                continue

            # Store the shift.
            spin.chemical_shift = assign.shifts[i]

            # Switch the flag.
            data_flag = True

            # Append the data for printing out.
            data.append([spin_id, repr(spin.chemical_shift)])

    # No data.
    if not data_flag:
        raise RelaxError("No chemical shifts could be loaded from the peak list")

    # Print out.
    if verbose:
        print("\nThe following chemical shifts have been loaded into the relax data store:\n")
        write_data(out=sys.stdout, headings=["Spin_ID", "Chemical shift"], data=data)


