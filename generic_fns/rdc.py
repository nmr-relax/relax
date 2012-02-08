###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Module for the manipulation of RDC data."""

# Python module imports.
from copy import deepcopy
from math import pi, sqrt
from numpy import float64, ones, zeros
from numpy.linalg import norm
import sys
from warnings import warn

# relax module imports.
from float import nan
from generic_fns import grace, pipes
from generic_fns.align_tensor import get_tensor_index
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from maths_fns.rdc import ave_rdc_tensor
from physical_constants import dipolar_constant, return_gyromagnetic_ratio
from relax_errors import RelaxError, RelaxNoRDCError, RelaxNoSequenceError, RelaxSpinTypeError
from relax_io import open_write_file, read_spin_data, write_spin_data
from relax_warnings import RelaxWarning, RelaxNoSpinWarning


def back_calc(align_id=None):
    """Back calculate the RDC from the alignment tensor and unit bond vectors.

    @keyword align_id:      The alignment tensor ID string.
    @type align_id:         str
    """

    # Arg check.
    if align_id and align_id not in cdp.align_ids:
        raise RelaxError, "The alignment ID '%s' is not in the alignment ID list %s." % (align_id, cdp.align_ids)

    # Convert the align IDs to an array, or take all IDs.
    if align_id:
        align_ids = [align_id]
    else:
        align_ids = cdp.align_ids

    # Add the ID to the RDC IDs, if needed.
    for align_id in align_ids:
        # Init.
        if not hasattr(cdp, 'rdc_ids'):
            cdp.rdc_ids = []

        # Add the ID.
        if align_id not in cdp.rdc_ids:
            cdp.rdc_ids.append(align_id)

    # The weights.
    weights = ones(cdp.N, float64) / cdp.N

    # Unit vector data structure init.
    unit_vect = zeros((cdp.N, 3), float64)

    # Loop over the spins.
    for spin in spin_loop():
        # Skip spins with no bond vectors.
        if not hasattr(spin, 'bond_vect') and not hasattr(spin, 'xh_vect'):
            continue

        # Check.
        if not hasattr(spin, 'heteronuc_type'):
            raise RelaxSpinTypeError

        # Alias.
        if hasattr(spin, 'bond_vect'):
            vectors = spin.bond_vect
        else:
            vectors = spin.xh_vect

        # Single vector.
        if type(vectors[0]) in [float, float64]:
            vectors = [vectors]

        # Gyromagnetic ratios.
        gx = return_gyromagnetic_ratio(spin.heteronuc_type)
        gh = return_gyromagnetic_ratio(spin.proton_type)

        # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
        dj = 3.0/(2.0*pi) * dipolar_constant(gx, gh, spin.r)

        # Unit vectors.
        for c in range(cdp.N):
            unit_vect[c] = vectors[c] / norm(vectors[c])

        # Initialise if necessary.
        if not hasattr(spin, 'rdc_bc'):
            spin.rdc_bc = {}

        # Calculate the RDCs.
        for id in align_ids:
            spin.rdc_bc[id] = ave_rdc_tensor(dj, unit_vect, cdp.N, cdp.align_tensors[get_tensor_index(align_id=id)].A, weights=weights)


def convert(value, align_id, to_intern=False):
    """Convert the RDC based on the 'D' or '2D' data type.

    @param value:           The value or error to convert.
    @type value:            float or None
    @param align_id:        The alignment tensor ID string.
    @type align_id:         str
    @keyword to_intern:     A flag which if True will convert to the internal D notation if needed, or if False will convert from the internal D notation to the external D or 2D format.
    @type to_intern:        bool
    @return:                The converted value.
    @rtype:                 float or None
    """

    # Handle values of None.
    if value == None:
        return None

    # The conversion factor.
    factor = 1.0
    if hasattr(cdp, 'rdc_data_types') and cdp.rdc_data_types.has_key(align_id) and cdp.rdc_data_types[align_id] == '2D':
        # Convert from 2D to D.
        if to_intern:
            factor = 2.0

        # Convert from D to 2D.
        else:
            factor = 0.5

    # Return the converted value.
    return value * factor


def corr_plot(format=None, file=None, dir=None, force=False):
    """Generate a correlation plot of the measured vs. back-calculated RDCs.

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

    # Does RDC data exist?
    if not hasattr(cdp, 'rdc_ids') or not cdp.rdc_ids:
        warn(RelaxWarning("No RDC data exists, skipping file creation."))
        return

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Init.
    data = []

    # The diagonal.
    data.append([[-100, -100, 0], [100, 100, 0]])

    # Loop over the RDC data.
    for align_id in cdp.rdc_ids:
        # Append a new list for this alignment.
        data.append([])

        # Errors present?
        err_flag = False
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Error present.
            if hasattr(spin, 'rdc_err') and align_id in spin.rdc_err.keys():
                err_flag = True
                break

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip if data is missing.
            if not hasattr(spin, 'rdc') or not hasattr(spin, 'rdc_bc') or not align_id in spin.rdc.keys() or not align_id in spin.rdc_bc.keys():
                continue

            # Append the data.
            data[-1].append([convert(spin.rdc_bc[align_id], align_id), convert(spin.rdc[align_id], align_id)])

            # Errors.
            if err_flag:
                if hasattr(spin, 'rdc_err') and align_id in spin.rdc_err.keys():
                    data[-1][-1].append(convert(spin.rdc_err[align_id], align_id))
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
        # The header.
        grace.write_xy_header(file=file, title="RDC correlation plot", sets=size, set_names=[None]+cdp.rdc_ids, linestyle=[2]+[0]*size, data_type=['rdc_bc', 'rdc'], axis_min=[-10, -10], axis_max=[10, 10], legend_pos=[1, 0.5])

        # The main data.
        grace.write_xy_data(data=data, file=file, graph_type=graph_type)


def delete(align_id=None):
    """Delete the RDC data corresponding to the alignment ID.

    @keyword align_id:  The alignment tensor ID string.  If not specified, all data will be deleted.
    @type align_id:     str or None
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Check that the ID exists.
    if align_id and not align_id in cdp.rdc_ids:
        raise RelaxError("The RDC alignment id '%s' does not exist" % align_id)

    # The IDs.
    if not align_id:
        ids = deepcopy(cdp.rdc_ids)
    else:
        ids = [align_id]

    # Loop over the alignments, removing all the corresponding data.
    for id in ids:
        # The RDC ID.
        cdp.rdc_ids.pop(cdp.rdc_ids.index(id))

        # The data type.
        if hasattr(cdp, 'rdc_data_types') and cdp.rdc_data_types.has_key(id):
            cdp.rdc_data_types.pop(id)

        # The spin data.
        for spin in spin_loop():
            # The data.
            if hasattr(spin, 'rdc') and spin.rdc.has_key(id):
                spin.rdc.pop(id)

            # The error.
            if hasattr(spin, 'rdc_err') and spin.rdc_err.has_key(id):
                spin.rdc_err.pop(id)

        # Clean the global data.
        if not hasattr(cdp, 'pcs_ids') or id not in cdp.pcs_ids:
            cdp.align_ids.pop(id)


def display(align_id=None, bc=False):
    """Display the RDC data corresponding to the alignment ID.

    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    @keyword bc:        The back-calculation flag which if True will cause the back-calculated rather than measured data to be displayed.
    @type bc:           bool
    """

    # Call the write method with sys.stdout as the file.
    write(align_id=align_id, file=sys.stdout, bc=bc)


def q_factors(spin_id=None):
    """Calculate the Q-factors for the RDC data.

    @keyword spin_id:   The spin ID string used to restrict the Q-factor calculation to a subset of all spins.
    @type spin_id:      None or str
    """

    # No RDCs, so no Q factors can be calculated.
    if not hasattr(cdp, 'rdc_ids') or not len(cdp.rdc_ids):
        warn(RelaxWarning("No RDC data exists, Q factors cannot be calculated."))
        return

    # Q-factor dictonaries.
    cdp.q_factors_rdc = {}
    cdp.q_factors_rdc_norm2 = {}

    # Loop over the alignments.
    for align_id in cdp.rdc_ids:
        # Init.
        D2_sum = 0.0
        sse = 0.0

        # Spin loop.
        dj = None
        N = 0
        spin_count = 0
        rdc_data = False
        rdc_bc_data = False
        for spin in spin_loop(spin_id):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Increment the spin counter.
            spin_count += 1

            # Data checks.
            if hasattr(spin, 'rdc') and spin.rdc.has_key(align_id):
                rdc_data = True
            if hasattr(spin, 'rdc_bc') and spin.rdc_bc.has_key(align_id):
                rdc_bc_data = True

            # Skip spins without RDC data.
            if not hasattr(spin, 'rdc') or not hasattr(spin, 'rdc_bc') or not spin.rdc.has_key(align_id) or spin.rdc[align_id] == None or not spin.rdc_bc.has_key(align_id) or spin.rdc_bc[align_id] == None:
                continue

            # Sum of squares.
            sse = sse + (spin.rdc[align_id] - spin.rdc_bc[align_id])**2

            # Sum the RDCs squared (for one type of normalisation).
            D2_sum = D2_sum + spin.rdc[align_id]**2

            # Gyromagnetic ratios.
            gx = return_gyromagnetic_ratio(spin.heteronuc_type)
            gh = return_gyromagnetic_ratio(spin.proton_type)

            # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
            dj_new = 3.0/(2.0*pi) * dipolar_constant(gx, gh, spin.r)
            if dj and dj_new != dj:
                raise RelaxError("All the RDCs must come from the same nucleus type.")
            else:
                dj = dj_new

            # Increment the number of data sets.
            N = N + 1

        # Warnings (and then exit).
        if not spin_count:
            warn(RelaxWarning("No spins have been used in the calculation."))
            return
        if not rdc_data:
            warn(RelaxWarning("No RDC data can be found."))
            return
        if not rdc_bc_data:
            warn(RelaxWarning("No back-calculated RDC data can be found."))
            return

        # Normalisation factor of 2Da^2(4 + 3R)/5.
        D = dj * cdp.align_tensors[cdp.align_ids.index(align_id)].A_diag
        Da = 1.0/3.0 * (D[2, 2] - (D[0, 0]+D[1, 1])/2.0)
        Dr = 1.0/3.0 * (D[0, 0] - D[1, 1])
        if Da == 0:
            R = nan
        else:
            R = Dr / Da
        norm = 2.0 * (Da)**2 * (4.0 + 3.0*R**2)/5.0
        if Da == 0.0:
            norm = 1e-15

        # The Q-factor for the alignment.
        Q = sqrt(sse / N / norm)
        cdp.q_factors_rdc[align_id] = Q
        cdp.q_factors_rdc_norm2[align_id] = sqrt(sse / D2_sum)

    # The total Q-factor.
    cdp.q_rdc = 0.0
    cdp.q_rdc_norm2 = 0.0
    for id in cdp.q_factors_rdc:
        cdp.q_rdc = cdp.q_rdc + cdp.q_factors_rdc[id]**2
    for id in cdp.q_factors_rdc_norm2:
        cdp.q_rdc_norm2 = cdp.q_rdc_norm2 + cdp.q_factors_rdc_norm2[id]**2
    cdp.q_rdc = sqrt(cdp.q_rdc / len(cdp.q_factors_rdc))
    cdp.q_rdc_norm2 = sqrt(cdp.q_rdc_norm2 / len(cdp.q_factors_rdc_norm2))


def read(align_id=None, file=None, dir=None, file_data=None, data_type='D', spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None, spin_id=None, neg_g_corr=False):
    """Read the RDC data from file.

    @keyword align_id:      The alignment tensor ID string.
    @type align_id:         str
    @keyword file:          The name of the file to open.
    @type file:             str
    @keyword dir:           The directory containing the file (defaults to the current directory if None).
    @type dir:              str or None
    @keyword file_data:     An alternative to opening a file, if the data already exists in the correct format.  The format is a list of lists where the first index corresponds to the row and the second the column.
    @type file_data:        list of lists
    @keyword data_type:     A string which is set to 'D' means that the splitting in the aligned sample was assumed to be J + D, or if set to '2D' then the splitting was taken as J + 2D.
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
    @keyword data_col:      The column containing the RDC data in Hz.
    @type data_col:         int or None
    @keyword error_col:     The column containing the RDC errors.
    @type error_col:        int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all spins.
    @type spin_id:          None or str
    @keyword neg_g_corr:    A flag which is used to correct for the negative gyromagnetic ratio of 15N.  If True, a sign inversion will be applied to all RDC values to be loaded.
    @type neg_g_corr:       bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Either the data or error column must be supplied.
    if data_col == None and error_col == None:
        raise RelaxError("One of either the data or error column must be supplied.")

    # Store the data type as global data (need for the conversion of spin data).
    if not hasattr(cdp, 'rdc_data_types'):
        cdp.rdc_data_types = {}
    if not cdp.rdc_data_types.has_key(align_id):
        cdp.rdc_data_types[align_id] = data_type

    # Spin specific data.
    #####################

    # Loop over the RDC data.
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
        spin = return_spin(id)
        if spin == None:
            warn(RelaxNoSpinWarning(id))
            continue

        # Add the data.
        if data_col:
            # Initialise.
            if not hasattr(spin, 'rdc'):
                spin.rdc = {}

            # Data conversion.
            value = convert(value, align_id, to_intern=True)

            # Correction for the negative gyromagnetic ratio of 15N.
            if neg_g_corr and value != None:
                value = -value

            # Append the value.
            spin.rdc[align_id] = value

        # Add the error.
        if error_col:
            # Initialise.
            if not hasattr(spin, 'rdc_err'):
                spin.rdc_err = {}

            # Data conversion.
            error = convert(error, align_id, to_intern=True)

            # Append the error.
            spin.rdc_err[align_id] = error

        # Append the data for print out.
        spin_ids.append(id)
        values.append(value)
        errors.append(error)

    # Print out.
    write_spin_data(file=sys.stdout, spin_ids=spin_ids, data=values, data_name='RDCs', error=errors, error_name='RDC_error')


    # Global (non-spin specific) data.
    ##################################

    # No data, so return.
    if not len(values):
        return

    # Initialise.
    if not hasattr(cdp, 'align_ids'):
        cdp.align_ids = []
    if not hasattr(cdp, 'rdc_ids'):
        cdp.rdc_ids = []

    # Add the RDC id string.
    if align_id not in cdp.align_ids:
        cdp.align_ids.append(align_id)
    if align_id not in cdp.rdc_ids:
        cdp.rdc_ids.append(align_id)


def weight(align_id=None, spin_id=None, weight=1.0):
    """Set optimisation weights on the RDC data.

    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    @keyword spin_id:   The spin ID string.
    @type spin_id:      None or str
    @keyword weight:    The optimisation weight.  The higher the value, the more importance the RDC will have.
    @type weight:       float or int.
    """

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data corresponding to 'align_id' exists.
    if not hasattr(cdp, 'rdc_ids') or align_id not in cdp.rdc_ids:
        raise RelaxNoRDCError(align_id)

    # Loop over the spins.
    for spin in spin_loop(spin_id):
        # No data structure.
        if not hasattr(spin, 'rdc_weight'):
            spin.rdc_weight = {}

        # Set the weight.
        spin.rdc_weight[align_id] = weight


def write(align_id=None, file=None, dir=None, bc=False, force=False):
    """Display the RDC data corresponding to the alignment ID.

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

    # Test if the current pipe exists.
    pipes.test()

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if data corresponding to 'align_id' exists.
    if not hasattr(cdp, 'rdc_ids') or align_id not in cdp.rdc_ids:
        raise RelaxNoRDCError(align_id)

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
        # Skip spins with no RDCs.
        if not bc and (not hasattr(spin, 'rdc') or align_id not in spin.rdc.keys()):
            continue
        elif bc and (not hasattr(spin, 'rdc_bc') or align_id not in spin.rdc_bc.keys()):
            continue

        # Append the spin data.
        mol_names.append(mol_name)
        res_nums.append(res_num)
        res_names.append(res_name)
        spin_nums.append(spin.num)
        spin_names.append(spin.name)

        # The value.
        if bc:
            values.append(convert(spin.rdc_bc[align_id], align_id))
        else:
            values.append(convert(spin.rdc[align_id], align_id))

        # The error.
        if hasattr(spin, 'rdc_err') and align_id in spin.rdc_err.keys():
            errors.append(convert(spin.rdc_err[align_id], align_id))
        else:
            errors.append(None)

    # Write out.
    write_spin_data(file=file, mol_names=mol_names, res_nums=res_nums, res_names=res_names, spin_nums=spin_nums, spin_names=spin_names, data=values, data_name='RDCs', error=errors, error_name='RDC_error')
