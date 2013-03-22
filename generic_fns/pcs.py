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
"""Module for the manipulation of pseudo-contact shift data."""

# Python module imports.
from copy import deepcopy
from math import pi, sqrt
from numpy import array, float64, ones, std, zeros
from numpy.linalg import norm
from random import gauss
import sys
from warnings import warn

# relax module imports.
from generic_fns import grace, pipes
from generic_fns.align_tensor import get_tensor_index
from generic_fns.mol_res_spin import exists_mol_res_spin_data, generate_spin_id_unique, return_spin, spin_index_loop, spin_loop
from lib.nmr.pcs import ave_pcs_tensor, pcs_tensor
from target_functions.vectors import random_unit_vector
from lib.physical_constants import g1H, pcs_constant
from lib.errors import RelaxError, RelaxAlignError, RelaxNoAlignError, RelaxNoPdbError, RelaxNoPCSError, RelaxNoSequenceError, RelaxPCSError
from lib.io import open_write_file, read_spin_data, write_spin_data
from lib.warnings import RelaxWarning, RelaxNoSpinWarning


def back_calc(align_id=None):
    """Back calculate the PCS from the alignment tensor.

    @keyword align_id:      The alignment tensor ID string.
    @type align_id:         str
    """

    # Check the pipe setup.
    check_pipe_setup(pcs_id=align_id, sequence=True, N=True, tensors=True, paramag_centre=True)

    # Convert the align IDs to an array, or take all IDs.
    if align_id:
        align_ids = [align_id]
    else:
        align_ids = cdp.align_ids

    # Add the ID to the PCS IDs, if needed.
    for align_id in align_ids:
        # Init.
        if not hasattr(cdp, 'pcs_ids'):
            cdp.pcs_ids = []

        # Add the ID.
        if align_id not in cdp.pcs_ids:
            cdp.pcs_ids.append(align_id)

    # The weights.
    weights = ones(cdp.N, float64) / cdp.N

    # Unit vector data structure init.
    unit_vect = zeros((cdp.N, 3), float64)

    # Loop over the spins.
    count = 0
    for spin in spin_loop():
        # Skip spins with no position.
        if not hasattr(spin, 'pos'):
            continue

        # Atom positions.
        pos = spin.pos
        if type(pos[0]) in [float, float64]:
            pos = [pos] * cdp.N

        # Loop over the alignments.
        for id in align_ids:
            # Vectors.
            vect = zeros((cdp.N, 3), float64)
            r = zeros(cdp.N, float64)
            dj = zeros(cdp.N, float64)
            for c in range(cdp.N):
                # The vector.
                vect[c] = pos[c] - cdp.paramagnetic_centre

                # The length.
                r[c] = norm(vect[c])

                # Normalise (only if the vector has length).
                if r[c]:
                    vect[c] = vect[c] / r[c]

                # Calculate the PCS constant.
                dj[c] = pcs_constant(cdp.temperature[id], cdp.frq[id] * 2.0 * pi / g1H, r[c]/1e10)

            # Initialise if necessary.
            if not hasattr(spin, 'pcs_bc'):
                spin.pcs_bc = {}

            # Calculate the PCSs (in ppm).
            spin.pcs_bc[id] = ave_pcs_tensor(dj, vect, cdp.N, cdp.align_tensors[get_tensor_index(align_id=id)].A, weights=weights) * 1e6

        # Increment the counter.
        count += 1

    # No PCSs calculated.
    if not count:
        warn(RelaxWarning("No PCSs have been back calculated, probably due to missing spin position information."))


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

    # Check the pipe setup.
    check_pipe_setup(pipe=pipe)

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
            print("    [%8.3f, %8.3f, %8.3f]" % (pos[0], pos[1], pos[2]))
        print("\nAverage paramagnetic centre located at:")
        print("    [%8.3f, %8.3f, %8.3f]" % (centre[0], centre[1], centre[2]))

    # Set the centre (place it into the current data pipe).
    if ave_pos:
        if verbosity:
            print("\nUsing the average paramagnetic position.")
        cdp.paramagnetic_centre = centre
    else:
        if verbosity:
            print("\nUsing all paramagnetic positions.")
        cdp.paramagnetic_centre = full_pos_list


def check_pipe_setup(pipe=None, pcs_id=None, sequence=False, N=False, tensors=False, pcs=False, paramag_centre=False):
    """Check that the current data pipe has been setup sufficiently.

    @keyword pipe:              The data pipe to check, defaulting to the current pipe.
    @type pipe:                 None or str
    @keyword pcs_id:            The PCS ID string to check for in cdp.pcs_ids.
    @type pcs_id:               None or str
    @keyword sequence:          A flag which when True will invoke the sequence data check.
    @type sequence:             bool
    @keyword N:                 A flag which if True will check that cdp.N is set.
    @type N:                    bool
    @keyword tensors:           A flag which if True will check that alignment tensors exist.
    @type tensors:              bool
    @keyword pcs:               A flag which if True will check that PCSs exist.
    @type pcs:                  bool
    @keyword paramag_centre:    A flag which if True will check that the paramagnetic centre has been set.
    @type paramag_centre:       bool
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

    # Check for dp.N.
    if N and not hasattr(dp, 'N'):
        raise RelaxError("The number of states N has not been set.")

    # Check that alignment tensors are present.
    if tensors and (not hasattr(dp, 'align_tensors') or len(dp.align_tensors) == 0):
        raise RelaxNoTensorError('alignment')

    # Test for the alignment ID.
    if pcs_id and (not hasattr(dp, 'align_ids') or pcs_id not in dp.align_ids):
        raise RelaxNoAlignError(pcs_id, pipe)

    # Test if PCS data exists.
    if pcs and not hasattr(dp, 'align_ids'):
        raise RelaxNoAlignError()
    if pcs and not hasattr(dp, 'pcs_ids'):
        raise RelaxNoPCSError()
    elif pcs and pcs_id and pcs_id not in dp.pcs_ids:
        raise RelaxNoPCSError(pcs_id)

    # Test if the paramagnetic centre is set.
    if paramag_centre and not hasattr(cdp, 'paramagnetic_centre'):
        raise RelaxError("The paramagnetic centre has not been defined.")


def copy(pipe_from=None, pipe_to=None, align_id=None):
    """Copy the PCS data from one data pipe to another.

    @keyword pipe_from: The data pipe to copy the PCS data from.  This defaults to the current data pipe.
    @type pipe_from:    str
    @keyword pipe_to:   The data pipe to copy the PCS data to.  This defaults to the current data pipe.
    @type pipe_to:      str
    @param align_id:    The alignment ID string.
    @type align_id:     str
    """

    # Defaults.
    if pipe_from == None and pipe_to == None:
        raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")
    elif pipe_from == None:
        pipe_from = pipes.cdp_name()
    elif pipe_to == None:
        pipe_to = pipes.cdp_name()

    # Check the pipe setup.
    check_pipe_setup(pipe=pipe_from, pcs_id=align_id, sequence=True, pcs=True)
    check_pipe_setup(pipe=pipe_to, sequence=True)

    # Get the data pipes.
    dp_from = pipes.get_pipe(pipe_from)
    dp_to = pipes.get_pipe(pipe_to)

    # The IDs.
    if align_id == None:
        align_ids = dp_from.align_ids
    else:
        align_ids = [align_id]

    # Init target pipe global structures.
    if not hasattr(dp_to, 'align_ids'):
        dp_to.align_ids = []
    if not hasattr(dp_to, 'pcs_ids'):
        dp_to.pcs_ids = []

    # Loop over the align IDs.
    for align_id in align_ids:
        # Copy the global data.
        if align_id not in dp_to.align_ids and align_id not in dp_to.align_ids:
            dp_to.align_ids.append(align_id)
        if align_id in dp_from.pcs_ids and align_id not in dp_to.pcs_ids:
            dp_to.pcs_ids.append(align_id)

        # Spin loop.
        for mol_index, res_index, spin_index in spin_index_loop():
            # Alias the spin containers.
            spin_from = dp_from.mol[mol_index].res[res_index].spin[spin_index]
            spin_to = dp_to.mol[mol_index].res[res_index].spin[spin_index]

            # No data or errors.
            if (not hasattr(spin_from, 'pcs') or not align_id in spin_from.pcs) and (not hasattr(spin_from, 'pcs_err') or not align_id in spin_from.pcs_err):
                continue

            # Initialise the spin data if necessary.
            if hasattr(spin_from, 'pcs') and not hasattr(spin_to, 'pcs'):
                spin_to.pcs = {}
            if hasattr(spin_from, 'pcs_err') and not hasattr(spin_to, 'pcs_err'):
                spin_to.pcs_err = {}

            # Copy the value and error from pipe_from.
            if hasattr(spin_from, 'pcs'):
                spin_to.pcs[align_id] = spin_from.pcs[align_id]
            if hasattr(spin_from, 'pcs_err'):
                spin_to.pcs_err[align_id] = spin_from.pcs_err[align_id]


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

    # Check the pipe setup.
    check_pipe_setup(sequence=True)

    # Does PCS data exist?
    if not hasattr(cdp, 'pcs_ids') or not cdp.pcs_ids:
        warn(RelaxWarning("No PCS data exists, skipping file creation."))
        return

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Init.
    data = []

    # The diagonal.
    data.append([[-100, -100, 0], [100, 100, 0]])

    # The spin types.
    types = []
    for spin in spin_loop():
        if spin.element not in types:
            types.append(spin.element)

    # Loop over the PCS data.
    for align_id in cdp.pcs_ids:
        # Loop over the spin types.
        for i in range(len(types)):
            # Append a new list for this alignment.
            data.append([])

            # Errors present?
            err_flag = False
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Error present.
                if hasattr(spin, 'pcs_err') and align_id in spin.pcs_err.keys():
                    err_flag = True
                    break

            # Loop over the spins.
            for spin, spin_id in spin_loop(return_id=True):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Incorrect spin type.
                if spin.element != types[i]:
                    continue

                # Skip if data is missing.
                if not hasattr(spin, 'pcs') or not hasattr(spin, 'pcs_bc') or not align_id in spin.pcs.keys() or not align_id in spin.pcs_bc.keys():
                    continue

                # Append the data.
                data[-1].append([spin.pcs_bc[align_id], spin.pcs[align_id]])

                # Errors.
                if err_flag:
                    if hasattr(spin, 'pcs_err') and align_id in spin.pcs_err.keys():
                        data[-1][-1].append(spin.pcs_err[align_id])
                    else:
                        data[-1][-1].append(None)

                # Label.
                data[-1][-1].append(spin_id)

    # The data size.
    size = len(data)

    # Only one data set.
    data = [data]

    # Graph type.
    if err_flag:
        graph_type = 'xydy'
    else:
        graph_type = 'xy'

    # Grace file.
    if format == 'grace':
        # The set names.
        set_names = [None]
        for i in range(len(cdp.pcs_ids)):
            for j in range(len(types)):
                set_names.append("%s (%s)" % (cdp.pcs_ids[i], types[j]))

        # The header.
        grace.write_xy_header(file=file, title="PCS correlation plot", sets=size, set_names=set_names, linestyle=[2]+[0]*size, data_type=['pcs_bc', 'pcs'], axis_min=[-0.5, -0.5], axis_max=[0.5, 0.5], legend_pos=[1, 0.5])

        # The main data.
        grace.write_xy_data(data=data, file=file, graph_type=graph_type)


def delete(align_id=None):
    """Delete the PCS data corresponding to the alignment ID.

    @keyword align_id:  The alignment tensor ID string.  If not specified, all data will be deleted.
    @type align_id:     str or None
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, pcs_id=align_id, pcs=True)

    # The IDs.
    if not align_id:
        ids = deepcopy(cdp.pcs_ids)
    else:
        ids = [align_id]

    # Loop over the alignments, removing all the corresponding data.
    for id in ids:
        # The PCS ID.
        cdp.pcs_ids.pop(cdp.pcs_ids.index(id))

        # The data type.
        if hasattr(cdp, 'pcs_data_types') and id in cdp.pcs_data_types:
            cdp.pcs_data_types.pop(id)

        # The spin data.
        for spin in spin_loop():
            # The data.
            if hasattr(spin, 'pcs') and id in spin.pcs:
                spin.pcs.pop(id)

            # The error.
            if hasattr(spin, 'pcs_err') and id in spin.pcs_err:
                spin.pcs_err.pop(id)

        # Clean the global data.
        if not hasattr(cdp, 'rdc_ids') or id not in cdp.rdc_ids:
            cdp.align_ids.pop(cdp.align_ids.index(id))


def display(align_id=None, bc=False):
    """Display the PCS data corresponding to the alignment ID.

    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    @keyword bc:        The back-calculation flag which if True will cause the back-calculated rather than measured data to be displayed.
    @type bc:           bool
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, pcs_id=align_id, pcs=True)

    # Call the write method with sys.stdout as the file.
    write(align_id=align_id, file=sys.stdout, bc=bc)


def q_factors(spin_id=None):
    """Calculate the Q-factors for the PCS data.

    @keyword spin_id:   The spin ID string used to restrict the Q-factor calculation to a subset of all spins.
    @type spin_id:      None or str
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True)

    # No PCSs, so no Q factors can be calculated.
    if not hasattr(cdp, 'pcs_ids') or not len(cdp.pcs_ids):
        warn(RelaxWarning("No PCS data exists, Q factors cannot be calculated."))
        return

    # Q-factor dictionary.
    cdp.q_factors_pcs = {}

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
            if hasattr(spin, 'pcs') and align_id in spin.pcs:
                pcs_data = True
            if hasattr(spin, 'pcs_bc') and align_id in spin.pcs_bc:
                pcs_bc_data = True

            # Skip spins without PCS data.
            if not hasattr(spin, 'pcs') or not hasattr(spin, 'pcs_bc') or not align_id in spin.pcs or spin.pcs[align_id] == None or not align_id in spin.pcs_bc or spin.pcs_bc[align_id] == None:
                continue

            # Sum of squares.
            sse = sse + (spin.pcs[align_id] - spin.pcs_bc[align_id])**2

            # Sum the PCSs squared (for normalisation).
            pcs2_sum = pcs2_sum + spin.pcs[align_id]**2

        # The Q-factor for the alignment.
        if pcs2_sum:
            Q = sqrt(sse / pcs2_sum)
            cdp.q_factors_pcs[align_id] = Q

        # Warnings (and then exit).
        if not spin_count:
            warn(RelaxWarning("No spins have been used in the calculation, skipping the PCS Q factor calculation."))
            return
        if not pcs_data:
            warn(RelaxWarning("No PCS data can be found for the alignment ID '%s', skipping the PCS Q factor calculation for this alignment." % align_id))
            continue
        if not pcs_bc_data:
            warn(RelaxWarning("No back-calculated PCS data can be found for the alignment ID '%s', skipping the PCS Q factor calculation for this alignment." % align_id))
            continue

    # The total Q-factor.
    cdp.q_pcs = 0.0
    for id in cdp.q_factors_pcs:
        cdp.q_pcs = cdp.q_pcs + cdp.q_factors_pcs[id]**2
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

    # Check the pipe setup.
    check_pipe_setup(sequence=True)

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Either the data or error column must be supplied.
    if data_col == None and error_col == None:
        raise RelaxError("One of either the data or error column must be supplied.")


    # Spin specific data.
    #####################

    # Loop over the PCS data.
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []
    values = []
    errors = []
    for data in read_spin_data(file=file, dir=dir, file_data=file_data, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep, spin_id=spin_id):
        # Unpack.
        if data_col and error_col:
            mol_name, res_num, res_name, spin_num, spin_name, value, error = data
        elif data_col:
            mol_name, res_num, res_name, spin_num, spin_name, value = data
            error = None
        else:
            mol_name, res_num, res_name, spin_num, spin_name, error = data
            value = None

        # Test the error value (cannot be 0.0).
        if error == 0.0:
            raise RelaxError("An invalid error value of zero has been encountered.")

        # Get the corresponding spin container.
        id = generate_spin_id_unique(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin_num, spin_name=spin_name)
        spin = return_spin(id)
        if spin == None and spin_id[0] == '@':    # Allow spin IDs of atom names to be used to specify multi column data.
            spin = return_spin(id+spin_id)
        if spin == None:
            warn(RelaxNoSpinWarning(id))
            continue

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

        # Append the data for printout.
        mol_names.append(mol_name)
        res_nums.append(res_num)
        res_names.append(res_name)
        spin_nums.append(spin_num)
        spin_names.append(spin_name)
        values.append(value)
        errors.append(error)

    # Print out.
    write_spin_data(file=sys.stdout, mol_names=mol_names, res_nums=res_nums, res_names=res_names, spin_nums=spin_nums, spin_names=spin_names, data=values, data_name='PCSs', error=errors, error_name='PCS_error')


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


def set_errors(align_id=None, spin_id=None, sd=None):
    """Set the PCS errors if not already present.

    @keyword align_id:  The optional alignment tensor ID string.
    @type align_id:     str
    @keyword spin_id:   The optional spin ID string.
    @type spin_id:      None or str
    @keyword sd:        The PCS standard deviation in ppm.
    @type sd:           float or int.
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, pcs_id=align_id, pcs=True)

    # Convert the align IDs to an array, or take all IDs.
    if align_id:
        align_ids = [align_id]
    else:
        align_ids = cdp.pcs_ids

    # Loop over the spins.
    for spin in spin_loop(spin_id):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Skip spins with no PCSs.
        if not hasattr(spin, 'pcs') or (align_id and not align_id in spin.pcs):
            continue

        # No data structure.
        if not hasattr(spin, 'pcs_err'):
            spin.pcs_err = {}

        # Set the error.
        for id in align_ids:
            spin.pcs_err[id] = sd


def structural_noise(align_id=None, rmsd=0.2, sim_num=1000, file=None, dir=None, force=False):
    """Determine the PCS error due to structural noise via simulation.

    For the simulation the following must already be set up in the current data pipe:

        - The position of the paramagnetic centre.
        - The alignment and magnetic susceptibility tensor.

    The protocol for the simulation is as follows:

        - The lanthanide or paramagnetic centre position will be fixed.  Its motion is assumed to be on the femto- to pico- and nanosecond timescales.  Hence the motion is averaged over the evolution of the PCS and can be ignored.
        - The positions of the nuclear spins will be randomised N times.  For each simulation a random unit vector will be generated.  Then a random distance along the unit vector will be generated by sampling from a Gaussian distribution centered at zero, the original spin position, with a standard deviation set to the given RMSD.  Both positive and negative displacements will be used.
        - The PCS for the randomised position will be back calculated.
        - The PCS standard deviation will be calculated from the N randomised PCS values.

    The standard deviation will both be stored in the spin container data structure in the relax data store as well as being added to the already present PCS error (using variance addition).  This will then be used in any optimisations involving the PCS.

    If the alignment ID string is not supplied, the procedure will be applied to the PCS data from all alignments.


    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    @keyword rmsd:      The atomic position RMSD, in Angstrom, to randomise the spin positions with for the simulations.
    @type rmsd:         float
    @keyword sim_num:   The number of simulations, N, to perform to determine the structural noise component of the PCS errors.
    @type sim_num:      int
    @keyword file:      The optional name of the Grace file to plot the structural errors verses the paramagnetic centre to spin distances.
    @type file:         None or str
    @keyword dir:       The directory name to place the Grace file into.
    @type dir:          None or str
    @keyword force:     A flag which if True will cause any pre-existing file to be overwritten.
    @type force:        bool
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, pcs_id=align_id, pcs=True, paramag_centre=True)

    # Convert the align IDs to an array, or take all IDs.
    if align_id:
        align_ids = [align_id]
    else:
        align_ids = cdp.align_ids

    # Initialise some numpy data structures for use in the simulations.
    grace_data = []
    unit_vect = zeros(3, float64)
    pcs = {}
    for id in align_ids:
        grace_data.append([])
        pcs[id] = zeros(sim_num, float64)

    # Print out.
    print("Executing %i simulations for each spin system." % sim_num)

    # Loop over the spins.
    for spin, spin_id in spin_loop(return_id=True):
        # Deselected spins.
        if not spin.select:
            continue

        # Skip spins with no PCS or position.
        if not hasattr(spin, 'pcs'):
            continue
        if not hasattr(spin, 'pos'):
            continue

        # Print out.
        print(spin_id)

        # Average the atom position.
        if type(spin.pos[0]) in [float, float64]:
            pos = spin.pos
        else:
            pos = zeros(3, float64)
            for i in range(len(spin.pos)):
                pos += spin.pos[i]
            pos = pos / len(spin.pos)

        # The original vector length (for the Grace plot).
        orig_vect = pos - cdp.paramagnetic_centre
        orig_r = norm(orig_vect)

        # Loop over the N randomisations.
        for i in range(sim_num):
            # The random unit vector.
            random_unit_vector(unit_vect)

            # The random displacement (in Angstrom).
            disp = gauss(0, rmsd)

            # Move the atom.
            new_pos = pos + disp*unit_vect

            # The vector and length.
            vect = new_pos - cdp.paramagnetic_centre
            r = norm(vect)
            vect = vect / r

            # Loop over the alignments.
            for id in align_ids:
                # No PCS value, so skip.
                if id not in spin.pcs:
                    continue

                # Calculate the PCS constant.
                dj = pcs_constant(cdp.temperature[id], cdp.frq[id] * 2.0 * pi / g1H, r/1e10)

                # Calculate the PCS value (in ppm).
                pcs[id][i] = pcs_tensor(dj, vect, cdp.align_tensors[get_tensor_index(id)].A) * 1e6

        # Initialise if necessary.
        if not hasattr(spin, 'pcs_struct_err'):
            spin.pcs_struct_err = {}

        # Loop over the alignments.
        align_index = 0
        for id in align_ids:
            # No PCS value, so skip.
            if id not in spin.pcs:
                align_index += 1
                continue

            # The PCS standard deviation.
            sd = std(pcs[id])

            # Remove the previous error.
            if id in spin.pcs_struct_err:
                warn(RelaxWarning("Removing the previous structural error value from the PCS error of the spin '%s' for the alignment ID '%s'." % (spin_id, id)))
                spin.pcs_err[id] = sqrt(spin.pcs_err[id]**2 - spin.pcs_struct_err[id]**2)

            # Store the structural error.
            spin.pcs_struct_err[id] = sd

            # Add it to the PCS error (with variance addition).
            spin.pcs_err[id] = sqrt(spin.pcs_err[id]**2 + sd**2)

            # Store the data for the Grace plot.
            grace_data[align_index].append([orig_r, sd])

            # Increment the alignment index.
            align_index += 1

    # The Grace output.
    if file:
        # Open the Grace file for writing.
        file = open_write_file(file, dir, force)

        # The header.
        grace.write_xy_header(file=file, title="PCS structural noise", subtitle="%s Angstrom structural noise"%rmsd, sets=len(align_ids), set_names=align_ids, symbol_sizes=[0.5]*len(align_ids), linetype=[0]*len(align_ids), data_type=['pcs_bc', 'pcs'], axis_labels=["Ln\\S3+\\N to spin distance (Angstrom)", "PCS standard deviation (ppm)"])

        # The main data.
        grace.write_xy_data(data=[grace_data], file=file, graph_type='xy')


def weight(align_id=None, spin_id=None, weight=1.0):
    """Set optimisation weights on the PCS data.

    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    @keyword spin_id:   The spin ID string.
    @type spin_id:      None or str
    @keyword weight:    The optimisation weight.  The higher the value, the more importance the PCS will have.
    @type weight:       float or int.
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, pcs_id=align_id, pcs=True)

    # Loop over the spins.
    for spin in spin_loop(spin_id):
        # No data structure.
        if not hasattr(spin, 'pcs_weight'):
            spin.pcs_weight = {}

        # Set the weight.
        spin.pcs_weight[align_id] = weight


def write(align_id=None, file=None, dir=None, bc=False, force=False):
    """Display the PCS data corresponding to the alignment ID.

    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    @keyword file:      The file name or object to write to.
    @type file:         str or file object
    @keyword dir:       The name of the directory to place the file into (defaults to the current directory).
    @type dir:          str
    @keyword bc:        The back-calculation flag which if True will cause the back-calculated rather than measured data to be written.
    @type bc:           bool
    @keyword force:     A flag which if True will cause any pre-existing file to be overwritten.
    @type force:        bool
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, pcs_id=align_id, pcs=True)

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Loop over the spins and collect the data.
    mol_names = []
    res_nums = []
    res_names = []
    spin_nums = []
    spin_names = []
    values = []
    errors = []
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Skip spins with no PCSs.
        if not bc and (not hasattr(spin, 'pcs') or not align_id in spin.pcs.keys()):
            continue
        elif bc and (not hasattr(spin, 'pcs_bc') or align_id not in spin.pcs_bc.keys()):
            continue

        # Append the spin data.
        mol_names.append(mol_name)
        res_nums.append(res_num)
        res_names.append(res_name)
        spin_nums.append(spin.num)
        spin_names.append(spin.name)

        # The value.
        if bc:
            values.append(spin.pcs_bc[align_id])
        else:
            values.append(spin.pcs[align_id])

        # The error.
        if hasattr(spin, 'pcs_err') and align_id in spin.pcs_err.keys():
            errors.append(spin.pcs_err[align_id])
        else:
            errors.append(None)

    # Write out.
    write_spin_data(file=file, mol_names=mol_names, res_nums=res_nums, res_names=res_names, spin_nums=spin_nums, spin_names=spin_names, data=values, data_name='PCSs', error=errors, error_name='PCS_error')
