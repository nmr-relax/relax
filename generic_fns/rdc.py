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
"""Module for the manipulation of RDC data."""

# Python module imports.
from math import pi, sqrt
from numpy import float64, ones, zeros
from numpy.linalg import norm
import sys
from warnings import warn

# relax module imports.
from generic_fns import grace, pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from maths_fns.rdc import ave_rdc_tensor
from physical_constants import dipolar_constant, return_gyromagnetic_ratio
from relax_errors import RelaxError, RelaxNoRDCError, RelaxNoSequenceError, RelaxNoSpinError
from relax_io import open_write_file, read_spin_data, write_spin_data
from relax_warnings import RelaxWarning


def back_calc(align_id=None):
    """Back calculate the RDC from the alignment tensor and unit bond vectors.

    @keyword align_id:      The alignment tensor ID string.
    @type align_id:         str
    """

    # Arg check.
    if align_id not in cdp.align_ids:
        raise RelaxError, "The alignment ID '%s' is not in the alignment ID list %s." % (align_id, cdp.align_ids)

    # The weights.
    weights = ones(cdp.N, float64) / cdp.N

    # Unit vector data structure init.
    unit_vect = zeros((cdp.N, 3), float64)

    # Loop over the spins.
    for spin in spin_loop():
        # Skip spins with no bond vectors.
        if not hasattr(spin, 'bond_vect') and not hasattr(spin, 'xh_vect'):
            continue

        # Alias.
        if hasattr(spin, 'bond_vect'):
            vectors = spin.bond_vect
        else:
            vectors = spin.xh_vect

        # Loop over each alignment.
        for i in range(len(cdp.align_tensors)):
            # Gyromagnetic ratios.
            gx = return_gyromagnetic_ratio(spin.heteronuc_type)
            gh = return_gyromagnetic_ratio(spin.proton_type)

            # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
            dj = 3.0/(2.0*pi) * dipolar_constant(gx, gh, spin.r)

            # Unit vectors.
            for c in range(cdp.N):
                unit_vect[c] = vectors[c] / norm(vectors[c])

            # Calculate the RDC.
            if not hasattr(spin, 'rdc_bc'):
                spin.rdc_bc = {}
            spin.rdc_bc[align_id] = ave_rdc_tensor(dj, unit_vect, cdp.N, cdp.align_tensors[i].A, weights=weights)


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

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip if data is missing.
            if not hasattr(spin, 'rdc') or not hasattr(spin, 'rdc_bc') or not align_id in spin.rdc.keys() or not align_id in spin.rdc_bc.keys():
                continue

            # Append the data.
            data[-1].append([spin.rdc[align_id], spin.rdc_bc[align_id], spin.rdc_err[align_id], spin_id])

    # The data size.
    size = len(data)

    # Only one data set.
    data = [data]

    # Grace file.
    if format == 'grace':
        # The header.
        grace.write_xy_header(file=file, title="RDC correlation plot", sets=size, set_names=[None]+cdp.rdc_ids, linestyle=[2]+[0]*size, data_type=['rdc', 'rdc_bc'], axis_min=[-10, -10], axis_max=[10, 10], legend_pos=[1, 0.5])

        # The main data.
        grace.write_xy_data(data=data, file=file, graph_type='xydy')


def display(align_id=None):
    """Display the RDC data corresponding to the alignment ID.

    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    """

    # Call the write method with sys.stdout as the file.
    write(align_id=align_id, file=sys.stdout)


def q_factors(spin_id=None):
    """Calculate the Q-factors for the RDC data.

    @keyword spin_id:   The spin ID string used to restrict the Q-factor calculation to a subset of all spins.
    @type spin_id:      None or str
    """

    # Q-factor list.
    cdp.q_factors_rdc = []
    cdp.q_factors_rdc_norm2 = []

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
            if hasattr(spin, 'rdc'):
                rdc_data = True
            if hasattr(spin, 'rdc_bc'):
                rdc_bc_data = True

            # Skip spins without RDC data.
            if not hasattr(spin, 'rdc') or not hasattr(spin, 'rdc_bc') or align_id not in spin.rdc.keys() or spin.rdc[align_id] == None:
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
        R = Dr / Da
        norm = 2.0 * (Da)**2 * (4.0 + 3.0*R**2)/5.0
        if Da == 0.0:
            norm = 1e-15

        # The Q-factor for the alignment.
        Q = sqrt(sse / N / norm)
        cdp.q_factors_rdc.append(Q)
        cdp.q_factors_rdc_norm2.append(sqrt(sse / D2_sum))

    # The total Q-factor.
    cdp.q_rdc = 0.0
    cdp.q_rdc_norm2 = 0.0
    for Q in cdp.q_factors_rdc:
        cdp.q_rdc = cdp.q_rdc + Q**2
    for Q in cdp.q_factors_rdc_norm2:
        cdp.q_rdc_norm2 = cdp.q_rdc_norm2 + Q**2
    cdp.q_rdc = sqrt(cdp.q_rdc / len(cdp.q_factors_rdc))
    cdp.q_rdc_norm2 = sqrt(cdp.q_rdc_norm2 / len(cdp.q_factors_rdc_norm2))


def read(align_id=None, file=None, dir=None, file_data=None, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None, spin_id=None):
    """Read the RDC data from file.

    @keyword align_id:      The alignment tensor ID string.
    @type align_id:         str
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
    @keyword data_col:      The column containing the RDC data in Hz.
    @type data_col:         int or None
    @keyword error_col:     The column containing the RDC errors.
    @type error_col:        int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword spin_id:       The spin ID string used to restrict data loading to a subset of all
                            spins.
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
        spin = return_spin([id, spin_id])
        if spin == None:
            raise RelaxNoSpinError(id)

        # Add the data.
        if data_col:
            # Initialise.
            if not hasattr(spin, 'rdc'):
                spin.rdc = {}

            # Append the value.
            spin.rdc[align_id] = value

        # Add the error.
        if error_col:
            # Initialise.
            if not hasattr(spin, 'rdc_err'):
                spin.rdc_err = {}

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


def write(align_id=None, file=None, dir=None, force=False):
    """Display the RDC data corresponding to the alignment ID.

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
    if not hasattr(cdp, 'rdc_ids') or align_id not in cdp.rdc_ids:
        raise RelaxNoRDCError(align_id)

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # The index.
    index = cdp.rdc_ids.index(align_id)

    # Loop over the spins and collect the data.
    spin_ids = []
    values = []
    errors = []
    for spin, spin_id in spin_loop(return_id=True):
        # Skip spins with no RDCs.
        if not hasattr(spin, 'rdc') or align_id not in spin.rdc.keys():
            continue

        # Store the data.
        spin_ids.append(spin_id)
        values.append(spin.rdc[align_id])
        if hasattr(spin, 'rdc_err') and align_id in spin.rdc_err.keys():
            errors.append(spin.rdc_err[align_id])
        else:
            errors.append(None)

    # Write out.
    write_spin_data(file=file, spin_ids=spin_ids, data=values, data_name='RDCs', error=errors, error_name='RDC_error')
