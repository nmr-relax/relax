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
"""Module for the manipulation of RDC data."""

# Python module imports.
from copy import deepcopy
from math import ceil, floor, pi, sqrt
from numpy import array, int32, float64, ones, transpose, zeros
from numpy.linalg import norm
import sys
from warnings import warn

# relax module imports.
from lib.check_types import is_float
from lib.float import nan
from lib.alignment.rdc import ave_rdc_tensor
from lib.errors import RelaxError, RelaxNoAlignError, RelaxNoJError, RelaxNoRDCError, RelaxNoSequenceError, RelaxSpinTypeError
from lib.io import extract_data, open_write_file, strip, write_data
from lib.periodic_table import periodic_table
from lib.physical_constants import dipolar_constant
from lib.warnings import RelaxWarning, RelaxSpinTypeWarning
from pipe_control import grace, pipes
from pipe_control.align_tensor import get_tensor_index, get_tensor_object, opt_uses_align_data, opt_uses_tensor
from pipe_control.interatomic import consistent_interatomic_data, create_interatom, interatomic_loop, return_interatom
from pipe_control.mol_res_spin import exists_mol_res_spin_data, is_pseudoatom, pseudoatom_loop, return_spin
from pipe_control.pipes import check_pipe


def back_calc(align_id=None):
    """Back calculate the RDC from the alignment tensor and unit bond vectors.

    @keyword align_id:      The alignment tensor ID string.
    @type align_id:         str
    """

    # Check the pipe setup.
    check_pipe_setup(rdc_id=align_id, sequence=True, N=True, tensors=True)

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
    count = 0
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
        if is_float(interatom.vector[0]):
            vectors = [interatom.vector]
        else:
            vectors = interatom.vector

        # Gyromagnetic ratios.
        g1 = periodic_table.gyromagnetic_ratio(spin1.isotope)
        g2 = periodic_table.gyromagnetic_ratio(spin2.isotope)

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
            # The signed value.
            interatom.rdc_bc[id] = ave_rdc_tensor(dj, unit_vect, cdp.N, cdp.align_tensors[get_tensor_index(align_id=id)].A, weights=weights)

            # T values.
            if hasattr(interatom, 'rdc_data_types') and align_id in interatom.rdc_data_types and interatom.rdc_data_types[align_id] == 'T':
                if not hasattr(interatom, 'j_coupling'):
                    raise RelaxNoJError

                interatom.rdc_bc[id] += interatom.j_coupling

            # The absolute value.
            if hasattr(interatom, 'absolute_rdc') and id in interatom.absolute_rdc and interatom.absolute_rdc[id]:
                interatom.rdc_bc[id] = abs(interatom.rdc_bc[id])

        # Increment the counter.
        count += 1

    # No RDCs calculated.
    if not count:
        warn(RelaxWarning("No RDCs have been back calculated, probably due to missing bond vector information."))


def check_pipe_setup(pipe=None, rdc_id=None, sequence=False, N=False, tensors=False, rdc=False):
    """Check that the current data pipe has been setup sufficiently.

    @keyword pipe:      The data pipe to check, defaulting to the current pipe.
    @type pipe:         None or str
    @keyword rdc_id:    The RDC ID string to check for in cdp.rdc_ids.
    @type rdc_id:       None or str
    @keyword sequence:  A flag which when True will invoke the sequence data check.
    @type sequence:     bool
    @keyword N:         A flag which if True will check that cdp.N is set.
    @type N:            bool
    @keyword tensors:   A flag which if True will check that alignment tensors exist.
    @type tensors:      bool
    @keyword rdc:       A flag which if True will check that RDCs exist.
    @type rdc:          bool
    """

    # The data pipe.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Test if the current data pipe exists.
    check_pipe(pipe)

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
    if rdc_id and (not hasattr(dp, 'align_ids') or rdc_id not in dp.align_ids):
        raise RelaxNoAlignError(rdc_id, pipe)

    # Test if RDC data exists.
    if rdc and not hasattr(dp, 'align_ids'):
        raise RelaxNoAlignError()
    if rdc and not hasattr(dp, 'rdc_ids'):
        raise RelaxNoRDCError()
    elif rdc and rdc_id and rdc_id not in dp.rdc_ids:
        raise RelaxNoRDCError(rdc_id)


def check_rdcs(interatom):
    """Check if all data required for calculating the RDC is present.

    @param interatom:   The interatomic data container.
    @type interatom:    InteratomContainer instance
    @return:            True if all data required for calculating the RDC is present, False otherwise.
    @rtype:             bool
    """

    # Skip deselected interatomic data containers.
    if not interatom.select:
        return False

    # Only use interatomic data containers with RDC data.
    if not hasattr(interatom, 'rdc'):
        return False

    # Only use interatomic data containers with RDC and J coupling data.
    if opt_uses_j_couplings() and not hasattr(interatom, 'j_coupling'):
        return False

    # Get the spins.
    spin1 = return_spin(interatom.spin_id1)
    spin2 = return_spin(interatom.spin_id2)

    # Spin information checks.
    if not hasattr(spin1, 'isotope'):
        warn(RelaxSpinTypeWarning(interatom.spin_id1))
        return False
    if not hasattr(spin2, 'isotope'):
        warn(RelaxSpinTypeWarning(interatom.spin_id2))
        return False
    if is_pseudoatom(spin1) and is_pseudoatom(spin2):
        warn(RelaxWarning("Support for both spins being in a dipole pair being pseudo-atoms is not implemented yet."))
        return False

    # Pseudo-atom checks.
    if is_pseudoatom(spin1) or is_pseudoatom(spin2):
        # Alias the pseudo and normal atoms.
        pseudospin = spin1
        base_spin_id = interatom.spin_id2
        pseudospin_id = interatom.spin_id1
        if is_pseudoatom(spin2):
            pseudospin = spin2
            base_spin_id = interatom.spin_id1
            pseudospin_id = interatom.spin_id2

        # Loop over the atoms of the pseudo-atom.
        for spin, spin_id in pseudoatom_loop(pseudospin, return_id=True):
            # Get the corresponding interatomic data container.
            pseudo_interatom = return_interatom(spin_id1=spin_id, spin_id2=base_spin_id)

            # Unit vector check.
            if not hasattr(pseudo_interatom, 'vector'):
                warn(RelaxWarning("The interatomic vector is missing for the spin pair '%s' and '%s' of the pseudo-atom '%s', skipping the RDC for the spin pair '%s' and '%s'." % (pseudo_interatom.spin_id1, pseudo_interatom.spin_id2, pseudospin_id, base_spin_id, pseudospin_id)))
                return False

            # Check.
            if not hasattr(pseudo_interatom, 'r'):
                warn(RelaxWarning("The averaged interatomic distance between spins '%s' and '%s' for the pseudo-atom '%s' has not been set yet." % (spin_id, base_spin_id, pseudospin_id)))
                return False

    # Normal atoms checks.
    else:
        # Unit vector check.
        if not hasattr(interatom, 'vector'):
            warn(RelaxWarning("The interatomic vector is missing, skipping the spin pair '%s' and '%s'." % (interatom.spin_id1, interatom.spin_id2)))
            return False

        # Distance information check.
        if not hasattr(interatom, 'r'):
            warn(RelaxWarning("The averaged interatomic distance between spins '%s' and '%s' has not been set yet." % (interatom.spin_id1, interatom.spin_id2)))
            return False

    # Everything is ok.
    return True


def convert(value, data_type, align_id, to_intern=False):
    """Convert the RDC based on the 'D' or '2D' data type.

    @param value:           The value or error to convert.
    @type value:            float or None
    @param data_type:       The RDC data type.  Either 'D', '2D' or 'T'.
    @type data_type:        str
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
    if data_type == '2D':
        # Convert from 2D to D.
        if to_intern:
            factor = 2.0

        # Convert from D to 2D.
        else:
            factor = 0.5

    # Return the converted value.
    return value * factor


def copy(pipe_from=None, pipe_to=None, align_id=None):
    """Copy the RDC data from one data pipe to another.

    @keyword pipe_from: The data pipe to copy the RDC data from.  This defaults to the current data pipe.
    @type pipe_from:    str
    @keyword pipe_to:   The data pipe to copy the RDC data to.  This defaults to the current data pipe.
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
    check_pipe_setup(pipe=pipe_from, rdc_id=align_id, sequence=True, rdc=True)
    check_pipe_setup(pipe=pipe_to, sequence=True)

    # Get the data pipes.
    dp_from = pipes.get_pipe(pipe_from)
    dp_to = pipes.get_pipe(pipe_to)

    # Test that the interatomic data is consistent between the two data pipe.
    consistent_interatomic_data(pipe1=pipe_to, pipe2=pipe_from)

    # The IDs.
    if align_id == None:
        align_ids = dp_from.align_ids
    else:
        align_ids = [align_id]

    # Init target pipe global structures.
    if not hasattr(dp_to, 'align_ids'):
        dp_to.align_ids = []
    if not hasattr(dp_to, 'rdc_ids'):
        dp_to.rdc_ids = []

    # Loop over the align IDs.
    for align_id in align_ids:
        # Copy the global data.
        if align_id not in dp_to.align_ids and align_id not in dp_to.align_ids:
            dp_to.align_ids.append(align_id)
        if align_id in dp_from.rdc_ids and align_id not in dp_to.rdc_ids:
            dp_to.rdc_ids.append(align_id)

        # Loop over the interatomic data.
        for i in range(len(dp_from.interatomic)):
            # Alias the containers.
            interatom_from = dp_from.interatomic[i]
            interatom_to = dp_to.interatomic[i]

            # No data or errors.
            if (not hasattr(interatom_from, 'rdc') or not align_id in interatom_from.rdc) and (not hasattr(interatom_from, 'rdc_err') or not align_id in interatom_from.rdc_err):
                continue

            # Initialise the data structures if necessary.
            if hasattr(interatom_from, 'rdc') and not hasattr(interatom_to, 'rdc'):
                interatom_to.rdc = {}
            if hasattr(interatom_from, 'rdc_err') and not hasattr(interatom_to, 'rdc_err'):
                interatom_to.rdc_err = {}

            # Copy the value and error from pipe_from.
            if hasattr(interatom_from, 'rdc'):
                interatom_to.rdc[align_id] = interatom_from.rdc[align_id]
            if hasattr(interatom_from, 'rdc_err'):
                interatom_to.rdc_err[align_id] = interatom_from.rdc_err[align_id]


def corr_plot(format=None, title=None, subtitle=None, file=None, dir=None, force=False):
    """Generate a correlation plot of the measured vs. back-calculated RDCs.

    @keyword format:    The format for the plot file.  The following values are accepted: 'grace', a Grace plot; None, a plain text file.
    @type format:       str or None
    @keyword title:     The title for the plot, overriding the default.
    @type title:        None or str
    @keyword subtitle:  The subtitle for the plot, overriding the default.
    @type subtitle:     None or str
    @keyword file:      The file name or object to write to.
    @type file:         str or file object
    @keyword dir:       The name of the directory to place the file into (defaults to the current directory).
    @type dir:          str
    @keyword force:     A flag which if True will cause any pre-existing file to be overwritten.
    @type force:        bool
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True)

    # Does RDC data exist?
    if not hasattr(cdp, 'rdc_ids') or not cdp.rdc_ids:
        warn(RelaxWarning("No RDC data exists, skipping file creation."))
        return

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Init.
    data = []
    orig_title = title
    if orig_title == None:
        title = "RDC correlation plot"
    axis_labels = ["Back-calculated RDC (Hz)", "Measured RDC (Hz)"]

    # The diagonal.
    data.append([[-100, -100, 0], [100, 100, 0]])

    # Loop over the RDC data.
    min_rdc = 1e100
    max_rdc = -1e100
    for align_id in cdp.rdc_ids:
        # Append a new list for this alignment.
        data.append([])

        # Errors present?
        err_flag = False
        for interatom in interatomic_loop():
            # Error present.
            if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err:
                err_flag = True
                break

        # Loop over the interatomic data.
        for interatom in interatomic_loop():
            # Skip if data is missing.
            if not hasattr(interatom, 'rdc') or not hasattr(interatom, 'rdc_bc') or not align_id in interatom.rdc or not align_id in interatom.rdc_bc:
                continue
            if interatom.rdc[align_id] == None or interatom.rdc_bc[align_id] == None:
                continue

            # Convert between the 2D and D notation.
            rdc_bc = convert(interatom.rdc_bc[align_id], interatom.rdc_data_types[align_id], align_id)
            rdc = convert(interatom.rdc[align_id], interatom.rdc_data_types[align_id], align_id)

            # T=J+D type data.
            if hasattr(interatom, 'rdc_data_types') and align_id in interatom.rdc_data_types and interatom.rdc_data_types[align_id] == 'T':
                # Convert T=J+D type data to D, if not absolute.
                if not interatom.absolute_rdc[align_id]:
                    rdc_bc -= interatom.j_coupling
                    rdc -= interatom.j_coupling

                # A different title and axis labels.
                else:
                    if orig_title == None:
                        title = "T = J+D correlation plot"
                    axis_labels = ["Measured T = J+D (Hz)", "Back-calculated T = J+D (Hz)"]

            # Append the data.
            data[-1].append([rdc_bc, rdc])

            # The minimum of all data sets.
            if rdc < min_rdc:
                min_rdc = rdc
            if rdc_bc < min_rdc:
                min_rdc = rdc_bc

            # The maximum of all data sets.
            if rdc > max_rdc:
                max_rdc = rdc
            if rdc_bc > max_rdc:
                max_rdc = rdc_bc

            # Errors.
            if err_flag:
                if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err:
                    data[-1][-1].append(convert(interatom.rdc_err[align_id], interatom.rdc_data_types[align_id], align_id))
                else:
                    data[-1][-1].append(None)

            # Label.
            data[-1][-1].append("%s-%s" % (interatom.spin_id1, interatom.spin_id2))

    # The data size.
    size = len(data)

    # Round the data limits.
    max_rdc = ceil(max_rdc)
    min_rdc = floor(min_rdc)

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
        grace.write_xy_header(file=file, title=title, subtitle=subtitle, world=[[min_rdc, min_rdc, max_rdc, max_rdc]], sets=[size], set_names=[[None]+cdp.rdc_ids], linestyle=[[2]+[0]*size], data_type=['rdc', 'rdc_bc'], axis_labels=[axis_labels], tick_major_spacing=[[10, 10]], tick_minor_count=[[9, 9]], legend_pos=[[1, 0.5]])

        # The main data.
        grace.write_xy_data(data=data, file=file, graph_type=graph_type, autoscale=False)


def delete(align_id=None):
    """Delete the RDC data corresponding to the alignment ID.

    @keyword align_id:  The alignment tensor ID string.  If not specified, all data will be deleted.
    @type align_id:     str or None
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, rdc_id=align_id, rdc=True)

    # The IDs.
    if not align_id:
        ids = deepcopy(cdp.rdc_ids)
    else:
        ids = [align_id]

    # Loop over the alignments, removing all the corresponding data.
    for id in ids:
        # The RDC ID.
        cdp.rdc_ids.pop(cdp.rdc_ids.index(id))

        # The interatomic data.
        for interatom in interatomic_loop():
            # The data.
            if hasattr(interatom, 'rdc') and id in interatom.rdc:
                interatom.rdc.pop(id)

            # The error.
            if hasattr(interatom, 'rdc_err') and id in interatom.rdc_err:
                interatom.rdc_err.pop(id)

            # The data type.
            if hasattr(interatom, 'rdc_data_types') and id in interatom.rdc_data_types:
                interatom.rdc_data_types.pop(id)

        # Clean the global data.
        if not hasattr(cdp, 'pcs_ids') or id not in cdp.pcs_ids:
            cdp.align_ids.pop(cdp.align_ids.index(id))


def display(align_id=None, bc=False):
    """Display the RDC data corresponding to the alignment ID.

    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    @keyword bc:        The back-calculation flag which if True will cause the back-calculated rather than measured data to be displayed.
    @type bc:           bool
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, rdc_id=align_id, rdc=True)

    # Call the write method with sys.stdout as the file.
    write(align_id=align_id, file=sys.stdout, bc=bc)


def opt_uses_j_couplings():
    """Determine of J couplings are needed for optimisation.

    @return:    True if J couplings are required, False otherwise.
    @rtype:     bool
    """

    # Loop over the alignments.
    for align_id in cdp.align_ids:
        for interatom in interatomic_loop():
            if hasattr(interatom, 'rdc_data_types') and align_id in interatom.rdc_data_types and interatom.rdc_data_types[align_id] == 'T':
                return True

    # No J values required.
    return False


def opt_uses_rdc(align_id):
    """Determine if the RDC data for the given alignment ID is needed for optimisation.

    @param align_id:    The alignment ID string.
    @type align_id:     str
    @return:            True if the RDC data is to be used for optimisation, False otherwise.
    @rtype:             bool
    """

    # No alignment IDs.
    if not hasattr(cdp, 'rdc_ids'):
        return False

    # No RDC data for the alignment.
    if align_id not in cdp.rdc_ids:
        return False

    # Is the tensor optimised?
    tensor_flag = opt_uses_tensor(get_tensor_object(align_id))

    # Is the paramagnetic position optimised?
    pos_flag = False
    if hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed:
        pos_flag = True

    # Are the populations optimised?
    prob_flag = False
    if cdp.model == 'population':
        prob_flag = True

    # Not used.
    if not tensor_flag and not pos_flag and not prob_flag:
        return False

    # The RDC data is to be used for optimisation.
    return True


def q_factors(spin_id=None, verbosity=1):
    """Calculate the Q factors for the RDC data.

    @keyword spin_id:   The spin ID string used to restrict the Q factor calculation to a subset of all spins.
    @type spin_id:      None or str
    @keyword verbosity: A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:    int
    """

    # Initial printout.
    if verbosity:
        print("\nRDC Q factors (norm1, norm2):")

    # Check the pipe setup.
    check_pipe_setup(sequence=True)

    # No RDCs, so no Q factors can be calculated.
    if not hasattr(cdp, 'rdc_ids') or not len(cdp.rdc_ids):
        warn(RelaxWarning("No RDC data exists, Q factors cannot be calculated."))
        return

    # Q factor dictonaries.
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
            j_flag = False
            if hasattr(interatom, 'rdc_data_types') and align_id in interatom.rdc_data_types and interatom.rdc_data_types[align_id] == 'T':
                j_flag = True
                if not hasattr(interatom, 'j_coupling'):
                    raise RelaxNoJError

            # Skip containers without RDC data.
            if not hasattr(interatom, 'rdc') or not hasattr(interatom, 'rdc_bc') or not align_id in interatom.rdc or interatom.rdc[align_id] == None or not align_id in interatom.rdc_bc or interatom.rdc_bc[align_id] == None:
                continue

            # Get the spins.
            spin1 = return_spin(interatom.spin_id1)
            spin2 = return_spin(interatom.spin_id2)

            # Sum of squares.
            sse = sse + (interatom.rdc[align_id] - interatom.rdc_bc[align_id])**2

            # Sum the RDCs squared (for one type of normalisation).
            if j_flag:
                D2_sum = D2_sum + (interatom.rdc[align_id] - interatom.j_coupling)**2
            else:
                D2_sum = D2_sum + interatom.rdc[align_id]**2

            # Gyromagnetic ratios.
            g1 = periodic_table.gyromagnetic_ratio(spin1.isotope)
            g2 = periodic_table.gyromagnetic_ratio(spin2.isotope)

            # Skip the 2Da^2(4 + 3R)/5 normalised Q factor if pseudo-atoms are present.
            if  norm2_flag and (is_pseudoatom(spin1) or is_pseudoatom(spin2)):
                warn(RelaxWarning("Pseudo-atoms are present, skipping the Q factor normalised with 2Da^2(4 + 3R)/5."))
                norm2_flag = False

            # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
            if norm2_flag:
                dj_new = 3.0/(2.0*pi) * dipolar_constant(g1, g2, interatom.r)
                if dj != None and dj_new != dj:
                    warn(RelaxWarning("The dipolar constant is not the same for all RDCs, skipping the Q factor normalised with 2Da^2(4 + 3R)/5."))
                    norm2_flag = False
                else:
                    dj = dj_new

            # Increment the number of data sets.
            N = N + 1

        # Warnings (and then exit).
        if not interatom_count:
            warn(RelaxWarning("No interatomic data containers have been used in the calculation, skipping the RDC Q factor calculation."))
            return
        if not rdc_data:
            warn(RelaxWarning("No RDC data can be found for the alignment ID '%s', skipping the RDC Q factor calculation for this alignment." % align_id))
            continue
        if not rdc_bc_data:
            warn(RelaxWarning("No back-calculated RDC data can be found for the alignment ID '%s', skipping the RDC Q factor calculation for this alignment." % align_id))
            continue

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

            # The Q factor for the alignment.
            cdp.q_factors_rdc[align_id] = sqrt(sse / N / norm)

        else:
            cdp.q_factors_rdc[align_id] = 0.0

        # The second Q factor definition.
        cdp.q_factors_rdc_norm2[align_id] = sqrt(sse / D2_sum)

        # ID and RDC Q factor printout.
        if verbosity:
            print("    Alignment ID '%s':  %.3f, %.3f" % (align_id, cdp.q_factors_rdc[align_id], cdp.q_factors_rdc_norm2[align_id]))

    # The total Q factor.
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
    @keyword data_type:     A string which is set to 'D' means that the splitting in the aligned sample was assumed to be J + D, or if set to '2D' then the splitting was taken as J + 2D.  If set to 'T', then the data will be marked as being J+D values.
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

    # Check the pipe setup.
    check_pipe_setup(sequence=True)

    # Either the data or error column must be supplied.
    if data_col == None and error_col == None:
        raise RelaxError("One of either the data or error column must be supplied.")

    # Check the data types.
    rdc_types = ['D', '2D', 'T']
    if data_type not in rdc_types:
        raise RelaxError("The RDC data type '%s' must be one of %s." % (data_type, rdc_types))

    # Spin specific data.
    #####################

    # Extract the data from the file, and remove comments and blank lines.
    file_data = extract_data(file, dir, sep=sep)
    file_data = strip(file_data, comments=True)

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

        # Get the interatomic data container.
        interatom = return_interatom(spin_id1, spin_id2)

        # Create the container if needed.
        if interatom == None:
            interatom = create_interatom(spin_id1=spin_id1, spin_id2=spin_id2)

        # Test the error value (a value of 0.0 will cause the interatomic container to be deselected).
        if error == 0.0:
            interatom.select = False
            warn(RelaxWarning("An error value of zero has been encountered, deselecting the interatomic container between spin '%s' and '%s'." % (spin_id1, spin_id2)))
            continue

        # Store the data type as global data (need for the conversion of RDC data).
        if not hasattr(interatom, 'rdc_data_types'):
            interatom.rdc_data_types = {}
        if not align_id in interatom.rdc_data_types:
            interatom.rdc_data_types[align_id] = data_type

        # Convert and add the data.
        if data_col:
            # Data conversion.
            value = convert(value, data_type, align_id, to_intern=True)

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
            error = convert(error, data_type, align_id, to_intern=True)

            # Initialise.
            if not hasattr(interatom, 'rdc_err'):
                interatom.rdc_err = {}

            # Append the error.
            interatom.rdc_err[align_id] = error

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


def return_rdc_data(sim_index=None, verbosity=0):
    """Set up the data structures for optimisation using RDCs as base data sets.

    @keyword sim_index: The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:    None or int
    @keyword verbosity: A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:    int
    @return:            The assembled data structures for using RDCs as the base data for optimisation.  These include:
                            - rdc, the RDC values.
                            - rdc_err, the RDC errors.
                            - rdc_weight, the RDC weights.
                            - vectors, the interatomic vectors (pseudo-atom dependent).
                            - rdc_const, the dipolar constants (pseudo-atom dependent).
                            - absolute, the absolute value flags (as 1's and 0's).
                            - T_flags, the flags for T = J+D type data (as 1's and 0's).
                            - j_couplings, the J coupling values if the RDC data type is set to T = J+D.
                            - pseudo_flags, the list of flags indicating if the interatomic data contains a pseudo-atom (as 1's and 0's).
    @rtype:             tuple of (numpy rank-2 float64 array, numpy rank-2 float64 array, numpy rank-2 float64 array, list of numpy rank-3 float64 arrays, list of lists of floats, numpy rank-2 int32 array, numpy rank-2 int32 array, numpy rank-2 float64 array, numpy rank-1 int32 array)
    """

    # Initial printout.
    if verbosity:
        print("\nRDC data counts:")

    # Sort out pseudo-atoms first.  This only needs to be called once.
    setup_pseudoatom_rdc()

    # Initialise.
    rdc = []
    rdc_err = []
    rdc_weight = []
    unit_vect = []
    rdc_const = []
    absolute = []
    T_flags = []
    j_couplings = []
    pseudo_flags = []

    # The unit vectors, RDC constants, and J couplings.
    for interatom in interatomic_loop():
        # Get the spins.
        spin1 = return_spin(interatom.spin_id1)
        spin2 = return_spin(interatom.spin_id2)

        # RDC checks.
        if not check_rdcs(interatom):
            continue

        # Gyromagnetic ratios.
        g1 = periodic_table.gyromagnetic_ratio(spin1.isotope)
        g2 = periodic_table.gyromagnetic_ratio(spin2.isotope)

        # Pseudo atoms.
        if is_pseudoatom(spin1) and is_pseudoatom(spin2):
            raise RelaxError("Support for both spins being in a dipole pair being pseudo-atoms is not implemented yet.")
        if is_pseudoatom(spin1) or is_pseudoatom(spin2):
            # Set the flag.
            pseudo_flags.append(1)

            # Alias the pseudo and normal atoms.
            if is_pseudoatom(spin1):
                pseudospin = spin1
                base_spin = spin2
                pseudospin_id = interatom.spin_id1
                base_spin_id = interatom.spin_id2
            else:
                pseudospin = spin2
                base_spin = spin1
                pseudospin_id = interatom.spin_id2
                base_spin_id = interatom.spin_id1

            # Loop over the atoms of the pseudo-atom, storing the data.
            pseudo_unit_vect = []
            pseudo_rdc_const = []
            for spin, spin_id in pseudoatom_loop(pseudospin, return_id=True):
                # Get the corresponding interatomic data container.
                pseudo_interatom = return_interatom(spin_id1=spin_id, spin_id2=base_spin_id)

                # Check.
                if pseudo_interatom == None:
                    raise RelaxError("The interatomic data container between the spins '%s' and '%s' for the pseudo-atom '%s' is not defined." % (base_spin_id, spin_id, pseudospin_id))

                # Add the vectors.
                if is_float(interatom.vector[0]):
                    pseudo_unit_vect.append([pseudo_interatom.vector])
                else:
                    pseudo_unit_vect.append(pseudo_interatom.vector)

                # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
                pseudo_rdc_const.append(3.0/(2.0*pi) * dipolar_constant(g1, g2, pseudo_interatom.r))

            # Reorder the unit vectors so that the structure and pseudo-atom dimensions are swapped.
            pseudo_unit_vect = transpose(array(pseudo_unit_vect, float64), (1, 0, 2))

            # Block append the pseudo-data.
            unit_vect.append(pseudo_unit_vect)
            rdc_const.append(pseudo_rdc_const)

        # Normal atom.
        else:
            # Set the flag.
            pseudo_flags.append(0)

            # Add the vectors.
            if is_float(interatom.vector[0]):
                unit_vect.append([interatom.vector])
            else:
                unit_vect.append(interatom.vector)

            # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
            rdc_const.append(3.0/(2.0*pi) * dipolar_constant(g1, g2, interatom.r))

        # Store the measured J coupling.
        if opt_uses_j_couplings():
            j_couplings.append(interatom.j_coupling)

    # Fix the unit vector data structure.
    num = None
    for rdc_index in range(len(unit_vect)):
        # Convert to numpy structures.
        unit_vect[rdc_index] = array(unit_vect[rdc_index], float64)

        # Number of vectors.
        if num == None:
            if unit_vect[rdc_index] != None:
                num = len(unit_vect[rdc_index])
            continue

        # Check.
        if unit_vect[rdc_index] != None and len(unit_vect[rdc_index]) != num:
            raise RelaxError("The number of interatomic vectors for all no match:\n%s" % unit_vect[rdc_index])

    # Missing unit vectors.
    if num == None:
        raise RelaxError("No interatomic vectors could be found.")

    # Update None entries.
    for i in range(len(unit_vect)):
        if unit_vect[i] == None:
            unit_vect[i] = [[None, None, None]]*num

    # The RDC data.
    for i in range(len(cdp.align_ids)):
        # Alias the ID.
        align_id = cdp.align_ids[i]

        # Skip non-optimised data.
        if not opt_uses_align_data(align_id):
            continue

        # Append empty arrays to the RDC structures.
        rdc.append([])
        rdc_err.append([])
        rdc_weight.append([])
        absolute.append([])
        T_flags.append([])

        # Interatom loop.
        j = 0
        for interatom in interatomic_loop():
            # Get the spins.
            spin1 = return_spin(interatom.spin_id1)
            spin2 = return_spin(interatom.spin_id2)

            # RDC checks.
            if not check_rdcs(interatom):
                continue

            # T-type data.
            if align_id in interatom.rdc_data_types and interatom.rdc_data_types[align_id] == 'T':
                T_flags[-1].append(True)
            else:
                T_flags[-1].append(False)

            # Check for J couplings if the RDC data type is T = J+D.
            if T_flags[-1][-1] and not hasattr(interatom, 'j_coupling'):
                continue

            # Defaults of None.
            value = None
            error = None

            # Normal set up.
            if align_id in interatom.rdc:
                # The RDC.
                if sim_index != None:
                    value = interatom.rdc_sim[align_id][sim_index]
                else:
                    value = interatom.rdc[align_id]

                # The error.
                if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err:
                    # T values.
                    if T_flags[-1][-1]:
                        error = sqrt(interatom.rdc_err[align_id]**2 + interatom.j_coupling_err**2)

                    # D values.
                    else:
                        error = interatom.rdc_err[align_id]

                # Increment the RDC count.
                if value != None:
                    j += 1

            # Append the RDCs to the list.
            rdc[-1].append(value)

            # Append the RDC errors.
            rdc_err[-1].append(error)

            # Append the weight.
            if hasattr(interatom, 'rdc_weight') and align_id in interatom.rdc_weight:
                rdc_weight[-1].append(interatom.rdc_weight[align_id])
            else:
                rdc_weight[-1].append(1.0)

            # Append the absolute value flag.
            if hasattr(interatom, 'absolute_rdc') and align_id in interatom.absolute_rdc:
                absolute[-1].append(interatom.absolute_rdc[align_id])
            else:
                absolute[-1].append(False)

        # ID and RDC count printout.
        if verbosity:
            print("    Alignment ID '%s':  %i" % (align_id, j))

    # Convert to numpy objects.
    rdc = array(rdc, float64)
    rdc_err = array(rdc_err, float64)
    rdc_weight = array(rdc_weight, float64)
    absolute = array(absolute, int32)
    T_flags = array(T_flags, int32)
    if not opt_uses_j_couplings():
        j_couplings = None
    pseudo_flags = array(pseudo_flags, int32)

    # Return the data structures.
    return rdc, rdc_err, rdc_weight, unit_vect, rdc_const, absolute, T_flags, j_couplings, pseudo_flags


def set_errors(align_id=None, spin_id1=None, spin_id2=None, sd=None):
    """Set the RDC errors if not already present.

    @keyword align_id:  The optional alignment tensor ID string.
    @type align_id:     str
    @keyword spin_id1:  The optional spin ID string of the first spin.
    @type spin_id1:     None or str
    @keyword spin_id2:  The optional spin ID string of the second spin.
    @type spin_id2:     None or str
    @keyword sd:        The RDC standard deviation in Hz.
    @type sd:           float or int.
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, rdc_id=align_id, rdc=True)

    # Convert the align IDs to an array, or take all IDs.
    if align_id:
        align_ids = [align_id]
    else:
        align_ids = cdp.rdc_ids

    # Loop over the interatomic data.
    for interatom in interatomic_loop(selection1=spin_id1, selection2=spin_id2):
        # No data structure.
        if not hasattr(interatom, 'rdc_err'):
            interatom.rdc_err = {}

        # Set the error.
        for id in align_ids:
            interatom.rdc_err[id] = sd


def setup_pseudoatom_rdc():
    """Make sure that the interatom system is properly set up for pseudo-atoms and RDCs.

    Interatomic data containers between the non-pseudo-atom and the pseudo-atom members will be deselected.
    """

    # Loop over all interatomic data containers.
    for interatom in interatomic_loop():
        # Get the spins.
        spin1 = return_spin(interatom.spin_id1)
        spin2 = return_spin(interatom.spin_id2)

        # Checks.
        flag1 = is_pseudoatom(spin1)
        flag2 = is_pseudoatom(spin2)

        # No pseudo-atoms, so do nothing.
        if not (flag1 or flag2):
            continue

        # Both are pseudo-atoms.
        if flag1 and flag2:
            warn(RelaxWarning("Support for both spins being in a dipole pair being pseudo-atoms is not implemented yet, deselecting the interatomic data container for the spin pair '%s' and '%s'." % (interatom.spin_id1, interatom.spin_id2)))
            interatom.select = False

        # Alias the pseudo and normal atoms.
        pseudospin = spin1
        base_spin_id = interatom.spin_id2
        pseudospin_id = interatom.spin_id1
        if flag2:
            pseudospin = spin2
            base_spin_id = interatom.spin_id1
            pseudospin_id = interatom.spin_id2

        # Loop over the atoms of the pseudo-atom.
        for spin, spin_id in pseudoatom_loop(pseudospin, return_id=True):
            # Get the corresponding interatomic data container.
            pseudo_interatom = return_interatom(spin_id1=spin_id, spin_id2=base_spin_id)

            # Deselect if needed.
            if pseudo_interatom.select:
                warn(RelaxWarning("Deselecting the interatomic data container for the spin pair '%s' and '%s' as it is part of the pseudo-atom system of the spin pair '%s' and '%s'." % (pseudo_interatom.spin_id1, pseudo_interatom.spin_id2, base_spin_id, pseudospin_id)))
                pseudo_interatom.select = False


def weight(align_id=None, spin_id=None, weight=1.0):
    """Set optimisation weights on the RDC data.

    @keyword align_id:  The alignment tensor ID string.
    @type align_id:     str
    @keyword spin_id:   The spin ID string.
    @type spin_id:      None or str
    @keyword weight:    The optimisation weight.  The higher the value, the more importance the RDC will have.
    @type weight:       float or int.
    """

    # Check the pipe setup.
    check_pipe_setup(sequence=True, rdc_id=align_id, rdc=True)

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

    # Check the pipe setup.
    check_pipe_setup(sequence=True, rdc_id=align_id, rdc=True)

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Loop over the interatomic data containers and collect the data.
    data = []
    for interatom in interatomic_loop():
        # Skip deselected containers.
        if not interatom.select:
            continue

        # Skip containers with no RDCs.
        if not bc and (not hasattr(interatom, 'rdc') or align_id not in interatom.rdc):
            continue
        elif bc and (not hasattr(interatom, 'rdc_bc') or align_id not in interatom.rdc_bc):
            continue

        # Append the spin data.
        data.append([])
        data[-1].append(repr(interatom.spin_id1))
        data[-1].append(repr(interatom.spin_id2))

        # Handle the missing rdc_data_types variable.
        data_type = None
        if hasattr(interatom, 'rdc_data_types'):
            data_type = interatom.rdc_data_types[align_id]

        # The value.
        if bc:
            data[-1].append(repr(convert(interatom.rdc_bc[align_id], data_type, align_id)))
        else:
            data[-1].append(repr(convert(interatom.rdc[align_id], data_type, align_id)))

        # The error.
        if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err:
            data[-1].append(repr(convert(interatom.rdc_err[align_id], data_type, align_id)))
        else:
            data[-1].append(repr(None))

    # Write out.
    write_data(out=file, headings=["Spin_ID1", "Spin_ID2", "RDCs", "RDC_error"], data=data)
