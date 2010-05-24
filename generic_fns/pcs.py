###############################################################################
#                                                                             #
# Copyright (C) 2003-2010 Edward d'Auvergne                                   #
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
"""Module for the manipulation of pseudocontact shift data."""

# Python module imports.
from math import sqrt
from numpy import array, float64, zeros
import sys
from warnings import warn

# relax module imports.
from generic_fns import grace, pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from relax_errors import RelaxError, RelaxNoPdbError, RelaxNoSequenceError, RelaxNoSpinError
from relax_io import open_write_file, read_spin_data, write_spin_data
from relax_warnings import RelaxWarning


def centre(pos=None, atom_id=None, pipe=None, verbosity=1, ave_pos=False, force=False):
    """Specify the atom in the loaded structure corresponding to the paramagnetic centre.

    @keyword pos:       The atomic position.  If set, the atom_id string will be ignored.
    @type pos:          list of float
    @keyword atom_id:   The atom identification string.
    @type atom_id:      str
    @keyword pipe:      An alternative data pipe to extract the paramagnetic centre from.
    @type pipe:         None or str
    @keyword verbosity: The amount of information to print out.  The bigger the number, the more information.
    @type verbosity:    int
    @keyword ave_pos:   A flag which if True causes the atomic positions from multiple models to be averaged.
    @type ave_pos:      bool
    @keyword force:     A flag which if True will cause the current PCS centre to be overwritten.
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Test the data pipe.
    pipes.test(pipe)

    # Get the data pipes.
    source_dp = pipes.get_pipe(pipe)

    # Test if the structure has been loaded.
    if not hasattr(source_dp, 'structure'):
        raise RelaxNoPdbError

    # Test the centre has already been set.
    if not force and hasattr(cdp, 'paramagnetic_centre'):
        raise RelaxError("The paramagnetic centre has already been set to the coordinates " + repr(cdp.paramagnetic_centre) + ".")

    # Position is supplied.
    if pos != None:
        centre = array(pos)
        num_pos = 1
        full_pos_list = []

    # Position from a loaded structure.
    else:
        # Get the positions.
        centre = zeros(3, float64)
        full_pos_list = []
        num_pos = 0
        for spin, spin_id in spin_loop(atom_id, pipe=pipe, return_id=True):
            # No atomic positions.
            if not hasattr(spin, 'pos'):
                continue
    
            # Spin position list.
            if isinstance(spin.pos[0], float) or isinstance(spin.pos[0], float64):
                pos_list = [spin.pos]
            else:
                pos_list = spin.pos
    
            # Loop over the model positions.
            for pos in pos_list:
                full_pos_list.append(pos)
                centre = centre + array(pos)
                num_pos = num_pos + 1
    
        # No positional information!
        if not num_pos:
            raise RelaxError("No positional information could be found for the spin '%s'." % atom_id)

    # Averaging.
    centre = centre / float(num_pos)

    # Print out.
    if verbosity:
        print("Paramagnetic centres located at:")
        for pos in full_pos_list:
            print(("    [%8.3f, %8.3f, %8.3f]" % (pos[0], pos[1], pos[2])))
        print("\nAverage paramagnetic centre located at:")
        print(("    [%8.3f, %8.3f, %8.3f]" % (centre[0], centre[1], centre[2])))

    # Set the centre (place it into the current data pipe).
    if ave_pos:
        if verbosity:
            print("\nUsing the average paramagnetic position.")
        cdp.paramagnetic_centre = centre
    else:
        if verbosity:
            print("\nUsing all paramagnetic positions.")
        cdp.paramagnetic_centre = full_pos_list


def corr_plot(format=None, file=None, dir=None, force=False):
    """Generate a correlation plot of the measured vs. back-calculated PCSs.

    @keyword format:    The format for the plot file.  The following values are accepted: 'grace', a Grace plot; None, a plain text file.
    @type format:       str or None
    @keyword file:      The file name or object to write to.
    @type file:         str or file object
    @keyword dir:       The name of the directory to place the file into (defaults to the current directory).
    @type dir:          str
    @keyword force:     A flag which if True will cause any pre-existing file to be overwritten.
    @type force:        bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Does PCS data exist?
    if not hasattr(cdp, 'pcs_ids') or not cdp.pcs_ids:
        warn(RelaxWarning("No PCS data exists, skipping file creation."))
        return

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Init.
    data = []

    # The diagonal.
    data.append([[-100, -100], [100, 100]])

    # Loop over the PCS data.
    for align_id in cdp.pcs_ids:
        # Append a new list for this alignment.
        data.append([])

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip if data is missing.
            if not hasattr(spin, 'pcs') or not hasattr(spin, 'pcs_bc') or not align_id in spin.pcs.keys() or not align_id in spin.pcs_bc.keys():
                continue

            # Append the data.
            data[-1].append([spin.pcs[align_id], spin.pcs_bc[align_id], spin_id])

    # The data size.
    size = len(data)

    # Only one data set.
    data = [data]

    # Grace file.
    if format == 'grace':
        # The header.
        grace.write_xy_header(file=file, title="PCS correlation plot", sets=size, set_names=[None]+cdp.pcs_ids, linestyle=[2]+[0]*size, data_type=['pcs', 'pcs_bc'], axis_min=[-0.5, -0.5], axis_max=[0.5, 0.5], legend_pos=[1, 0.5])

        # The main data.
        grace.write_xy_data(data=data, file=file, graph_type='xy')


def display(align_id=None):
    """Display the PCS data corresponding to the alignment ID.

    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    """

    # Call the write method with sys.stdout as the file.
    write(align_id=align_id, file=sys.stdout)


def q_factors(spin_id=None):
    """Calculate the Q-factors for the PCS data.

    @keyword spin_id:   The spin ID string used to restrict the Q-factor calculation to a subset of all spins.
    @type spin_id:      None or str
    """

    # Q-factor list.
    cdp.q_factors_pcs = []

    # Loop over the alignments.
    for align_id in cdp.pcs_ids:
        # Init.
        pcs2_sum = 0.0
        sse = 0.0

        # Spin loop.
        spin_count = 0
        pcs_data = False
        pcs_bc_data = False
        for spin in spin_loop(spin_id):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Increment the spin counter.
            spin_count += 1

            # Data checks.
            if hasattr(spin, 'pcs'):
                pcs_data = True
            if hasattr(spin, 'pcs_bc'):
                pcs_bc_data = True

            # Skip spins without PCS data.
            if not hasattr(spin, 'pcs') or not hasattr(spin, 'pcs_bc') or align_id not in spin.pcs.keys() or spin.pcs[align_id] == None:
                continue

            # Sum of squares.
            sse = sse + (spin.pcs[align_id] - spin.pcs_bc[align_id])**2

            # Sum the PCSs squared (for normalisation).
            pcs2_sum = pcs2_sum + spin.pcs[align_id]**2

        # The Q-factor for the alignment.
        Q = sqrt(sse / pcs2_sum)
        cdp.q_factors_pcs.append(Q)

        # Warnings (and then exit).
        if not spin_count:
            warn(RelaxWarning("No spins have been used in the calculation."))
            return
        if not pcs_data:
            warn(RelaxWarning("No PCS data can be found."))
            return
        if not pcs_bc_data:
            warn(RelaxWarning("No back-calculated PCS data can be found."))
            return

    # The total Q-factor.
    cdp.q_pcs = 0.0
    for Q in cdp.q_factors_pcs:
        cdp.q_pcs = cdp.q_pcs + Q**2
    cdp.q_pcs = cdp.q_pcs / len(cdp.q_factors_pcs)
    cdp.q_pcs = sqrt(cdp.q_pcs)


def read(align_id=None, file=None, dir=None, file_data=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None, spin_id=None):
    """Read the PCS data from file.

    @param align_id:        The alignment tensor ID string.
    @type align_id:         str
    @param file:            The name of the file to open.
    @type file:             str
    @param dir:             The directory containing the file (defaults to the current directory if None).
    @type dir:              str or None
    @param file_data:       An alternative opening a file, if the data already exists in the correct format.  The format is a list of lists where the first index corresponds to the row and the second the column.
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
    @keyword data_col:      The column containing the PCS data in Hz.
    @type data_col:         int or None
    @keyword error_col:     The column containing the PCS errors.
    @type error_col:        int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all spins.
    @type spin_id:          None or str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Either the data or error column must be supplied.
    if data_col == None and error_col == None:
        raise RelaxError("One of either the data or error column must be supplied.")


    # Spin specific data.
    #####################

    # Loop over the PCS data.
    spin_ids = []
    values = []
    errors = []
    for data in read_spin_data(file=file, dir=dir, file_data=file_data, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep, spin_id=spin_id):
        # Unpack.
        if data_col and error_col:
            id, value, error = data
        elif data_col:
            id, value = data
            error = None
        else:
            id, error = data
            value = None

        # Test the error value (cannot be 0.0).
        if error == 0.0:
            raise RelaxError("An invalid error value of zero has been encountered.")

        # Get the corresponding spin container.
        spin = return_spin([id, spin_id])
        if spin == None:
            raise RelaxNoSpinError(id)

        # Add the data.
        if data_col:
            # Initialise.
            if not hasattr(spin, 'pcs'):
                spin.pcs = {}

            # Append the value.
            spin.pcs[align_id] = value

        # Add the error.
        if error_col:
            # Initialise.
            if not hasattr(spin, 'pcs_err'):
                spin.pcs_err = {}

            # Append the error.
            spin.pcs_err[align_id] = error

        # Append the data for print out.
        spin_ids.append(id)
        values.append(value)
        errors.append(error)

    # Print out.
    write_spin_data(file=sys.stdout, spin_ids=spin_ids, data=values, data_name='PCSs', error=errors, error_name='PCS_error')


    # Global (non-spin specific) data.
    ##################################

    # No data, so return.
    if not len(values):
        return

    # Initialise.
    if not hasattr(cdp, 'align_ids'):
        cdp.align_ids = []
    if not hasattr(cdp, 'pcs_ids'):
        cdp.pcs_ids = []

    # Add the PCS id string.
    if align_id not in cdp.align_ids:
        cdp.align_ids.append(align_id)
    if align_id not in cdp.pcs_ids:
        cdp.pcs_ids.append(align_id)


def write(align_id=None, file=None, dir=None, force=False):
    """Display the PCS data corresponding to the alignment ID.

    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    @keyword file:      The file name or object to write to.
    @type file:         str or file object
    @keyword dir:       The name of the directory to place the file into (defaults to the current directory).
    @type dir:          str
    @keyword force:     A flag which if True will cause any pre-existing file to be overwritten.
    @type force:        bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data corresponding to 'align_id' exists.
    if not hasattr(cdp, 'pcs_ids') or align_id not in cdp.pcs_ids:
        raise RelaxNoPCSError(align_id)

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Loop over the spins and collect the data.
    spin_ids = []
    values = []
    errors = []
    for spin, spin_id in spin_loop(return_id=True):
        # Skip spins with no PCSs.
        if not hasattr(spin, 'pcs') or not align_id in spin.pcs.keys():
            continue

        # Store the data.
        spin_ids.append(spin_id)
        values.append(spin.pcs[align_id])
        if hasattr(spin, 'pcs_err') and align_id in spin.pcs_err.keys():
            errors.append(spin.pcs_err[align_id])
        else:
            errors.append(None)

    # Write out.
    write_spin_data(file=file, spin_ids=spin_ids, data=values, data_name='PCSs', error=errors, error_name='PCS_error')
