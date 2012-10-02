###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Module for the manipulation of RDC data."""

# Python module imports.
from copy import deepcopy
from math import pi, sqrt
from numpy import float64, ones, zeros
from numpy.linalg import norm
import sys
from warnings import warn

# relax module imports.
from arg_check import is_float
from float import nan
from generic_fns import grace, pipes
from generic_fns.align_tensor import get_tensor_index
from generic_fns.interatomic import create_interatom, interatomic_loop, return_interatom
from generic_fns.mol_res_spin import exists_mol_res_spin_data, generate_spin_id, return_spin, spin_loop
from maths_fns.rdc import ave_rdc_tensor
from physical_constants import dipolar_constant, return_gyromagnetic_ratio
from relax_errors import RelaxError, RelaxNoRDCError, RelaxNoSequenceError, RelaxSpinTypeError
from relax_io import extract_data, open_write_file, strip, write_data
from relax_warnings import RelaxWarning


def back_calc(align_id=None):
    """Back calculate the RDC from the alignment tensor and unit bond vectors.

    @keyword align_id:      The alignment tensor ID string.
    @type align_id:         str
    """

    # Arg check.
    if align_id and align_id not in cdp.align_ids:
        raise RelaxError("The alignment ID '%s' is not in the alignment ID list %s." % (align_id, cdp.align_ids))

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

    # Loop over the interatomic data.
    for interatom in interatomic_loop():
        # Skip containers with no interatomic vectors.
        if not hasattr(interatom, 'vector'):
            continue

        # Get the spins.
        spin1 = return_spin(interatom.spin_id1)
        spin2 = return_spin(interatom.spin_id2)

        # Checks.
        if not hasattr(spin1, 'isotope'):
            raise RelaxSpinTypeError(interatom.spin_id1)
        if not hasattr(spin2, 'isotope'):
            raise RelaxSpinTypeError(interatom.spin_id2)

        # Single vector.
        if is_float(interatom.vector[0], raise_error=False):
            vectors = [interatom.vector]
        else:
            vectors = interatom.vector

        # Gyromagnetic ratios.
        g1 = return_gyromagnetic_ratio(spin1.isotope)
        g2 = return_gyromagnetic_ratio(spin2.isotope)

        # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
        dj = 3.0/(2.0*pi) * dipolar_constant(g1, g2, interatom.r)

        # Unit vectors.
        for c in range(cdp.N):
            unit_vect[c] = vectors[c] / norm(vectors[c])

        # Initialise if necessary.
        if not hasattr(interatom, 'rdc_bc'):
            interatom.rdc_bc = {}

        # Calculate the RDCs.
        for id in align_ids:
            interatom.rdc_bc[id] = ave_rdc_tensor(dj, unit_vect, cdp.N, cdp.align_tensors[get_tensor_index(id)].A, weights=weights)


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
    if hasattr(cdp, 'rdc_data_types') and align_id in cdp.rdc_data_types and cdp.rdc_data_types[align_id] == '2D':
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
        for interatom in interatomic_loop():
            # Error present.
            if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err.keys():
                err_flag = True
                break

        # Loop over the interatomic data.
        for interatom in interatomic_loop():
            # Skip if data is missing.
            if not hasattr(interatom, 'rdc') or not hasattr(interatom, 'rdc_bc') or not align_id in interatom.rdc.keys() or not align_id in interatom.rdc_bc.keys():
                continue

            # Append the data.
            data[-1].append([convert(interatom.rdc_bc[align_id], align_id), convert(interatom.rdc[align_id], align_id)])

            # Errors.
            if err_flag:
                if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err.keys():
                    data[-1][-1].append(convert(interatom.rdc_err[align_id], align_id))
                else:
                    data[-1][-1].append(None)

            # Label.
            data[-1][-1].append("%s-%s" % (interatom.spin_id1, interatom.spin_id2))

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
        if hasattr(cdp, 'rdc_data_types') and id in cdp.rdc_data_types:
            cdp.rdc_data_types.pop(id)

        # The interatomic data.
        for interatom in interatomic_loop():
            # The data.
            if hasattr(interatom, 'rdc') and id in interatom.rdc:
                interatom.rdc.pop(id)

            # The error.
            if hasattr(interatom, 'rdc_err') and id in interatom.rdc_err:
                interatom.rdc_err.pop(id)

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

        # Interatomic data loop.
        dj = None
        N = 0
        interatom_count = 0
        rdc_data = False
        rdc_bc_data = False
        norm2_flag = True
        for interatom in interatomic_loop():
            # Increment the counter.
            interatom_count += 1

            # Data checks.
            if hasattr(interatom, 'rdc') and align_id in interatom.rdc:
                rdc_data = True
            if hasattr(interatom, 'rdc_bc') and align_id in interatom.rdc_bc:
                rdc_bc_data = True

            # Skip containers without RDC data.
            if not hasattr(interatom, 'rdc') or not hasattr(interatom, 'rdc_bc') or not align_id in interatom.rdc or interatom.rdc[align_id] == None or not align_id in interatom.rdc_bc or interatom.rdc_bc[align_id] == None:
                continue

            # Get the spins.
            spin1 = return_spin(interatom.spin_id1)
            spin2 = return_spin(interatom.spin_id2)

            # Sum of squares.
            sse = sse + (interatom.rdc[align_id] - interatom.rdc_bc[align_id])**2

            # Sum the RDCs squared (for one type of normalisation).
            D2_sum = D2_sum + interatom.rdc[align_id]**2

            # Gyromagnetic ratios.
            g1 = return_gyromagnetic_ratio(spin1.isotope)
            g2 = return_gyromagnetic_ratio(spin2.isotope)

            # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
            dj_new = 3.0/(2.0*pi) * dipolar_constant(g1, g2, interatom.r)
            if norm2_flag and dj != None and dj_new != dj:
                warn(RelaxWarning("The dipolar constant is not the same for all RDCs, skipping the Q factor normalised with 2Da^2(4 + 3R)/5."))
                norm2_flag = False
            else:
                dj = dj_new

            # Increment the number of data sets.
            N = N + 1

        # Warnings (and then exit).
        if not interatom_count:
            warn(RelaxWarning("No interatomic data containers have been used in the calculation."))
            return
        if not rdc_data:
            warn(RelaxWarning("No RDC data can be found."))
            return
        if not rdc_bc_data:
            warn(RelaxWarning("No back-calculated RDC data can be found."))
            return

        # Normalisation factor of 2Da^2(4 + 3R)/5.
        if norm2_flag:
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
            cdp.q_factors_rdc[align_id] = sqrt(sse / N / norm)

        else:
            cdp.q_factors_rdc[align_id] = 0.0

        # The second Q-factor definition.
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


def read(align_id=None, file=None, dir=None, file_data=None, data_type='D', spin_id1_col=None, spin_id2_col=None, data_col=None, error_col=None, sep=None, neg_g_corr=False, absolute=False):
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
    @keyword spin_id1_col:  The column containing the spin ID strings of the first spin.
    @type spin_id1_col:     int
    @keyword spin_id2_col:  The column containing the spin ID strings of the second spin.
    @type spin_id2_col:     int
    @keyword data_col:      The column containing the RDC data in Hz.
    @type data_col:         int or None
    @keyword error_col:     The column containing the RDC errors.
    @type error_col:        int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    @keyword neg_g_corr:    A flag which is used to correct for the negative gyromagnetic ratio of 15N.  If True, a sign inversion will be applied to all RDC values to be loaded.
    @type neg_g_corr:       bool
    @keyword absolute:      A flag which if True indicates that the RDCs to load are signless.  All RDCs will then be converted to positive values.
    @type absolute:         bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Either the data or error column must be supplied.
    if data_col == None and error_col == None:
        raise RelaxError("One of either the data or error column must be supplied.")

    # Store the data type as global data (need for the conversion of RDC data).
    if not hasattr(cdp, 'rdc_data_types'):
        cdp.rdc_data_types = {}
    if not align_id in cdp.rdc_data_types:
        cdp.rdc_data_types[align_id] = data_type

    # Spin specific data.
    #####################

    # Extract the data from the file.
    file_data = extract_data(file, dir, sep=sep)

    # Loop over the RDC data.
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

        # Unpack.
        spin_id1 = line[spin_id1_col-1]
        spin_id2 = line[spin_id2_col-1]
        value = None
        if data_col:
            value = line[data_col-1]
        error = None
        if error_col:
            error = line[error_col-1]

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
                warn(RelaxWarning("The RDC value of the line %s is invalid." % line))
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

        # Remap the spin IDs.
        spin_id1 = spin1._spin_ids[0]
        spin_id2 = spin2._spin_ids[0]

        # Get the interatomic data container.
        interatom = return_interatom(spin_id1, spin_id2)

        # Create the container if needed.
        if interatom == None:
            interatom = create_interatom(spin_id1=spin_id1, spin_id2=spin_id2)

        # Convert and add the data.
        if data_col:
            # Data conversion.
            value = convert(value, align_id, to_intern=True)

            # Correction for the negative gyromagnetic ratio of 15N.
            if neg_g_corr and value != None:
                value = -value

            # Absolute values.
            if absolute:
                # Force the value to be positive.
                value = abs(value)

            # Initialise.
            if not hasattr(interatom, 'rdc'):
                interatom.rdc = {}

            # Add the value.
            interatom.rdc[align_id] = value

            # Store the absolute value flag.
            if not hasattr(interatom, 'absolute_rdc'):
                interatom.absolute_rdc = {}
            interatom.absolute_rdc[align_id] = absolute

        # Convert and add the error.
        if error_col:
            # Data conversion.
            error = convert(error, align_id, to_intern=True)

            # Initialise.
            if not hasattr(interatom, 'rdc_err'):
                interatom.rdc_err = {}

            # Append the error.
            interatom.rdc_err[align_id] = error

        # Append the data for printout.
        data.append([spin_id1, spin_id2, repr(value), repr(error)])

    # No data, so fail hard!
    if not len(data):
        raise RelaxError("No RDC data could be extracted.")

    # Print out.
    print("The following RDCs have been loaded into the relax data store:\n")
    write_data(out=sys.stdout, headings=["Spin_ID1", "Spin_ID2", "Value", "Error"], data=data)

    # Initialise some global structures.
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

    # Loop over the interatomic data.
    for interatom in interatomic_loop():
        # No data structure.
        if not hasattr(interatom, 'rdc_weight'):
            interatom.rdc_weight = {}

        # Set the weight.
        interatom.rdc_weight[align_id] = weight


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

    # Loop over the interatomic data containers and collect the data.
    data = []
    for interatom in interatomic_loop():
        # Skip containers with no RDCs.
        if not bc and (not hasattr(interatom, 'rdc') or align_id not in interatom.rdc.keys()):
            continue
        elif bc and (not hasattr(interatom, 'rdc_bc') or align_id not in interatom.rdc_bc.keys()):
            continue

        # Append the spin data.
        data.append([])
        data[-1].append(interatom.spin_id1)
        data[-1].append(interatom.spin_id2)

        # The value.
        if bc:
            data[-1].append(repr(convert(interatom.rdc_bc[align_id], align_id)))
        else:
            data[-1].append(repr(convert(interatom.rdc[align_id], align_id)))

        # The error.
        if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err.keys():
            data[-1].append(repr(convert(interatom.rdc_err[align_id], align_id)))
        else:
            data[-1].append(repr(None))

    # Write out.
    write_data(out=file, headings=["Spin_ID1", "Spin_ID2", "RDCs", "RDC_error"], data=data)
