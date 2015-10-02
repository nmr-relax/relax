###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
"""Module for the optimisation of the frame order models."""

# Python module imports.
from math import cos, pi
from minfx.generic import generic_minimise
from minfx.grid import grid_point_array
from numpy import arccos, array, dot, float64, ones, zeros
from numpy.linalg import inv, norm
from re import search
import sys
from warnings import warn

# relax module imports.
from lib.float import isNaN, isInf
from lib.errors import RelaxError, RelaxInfError, RelaxNaNError, RelaxNoPCSError, RelaxNoRDCError
from lib.geometry.angles import wrap_angles
from lib.order import order_parameters
from lib.periodic_table import periodic_table
from lib.physical_constants import dipolar_constant
from lib.warnings import RelaxWarning
from multi import Memo, Result_command, Slave_command
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import return_spin, spin_loop
from pipe_control.structure.mass import pipe_centre_of_mass
from specific_analyses.frame_order.data import base_data_types, domain_moving, pivot_fixed, tensor_loop
from specific_analyses.frame_order.parameters import assemble_param_vector, assemble_scaling_matrix, linear_constraints
from specific_analyses.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_FREE_ROTOR, MODEL_RIGID, MODEL_ROTOR
from target_functions.frame_order import Frame_order


def grid_row(incs, lower, upper, dist_type=None, end_point=True):
    """Set up a row of the grid search for a given parameter.

    @param incs:        The number of increments.
    @type incs:         int
    @param lower:       The lower bounds.
    @type lower:        float
    @param upper:       The upper bounds.
    @type upper:        float
    @keyword dist_type: The spacing or distribution type between grid nodes.  If None, then a linear grid row is returned.  If 'acos', then an inverse cos distribution of points is returned (e.g. for uniform sampling in angular space).
    @type dist_type:    None or str
    @keyword end_point: A flag which if False will cause the end point to be removed.
    @type end_point:    bool
    @return:            The row of the grid.
    @rtype:             list of float
    """

    # Init.
    row = []

    # Linear grid.
    if dist_type == None:
        # Handle a single increment.
        if incs == 1:
            row.append((lower + upper) / 2.0)

        # Loop over the increments.
        else:
            for i in range(incs):
                row.append(lower + i * (upper - lower) / (incs - 1.0))

    # Inverse cos distribution.
    elif dist_type == 'acos':
        # Handle a single increment.
        if incs == 1:
            row.append((lower + upper) / 2.0)

        # Generate the increment values of v from cos(upper) to cos(lower).
        else:
            v = zeros(incs, float64)
            val = (cos(lower) - cos(upper)) / (incs - 1.0)
            for i in range(incs):
                v[-i-1] = cos(upper) + float(i) * val

            # Generate the distribution.
            row = arccos(v)

    # Remove the last point.
    if incs != 1 and not end_point:
        row = row[:-1]

    # Return the row (as a list).
    return list(row)


def minimise_setup_atomic_pos(sim_index=None):
    """Set up the atomic position data structures for optimisation using PCSs and PREs as base data sets.

    @keyword sim_index: The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:    None or int
    @return:            The atomic positions (the first index is the spins, the second is the structures, and the third is the atomic coordinates) and the paramagnetic centre.
    @rtype:             numpy rank-3 array, numpy rank-1 array.
    """

    # Initialise.
    atomic_pos = []

    # Store the atomic positions.
    for spin, spin_id in spin_loop(selection=domain_moving(), return_id=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # Only use spins with alignment/paramagnetic data.
        if not hasattr(spin, 'pcs') and not hasattr(spin, 'pre'):
            continue

        # A single atomic position.
        if spin.pos.shape == (3,):
            atomic_pos.append(spin.pos)

        # A single model (rank-2 array of a single position).
        elif spin.pos.shape == (1, 3):
            atomic_pos.append(spin.pos[0])

        # Average multiple atomic positions.
        else:
            # First throw a warning to tell the user what is happening.
            if sim_index == None:
                warn(RelaxWarning("Averaging the %s atomic positions for the PCS for the spin '%s'." % (len(spin.pos), spin_id)))

            # The average position.
            ave_pos = zeros(3, float64)
            for i in range(len(spin.pos)):
                ave_pos += spin.pos[i]
            ave_pos = ave_pos / len(spin.pos)

            # Store.
            atomic_pos.append(ave_pos)

    # Convert to numpy objects.
    atomic_pos = array(atomic_pos, float64)

    # The paramagnetic centre.
    if not hasattr(cdp, 'paramagnetic_centre'):
        paramag_centre = zeros(3, float64)
    else:
        paramag_centre = array(cdp.paramagnetic_centre)

    # Return the data structures.
    return atomic_pos, paramag_centre


def minimise_setup_pcs(sim_index=None):
    """Set up the data structures for optimisation using PCSs as base data sets.

    @keyword sim_index: The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:    None or int
    @return:            The assembled data structures for using PCSs as the base data for optimisation.  These include:
                            - the PCS values.
                            - the unit vectors connecting the paramagnetic centre (the electron spin) to
                            - the PCS weight.
                            - the nuclear spin.
                            - the pseudocontact shift constants.
    @rtype:             tuple of (numpy rank-2 array, numpy rank-2 array, numpy rank-2 array, numpy rank-1 array, numpy rank-1 array)
    """

    # Data setup tests.
    if not hasattr(cdp, 'paramagnetic_centre'):
        raise RelaxError("The paramagnetic centre has not yet been specified.")
    if not hasattr(cdp, 'temperature'):
        raise RelaxError("The experimental temperatures have not been set.")
    if not hasattr(cdp, 'spectrometer_frq'):
        raise RelaxError("The spectrometer frequencies of the experiments have not been set.")

    # Initialise.
    pcs = []
    pcs_err = []
    pcs_weight = []
    temp = []
    frq = []

    # The PCS data.
    for i in range(len(cdp.align_ids)):
        # Alias the ID.
        align_id = cdp.align_ids[i]

        # Skip non-optimised data.
        if not opt_uses_align_data(align_id):
            continue

        # Append empty arrays to the PCS structures.
        pcs.append([])
        pcs_err.append([])
        pcs_weight.append([])

        # Get the temperature for the PCS constant.
        if align_id in cdp.temperature:
            temp.append(cdp.temperature[align_id])

        # The temperature must be given!
        else:
            raise RelaxError("The experimental temperature for the alignment ID '%s' has not been set." % align_id)

        # Get the spectrometer frequency in Tesla units for the PCS constant.
        if align_id in cdp.spectrometer_frq:
            frq.append(cdp.spectrometer_frq[align_id] * 2.0 * pi / periodic_table.gyromagnetic_ratio('1H'))

        # The frequency must be given!
        else:
            raise RelaxError("The spectrometer frequency for the alignment ID '%s' has not been set." % align_id)

        # Spin loop over the domain.
        j = 0
        for spin in spin_loop(selection=domain_moving()):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins without PCS data.
            if not hasattr(spin, 'pcs'):
                continue

            # Append the PCSs to the list.
            if align_id in spin.pcs:
                if sim_index != None:
                    pcs[-1].append(spin.pcs_sim[align_id][sim_index])
                else:
                    pcs[-1].append(spin.pcs[align_id])
            else:
                pcs[-1].append(None)

            # Append the PCS errors.
            if hasattr(spin, 'pcs_err') and align_id in spin.pcs_err:
                pcs_err[-1].append(spin.pcs_err[align_id])
            else:
                pcs_err[-1].append(None)

            # Append the weight.
            if hasattr(spin, 'pcs_weight') and align_id in spin.pcs_weight:
                pcs_weight[-1].append(spin.pcs_weight[align_id])
            else:
                pcs_weight[-1].append(1.0)

            # Spin index.
            j = j + 1

    # Convert to numpy objects.
    pcs = array(pcs, float64)
    pcs_err = array(pcs_err, float64)
    pcs_weight = array(pcs_weight, float64)

    # Convert the PCS from ppm to no units.
    pcs = pcs * 1e-6
    pcs_err = pcs_err * 1e-6

    # Return the data structures.
    return pcs, pcs_err, pcs_weight, temp, frq


def minimise_setup_rdcs(sim_index=None):
    """Set up the data structures for optimisation using RDCs as base data sets.

    @keyword sim_index: The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:    None or int
    @return:            The assembled data structures for using RDCs as the base data for optimisation.  These include:
                            - rdc, the RDC values.
                            - rdc_err, the RDC errors.
                            - rdc_weight, the RDC weights.
                            - vectors, the interatomic vectors.
                            - rdc_const, the dipolar constants.
                            - absolute, the absolute value flags (as 1's and 0's).
    @rtype:             tuple of (numpy rank-2 array, numpy rank-2 array, numpy rank-2 array, numpy rank-3 array, numpy rank-2 array, numpy rank-2 array)
    """

    # Initialise.
    rdc = []
    rdc_err = []
    rdc_weight = []
    unit_vect = []
    rdc_const = []
    absolute = []

    # The unit vectors and RDC constants.
    for interatom in interatomic_loop(selection1=domain_moving()):
        # Get the spins.
        spin1 = return_spin(interatom.spin_id1)
        spin2 = return_spin(interatom.spin_id2)

        # A single unit vector.
        if interatom.vector.shape == (3,):
            unit_vect.append(interatom.vector)

        # Average multiple unit vectors.
        else:
            # First throw a warning to tell the user what is happening.
            if sim_index == None:
                warn(RelaxWarning("Averaging the %s unit vectors for the RDC for the spin pair '%s' and '%s'." % (len(interatom.vector), interatom.spin_id1, interatom.spin_id2)))

            # The average position.
            ave_vector = zeros(3, float64)
            for i in range(len(interatom.vector)):
                ave_vector += interatom.vector[i]

            # Store.
            unit_vect.append(ave_vector)

        # Normalise (to be sure).
        unit_vect[-1] = unit_vect[-1] / norm(unit_vect[-1])

        # Gyromagnetic ratios.
        g1 = periodic_table.gyromagnetic_ratio(spin1.isotope)
        g2 = periodic_table.gyromagnetic_ratio(spin2.isotope)

        # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
        rdc_const.append(3.0/(2.0*pi) * dipolar_constant(g1, g2, interatom.r))

    # Fix the unit vector data structure.
    num = None
    for rdc_index in range(len(unit_vect)):
        # Number of vectors.
        if num == None:
            if unit_vect[rdc_index] != None:
                num = len(unit_vect[rdc_index])
            continue

        # Check.
        if unit_vect[rdc_index] != None and len(unit_vect[rdc_index]) != num:
            raise RelaxError("The number of interatomic vectors for all no match:\n%s" % unit_vect)

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

        # Interatom loop over the domain.
        for interatom in interatomic_loop(domain_moving(), skip_desel=True):
            # Get the spins.
            spin1 = return_spin(interatom.spin_id1)
            spin2 = return_spin(interatom.spin_id2)

            # Only use interatomic data containers with RDC and vector data.
            if not hasattr(interatom, 'rdc') or not hasattr(interatom, 'vector'):
                continue

            # Defaults of None.
            value = None
            error = None

            # Pseudo-atom set up.
            if (hasattr(spin1, 'members') or hasattr(spin2, 'members')) and align_id in interatom.rdc:
                raise RelaxError("Psuedo-atoms are currently not supported for the frame order analysis.")

            # Normal set up.
            elif align_id in interatom.rdc:
                # The RDC.
                if sim_index != None:
                    value = interatom.rdc_sim[align_id][sim_index]
                else:
                    value = interatom.rdc[align_id]

                # The error.
                if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err:
                    error = interatom.rdc_err[align_id]

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

    # Convert to numpy objects.
    rdc = array(rdc, float64)
    rdc_err = array(rdc_err, float64)
    rdc_weight = array(rdc_weight, float64)
    unit_vect = array(unit_vect, float64)
    rdc_const = array(rdc_const, float64)
    absolute = array(absolute, float64)

    # Return the data structures.
    return rdc, rdc_err, rdc_weight, unit_vect, rdc_const, absolute


def minimise_setup_tensors(sim_index=None):
    """Set up the data structures for optimisation using alignment tensors as base data sets.

    @keyword sim_index: The simulation index.  This should be None if normal optimisation is desired.
    @type sim_index:    None or int
    @return:            The assembled data structures for using alignment tensors as the base data for optimisation.  These include:
                            - full_tensors, the full tensors as concatenated arrays.
                            - full_err, the full tensor errors as concatenated arrays.
                            - full_in_ref_frame, the flags specifying if the tensor is the full or reduced tensor in the non-moving reference domain.
    @rtype:             tuple of 3 numpy nx5D, rank-1 arrays
    """

    # Checks.
    if not hasattr(cdp, 'ref_domain'):
        raise RelaxError("The reference domain has not been set up.")
    if not hasattr(cdp.align_tensors, 'reduction'):
        raise RelaxError("The tensor reductions have not been specified.")
    for i, tensor in tensor_loop():
        if not hasattr(tensor, 'domain'):
            raise RelaxError("The domain that the '%s' tensor is attached to has not been set" % tensor.name)

    # Initialise.
    n = len(cdp.align_tensors.reduction)
    full_tensors = zeros(n*5, float64)
    full_err = ones(n*5, float64) * 1e-5
    full_in_ref_frame = zeros(n, float64)

    # Loop over the full tensors.
    for i, tensor in tensor_loop(red=False):
        # The full tensor.
        full_tensors[5*i + 0] = tensor.Axx
        full_tensors[5*i + 1] = tensor.Ayy
        full_tensors[5*i + 2] = tensor.Axy
        full_tensors[5*i + 3] = tensor.Axz
        full_tensors[5*i + 4] = tensor.Ayz

        # The full tensor corresponds to the frame of reference.
        if cdp.ref_domain == tensor.domain:
            full_in_ref_frame[i] = 1

        # The full tensor errors.
        if hasattr(tensor, 'Axx_err'):
            full_err[5*i + 0] = tensor.Axx_err
            full_err[5*i + 1] = tensor.Ayy_err
            full_err[5*i + 2] = tensor.Axy_err
            full_err[5*i + 3] = tensor.Axz_err
            full_err[5*i + 4] = tensor.Ayz_err

    # Return the data structures.
    return full_tensors, full_err, full_in_ref_frame


def opt_uses_align_data(align_id=None):
    """Determine if the PCS or RDC data for the given alignment ID is needed for optimisation.

    @keyword align_id:  The optional alignment ID string.
    @type align_id:     str
    @return:            True if alignment data is to be used for optimisation, False otherwise.
    @rtype:             bool
    """

    # No alignment IDs.
    if not hasattr(cdp, 'align_ids'):
        return False

    # Convert the align IDs to an array, or take all IDs.
    if align_id:
        align_ids = [align_id]
    else:
        align_ids = cdp.align_ids

    # Check the PCS and RDC.
    for align_id in align_ids:
        if opt_uses_pcs(align_id) or opt_uses_rdc(align_id):
            return True

    # No alignment data is used for optimisation.
    return False


def opt_uses_pcs(align_id):
    """Determine if the PCS data for the given alignment ID is needed for optimisation.

    @param align_id:    The alignment ID string.
    @type align_id:     str
    @return:            True if the PCS data is to be used for optimisation, False otherwise.
    @rtype:             bool
    """

    # No alignment IDs.
    if not hasattr(cdp, 'pcs_ids'):
        return False

    # No PCS data for the alignment.
    if align_id not in cdp.pcs_ids:
        return False

    # The PCS data is to be used for optimisation.
    return True


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

    # The RDC data is to be used for optimisation.
    return True


def store_bc_data(A_5D_bc=None, pcs_theta=None, rdc_theta=None):
    """Store the back-calculated data.

    @keyword A_5D_bc:       The reduced back-calculated alignment tensors from the target function.
    @type A_5D_bc:          numpy float64 array
    @keyword pcs_theta:     The back calculated PCS values from the target function.
    @type pcs_theta:        numpy float64 array
    @keyword rdc_theta:     The back calculated RDC values from the target function.
    @type rdc_theta:        numpy float64 array
    """

    # Loop over the reduced tensors.
    for i, tensor in tensor_loop(red=True):
        # Store the values.
        tensor.set(param='Axx', value=A_5D_bc[5*i + 0])
        tensor.set(param='Ayy', value=A_5D_bc[5*i + 1])
        tensor.set(param='Axy', value=A_5D_bc[5*i + 2])
        tensor.set(param='Axz', value=A_5D_bc[5*i + 3])
        tensor.set(param='Ayz', value=A_5D_bc[5*i + 4])

    # The RDC data.
    for i in range(len(cdp.align_ids)):
        # The alignment ID.
        align_id = cdp.align_ids[i]

        # Data flags
        rdc_flag = False
        if hasattr(cdp, 'rdc_ids') and align_id in cdp.rdc_ids:
            rdc_flag = True
        pcs_flag = False
        if hasattr(cdp, 'pcs_ids') and align_id in cdp.pcs_ids:
            pcs_flag = True

        # Spin loop over the domain.
        pcs_index = 0
        for spin in spin_loop(domain_moving()):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Spins with PCS data.
            if pcs_flag and hasattr(spin, 'pcs'):
                # Initialise the data structure.
                if not hasattr(spin, 'pcs_bc'):
                    spin.pcs_bc = {}

                # Store the back-calculated value (in ppm).
                spin.pcs_bc[align_id] = pcs_theta[i, pcs_index] * 1e6

                # Increment the index.
                pcs_index += 1

        # Interatomic data container loop.
        rdc_index = 0
        for interatom in interatomic_loop(domain_moving(), skip_desel=True):
            # Initialise the data structure.
            if not hasattr(interatom, 'rdc_bc'):
                interatom.rdc_bc = {}

            # Store the back-calculated value.
            interatom.rdc_bc[align_id] = rdc_theta[i, rdc_index]

            # Increment the index.
            rdc_index += 1


def target_fn_data_setup(sim_index=None, verbosity=1, scaling_matrix=None, unset_fail=False):
    """Initialise the target function for optimisation or direct calculation.

    @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:            None or int
    @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:            int
    @keyword scaling_matrix:    The diagonal and square scaling matrices.
    @type scaling_matrix:       numpy rank-2, float64 array or None
    @keyword unset_fail:        A flag which if True will cause a RelaxError to be raised if the parameter is not set yet.
    @type unset_fail:           bool
    """

    # Assemble the parameter vector.
    param_vector = assemble_param_vector(sim_index=sim_index, unset_fail=unset_fail)

    # Determine the base data types (RDCs and/or PCSs).
    data_types = base_data_types()

    # Diagonal scaling.
    if scaling_matrix != None and len(param_vector):
        param_vector = dot(inv(scaling_matrix), param_vector)

    # Get the data structures for optimisation using the tensors as base data sets.
    full_tensors, full_tensor_err, full_in_ref_frame = minimise_setup_tensors(sim_index)

    # Get the data structures for optimisation using PCSs as base data sets.
    pcs, pcs_err, pcs_weight, temp, frq = None, None, None, None, None
    if 'pcs' in data_types:
        pcs, pcs_err, pcs_weight, temp, frq = minimise_setup_pcs(sim_index=sim_index)

    # Get the data structures for optimisation using RDCs as base data sets.
    rdcs, rdc_err, rdc_weight, rdc_vect, rdc_const, absolute_rdc = None, None, None, None, None, None
    if 'rdc' in data_types:
        rdcs, rdc_err, rdc_weight, rdc_vect, rdc_const, absolute_rdc = minimise_setup_rdcs(sim_index=sim_index)

    # Data checks.
    if pcs != None and not len(pcs):
        raise RelaxNoPCSError
    if rdcs != None and not len(rdcs):
        raise RelaxNoRDCError

    # Get the atomic_positions.
    atomic_pos, paramag_centre = None, None
    if 'pcs' in data_types or 'pre' in data_types:
        atomic_pos, paramag_centre = minimise_setup_atomic_pos(sim_index=sim_index)

    # The fixed pivot point.
    pivot = None
    if hasattr(cdp, 'pivot_x'):
        pivot = array([cdp.pivot_x, cdp.pivot_y, cdp.pivot_z])

    # Pivot optimisation.
    pivot_opt = True
    if pivot_fixed():
        pivot_opt = False

    # The number of integration points.
    if not hasattr(cdp, 'num_int_pts'):
        cdp.num_int_pts = 200000

    # The centre of mass of the moving domain - to use as the centroid for the average domain position rotation.
    ave_pos_pivot = pipe_centre_of_mass(atom_id=domain_moving(), verbosity=0)

    # The centre of mass, for use in the rotor models.
    com = None
    if cdp.model in [MODEL_ROTOR, MODEL_FREE_ROTOR, MODEL_DOUBLE_ROTOR]:
        # The centre of mass of all objects in the data pipe.
        com = pipe_centre_of_mass(verbosity=0)
        com = array(com, float64)

    # Information printout.
    if verbosity and sim_index == None:
        sys.stdout.write("\nThe average domain rotation centroid, taken as the CoM of the atoms defined as the moving domain, is:\n    %s\n" % list(ave_pos_pivot))
        if com != None:
            sys.stdout.write("The centre of mass reference coordinate for the rotor models is:\n    %s\n" % list(com))
        if cdp.model != MODEL_RIGID:
            sys.stdout.write("Numerical integration:  Quasi-random Sobol' sequence.\n")
            sys.stdout.write("Number of integration points:  %s\n" % cdp.num_int_pts)
        base_data = []
        if rdcs != None and len(rdcs):
            base_data.append("RDCs")
        if pcs != None and len(pcs):
            base_data.append("PCSs")
        sys.stdout.write("Base data: %s\n" % repr(base_data))
        sys.stdout.write("\n")

    # Return the data.
    return param_vector, full_tensors, full_in_ref_frame, rdcs, rdc_err, rdc_weight, rdc_vect, rdc_const, pcs, pcs_err, pcs_weight, atomic_pos, temp, frq, paramag_centre, com, ave_pos_pivot, pivot, pivot_opt


def unpack_opt_results(param_vector=None, func=None, iter_count=None, f_count=None, g_count=None, h_count=None, warning=None, scaling_matrix=None, sim_index=None):
    """Unpack and store the Frame Order optimisation results.

    @keyword param_vector:      The model-free parameter vector.
    @type param_vector:         numpy array
    @keyword func:              The optimised chi-squared value.
    @type func:                 float
    @keyword iter_count:        The number of optimisation steps required to find the minimum.
    @type iter_count:           int
    @keyword f_count:           The function count.
    @type f_count:              int
    @keyword g_count:           The gradient count.
    @type g_count:              int
    @keyword h_count:           The Hessian count.
    @type h_count:              int
    @keyword warning:           Any optimisation warnings.
    @type warning:              str or None
    @keyword scaling_matrix:    The diagonal and square scaling matrices.
    @type scaling_matrix:       numpy rank-2, float64 array or None
    @keyword sim_index:         The index of the simulation to optimise.  This should be None for normal optimisation.
    @type sim_index:            None or int
     """

    # Catch infinite chi-squared values.
    if isInf(func):
        raise RelaxInfError('chi-squared')

    # Catch chi-squared values of NaN.
    if isNaN(func):
        raise RelaxNaNError('chi-squared')

    # Scaling.
    if scaling_matrix != None:
        param_vector = dot(scaling_matrix, param_vector)

    # The parameters to wrap.
    wrap = [
        'ave_pos_alpha',
        'ave_pos_beta',
        'ave_pos_gamma',
        'eigen_alpha',
        'eigen_beta',
        'eigen_gamma',
        'axis_theta',
        'axis_phi'
    ]

    # Monte Carlo simulation data structures.
    if sim_index != None:
        # Loop over the parameters.
        for i in range(len(cdp.params)):
            # Angle wrapping around the real value.
            if cdp.params[i] in wrap or cdp.params[i] == 'axis_alpha':
                val = getattr(cdp, cdp.params[i])
                param_vector[i] = wrap_angles(param_vector[i], val-pi, val+pi)

            # Store the value.
            obj = getattr(cdp, cdp.params[i]+'_sim')
            obj[sim_index] = param_vector[i]

            # Order parameter to angle conversion.
            if cdp.params[i] == 'cone_s1':
                cdp.cone_theta_sim[sim_index] = order_parameters.iso_cone_S_to_theta(param_vector[i])

        # Optimisation stats.
        cdp.chi2_sim[sim_index] = func
        cdp.iter_sim[sim_index] = iter_count
        cdp.f_count_sim[sim_index] = f_count
        cdp.g_count_sim[sim_index] = g_count
        cdp.h_count_sim[sim_index] = h_count
        cdp.warning_sim[sim_index] = warning

    # Normal data structures.
    else:
        # Loop over the parameters.
        for i in range(len(cdp.params)):
            # Angle wrapping.
            if cdp.params[i] in wrap:
                param_vector[i] = wrap_angles(param_vector[i], 0.0, 2.0*pi)
            if cdp.params[i] == 'axis_alpha':
                param_vector[i] = wrap_angles(param_vector[i], -pi, pi)

            # Store the value.
            setattr(cdp, cdp.params[i], param_vector[i])

            # Order parameter to angle conversion.
            if cdp.params[i] == 'cone_s1':
                cdp.cone_theta = order_parameters.iso_cone_S_to_theta(param_vector[i])

        # Optimisation stats.
        cdp.chi2 = func
        cdp.iter = iter_count
        cdp.f_count = f_count
        cdp.g_count = g_count
        cdp.h_count = h_count
        cdp.warning = warning



class Frame_order_grid_command(Slave_command):
    """Command class for relaxation dispersion optimisation on the slave processor."""

    def __init__(self, points=None, scaling_matrix=None, sim_index=None, model=None, param_vector=None, full_tensors=None, full_in_ref_frame=None, rdcs=None, rdc_err=None, rdc_weight=None, rdc_vect=None, rdc_const=None, pcs=None, pcs_err=None, pcs_weight=None, atomic_pos=None, temp=None, frq=None, paramag_centre=None, com=None, ave_pos_pivot=None, pivot=None, pivot_opt=None, num_int_pts=None, verbosity=None):
        """Initialise the base class, storing all the master data to be sent to the slave processor.

        This method is run on the master processor whereas the run() method is run on the slave processor.

        @keyword points:            The points of the grid search subdivision to search over.
        @type points:               numpy rank-2 array
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword model:             The name of the Frame Order model.
        @type model:                str
        @keyword param_vector:      The initial parameter values.
        @type param_vector:         numpy float64 array
        @keyword full_tensors:      An array of the {Axx, Ayy, Axy, Axz, Ayz} values for all full alignment tensors.  The format is [Axx1, Ayy1, Axy1, Axz1, Ayz1, Axx2, Ayy2, Axy2, Axz2, Ayz2, ..., Axxn, Ayyn, Axyn, Axzn, Ayzn].
        @type full_tensors:         numpy nx5D, rank-1 float64 array
        @keyword full_in_ref_frame: An array of flags specifying if the tensor in the reference frame is the full or reduced tensor.
        @type full_in_ref_frame:    numpy rank-1 array
        @keyword rdcs:              The RDC lists.  The first index must correspond to the different alignment media i and the second index to the spin systems j.
        @type rdcs:                 numpy rank-2 array
        @keyword rdc_err:           The RDC error lists.  The dimensions of this argument are the same as for 'rdcs'.
        @type rdc_err:              numpy rank-2 array
        @keyword rdc_weight:        The RDC weight lists.  The dimensions of this argument are the same as for 'rdcs'.
        @type rdc_weight:           numpy rank-2 array
        @keyword rdc_vect:          The unit XH vector lists corresponding to the RDC values.  The first index must correspond to the spin systems and the second index to the x, y, z elements.
        @type rdc_vect:             numpy rank-2 array
        @keyword rdc_const:         The dipolar constants for each RDC.  The indices correspond to the spin systems j.
        @type rdc_const:            numpy rank-1 array
        @keyword pcs:               The PCS lists.  The first index must correspond to the different alignment media i and the second index to the spin systems j.
        @type pcs:                  numpy rank-2 array
        @keyword pcs_err:           The PCS error lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_err:              numpy rank-2 array
        @keyword pcs_weight:        The PCS weight lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_weight:           numpy rank-2 array
        @keyword atomic_pos:        The atomic positions of all spins for the PCS and PRE data.  The first index is the spin systems j and the second is the structure or state c.
        @type atomic_pos:           numpy rank-3 array
        @keyword temp:              The temperature of each PCS data set.
        @type temp:                 numpy rank-1 array
        @keyword frq:               The frequency of each PCS data set.
        @type frq:                  numpy rank-1 array
        @keyword paramag_centre:    The paramagnetic centre position (or positions).
        @type paramag_centre:       numpy rank-1, 3D array or rank-2, Nx3 array
         @keyword com:               The centre of mass of the system.  This is used for defining the rotor model systems.
        @type com:                  numpy 3D rank-1 array
        @keyword ave_pos_pivot:     The pivot point to rotate all atoms about to the average domain position.  In most cases this will be the centre of mass of the moving domain.  This pivot is shifted by the translation vector.
        @type ave_pos_pivot:        numpy 3D rank-1 array
        @keyword pivot:             The pivot point for the ball-and-socket joint motion.  This is needed if PCS or PRE values are used.
        @type pivot:                numpy rank-1, 3D array or None
        @keyword pivot_opt:         A flag which if True will allow the pivot point of the motion to be optimised.
        @type pivot_opt:            bool
        @keyword num_int_pts:       The number of points to use for the numerical integration technique.
        @type num_int_pts:          int
        @keyword verbosity:         The verbosity level.  This is used by the result command returned to the master for printouts.
        @type verbosity:            int
        """

        # Store the arguments.
        self.points = points
        self.scaling_matrix = scaling_matrix
        self.model = model
        self.param_vector = param_vector
        self.full_tensors = full_tensors
        self.full_in_ref_frame = full_in_ref_frame
        self.rdcs = rdcs
        self.rdc_err = rdc_err
        self.rdc_weight = rdc_weight
        self.rdc_vect = rdc_vect
        self.rdc_const = rdc_const
        self.pcs = pcs
        self.pcs_err = pcs_err
        self.pcs_weight = pcs_weight
        self.atomic_pos = atomic_pos
        self.temp = temp
        self.frq = frq
        self.paramag_centre = paramag_centre
        self.com = com
        self.ave_pos_pivot = ave_pos_pivot
        self.pivot = pivot
        self.pivot_opt = pivot_opt
        self.num_int_pts = num_int_pts
        self.verbosity = verbosity


    def run(self, processor, completed):
        """Set up and perform the optimisation."""

        # Set up the optimisation target function class.
        target_fn = Frame_order(model=self.model, init_params=self.param_vector, full_tensors=self.full_tensors, full_in_ref_frame=self.full_in_ref_frame, rdcs=self.rdcs, rdc_errors=self.rdc_err, rdc_weights=self.rdc_weight, rdc_vect=self.rdc_vect, dip_const=self.rdc_const, pcs=self.pcs, pcs_errors=self.pcs_err, pcs_weights=self.pcs_weight, atomic_pos=self.atomic_pos, temp=self.temp, frq=self.frq, paramag_centre=self.paramag_centre, scaling_matrix=self.scaling_matrix, com=self.com, ave_pos_pivot=self.ave_pos_pivot, pivot=self.pivot, pivot_opt=self.pivot_opt, num_int_pts=self.num_int_pts)

        # Grid search.
        results = grid_point_array(func=target_fn.func, args=(), points=self.points, verbosity=self.verbosity)

        # Create the result command object on the slave to send back to the master.
        processor.return_object(Frame_order_result_command(processor=processor, memo_id=self.memo_id, results=results, A_5D_bc=target_fn.A_5D_bc, pcs_theta=target_fn.pcs_theta, rdc_theta=target_fn.rdc_theta, completed=completed))



class Frame_order_memo(Memo):
    """The frame order memo class."""

    def __init__(self, spins=None, spin_ids=None, sim_index=None, scaling_matrix=None, verbosity=None):
        """Initialise the relaxation dispersion memo class.

        This is used for handling the optimisation results returned from a slave processor.  It runs on the master processor and is used to store data which is passed to the slave processor and then passed back to the master via the results command.


        @keyword spins:             The list of spin data container for the cluster.  If this argument is supplied, then the spin_id argument will be ignored.
        @type spins:                list of SpinContainer instances
        @keyword spin_ids:          The spin ID strings for the cluster.
        @type spin_ids:             list of str
        @keyword sim_index:         The optional MC simulation index.
        @type sim_index:            int
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        @keyword verbosity:         The verbosity level.  This is used by the result command returned to the master for printouts.
        @type verbosity:            int
        """

        # Execute the base class __init__() method.
        super(Frame_order_memo, self).__init__()

        # Store the arguments.
        self.spins = spins
        self.spin_ids = spin_ids
        self.sim_index = sim_index
        self.scaling_matrix = scaling_matrix



class Frame_order_minimise_command(Slave_command):
    """Command class for relaxation dispersion optimisation on the slave processor."""

    def __init__(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, scaling_matrix=None, constraints=False, sim_index=None, model=None, param_vector=None, full_tensors=None, full_in_ref_frame=None, rdcs=None, rdc_err=None, rdc_weight=None, rdc_vect=None, rdc_const=None, pcs=None, pcs_err=None, pcs_weight=None, atomic_pos=None, temp=None, frq=None, paramag_centre=None, com=None, ave_pos_pivot=None, pivot=None, pivot_opt=None, num_int_pts=None, verbosity=None):
        """Initialise the base class, storing all the master data to be sent to the slave processor.

        This method is run on the master processor whereas the run() method is run on the slave processor.

        @keyword min_algor:         The minimisation algorithm to use.
        @type min_algor:            str
        @keyword min_options:       An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword constraints:       If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword model:             The name of the Frame Order model.
        @type model:                str
        @keyword param_vector:      The initial parameter values.
        @type param_vector:         numpy float64 array
        @keyword full_tensors:      An array of the {Axx, Ayy, Axy, Axz, Ayz} values for all full alignment tensors.  The format is [Axx1, Ayy1, Axy1, Axz1, Ayz1, Axx2, Ayy2, Axy2, Axz2, Ayz2, ..., Axxn, Ayyn, Axyn, Axzn, Ayzn].
        @type full_tensors:         numpy nx5D, rank-1 float64 array
        @keyword full_in_ref_frame: An array of flags specifying if the tensor in the reference frame is the full or reduced tensor.
        @type full_in_ref_frame:    numpy rank-1 array
        @keyword rdcs:              The RDC lists.  The first index must correspond to the different alignment media i and the second index to the spin systems j.
        @type rdcs:                 numpy rank-2 array
        @keyword rdc_err:           The RDC error lists.  The dimensions of this argument are the same as for 'rdcs'.
        @type rdc_err:              numpy rank-2 array
        @keyword rdc_weight:        The RDC weight lists.  The dimensions of this argument are the same as for 'rdcs'.
        @type rdc_weight:           numpy rank-2 array
        @keyword rdc_vect:          The unit XH vector lists corresponding to the RDC values.  The first index must correspond to the spin systems and the second index to the x, y, z elements.
        @type rdc_vect:             numpy rank-2 array
        @keyword rdc_const:         The dipolar constants for each RDC.  The indices correspond to the spin systems j.
        @type rdc_const:            numpy rank-1 array
        @keyword pcs:               The PCS lists.  The first index must correspond to the different alignment media i and the second index to the spin systems j.
        @type pcs:                  numpy rank-2 array
        @keyword pcs_err:           The PCS error lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_err:              numpy rank-2 array
        @keyword pcs_weight:        The PCS weight lists.  The dimensions of this argument are the same as for 'pcs'.
        @type pcs_weight:           numpy rank-2 array
        @keyword atomic_pos:        The atomic positions of all spins for the PCS and PRE data.  The first index is the spin systems j and the second is the structure or state c.
        @type atomic_pos:           numpy rank-3 array
        @keyword temp:              The temperature of each PCS data set.
        @type temp:                 numpy rank-1 array
        @keyword frq:               The frequency of each PCS data set.
        @type frq:                  numpy rank-1 array
        @keyword paramag_centre:    The paramagnetic centre position (or positions).
        @type paramag_centre:       numpy rank-1, 3D array or rank-2, Nx3 array
         @keyword com:               The centre of mass of the system.  This is used for defining the rotor model systems.
        @type com:                  numpy 3D rank-1 array
        @keyword ave_pos_pivot:     The pivot point to rotate all atoms about to the average domain position.  In most cases this will be the centre of mass of the moving domain.  This pivot is shifted by the translation vector.
        @type ave_pos_pivot:        numpy 3D rank-1 array
        @keyword pivot:             The pivot point for the ball-and-socket joint motion.  This is needed if PCS or PRE values are used.
        @type pivot:                numpy rank-1, 3D array or None
        @keyword pivot_opt:         A flag which if True will allow the pivot point of the motion to be optimised.
        @type pivot_opt:            bool
        @keyword num_int_pts:       The number of points to use for the numerical integration technique.
        @type num_int_pts:          int
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        """

        # Store some arguments.
        self.min_algor = min_algor
        self.min_options = min_options
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.max_iterations = max_iterations
        self.scaling_matrix = scaling_matrix
        self.model = model
        self.param_vector = param_vector
        self.full_tensors = full_tensors
        self.full_in_ref_frame = full_in_ref_frame
        self.rdcs = rdcs
        self.rdc_err = rdc_err
        self.rdc_weight = rdc_weight
        self.rdc_vect = rdc_vect
        self.rdc_const = rdc_const
        self.pcs = pcs
        self.pcs_err = pcs_err
        self.pcs_weight = pcs_weight
        self.atomic_pos = atomic_pos
        self.temp = temp
        self.frq = frq
        self.paramag_centre = paramag_centre
        self.com = com
        self.ave_pos_pivot = ave_pos_pivot
        self.pivot = pivot
        self.pivot_opt = pivot_opt
        self.num_int_pts = num_int_pts
        self.verbosity = verbosity

        # Linear constraints.
        self.A, self.b = None, None
        if constraints:
            # Obtain the constraints.
            self.A, self.b = linear_constraints(scaling_matrix=scaling_matrix)

            # Constraint flag set but no constraints present.
            if self.A == None:
                if verbosity:
                    warn(RelaxWarning("The '%s' model parameters are not constrained, turning the linear constraint algorithm off." % cdp.model))

                # Pop out the log barrier algorithm.
                if self.min_algor == 'Log barrier':
                    self.min_algor = self.min_options[0]
                    self.min_options = self.min_options[1:]


    def run(self, processor, completed):
        """Set up and perform the optimisation."""

        # Set up the optimisation target function class.
        target_fn = Frame_order(model=self.model, init_params=self.param_vector, full_tensors=self.full_tensors, full_in_ref_frame=self.full_in_ref_frame, rdcs=self.rdcs, rdc_errors=self.rdc_err, rdc_weights=self.rdc_weight, rdc_vect=self.rdc_vect, dip_const=self.rdc_const, pcs=self.pcs, pcs_errors=self.pcs_err, pcs_weights=self.pcs_weight, atomic_pos=self.atomic_pos, temp=self.temp, frq=self.frq, paramag_centre=self.paramag_centre, scaling_matrix=self.scaling_matrix, com=self.com, ave_pos_pivot=self.ave_pos_pivot, pivot=self.pivot, pivot_opt=self.pivot_opt, num_int_pts=self.num_int_pts)

        # Minimisation.
        results = generic_minimise(func=target_fn.func, args=(), x0=self.param_vector, min_algor=self.min_algor, min_options=self.min_options, func_tol=self.func_tol, grad_tol=self.grad_tol, maxiter=self.max_iterations, A=self.A, b=self.b, full_output=True, print_flag=self.verbosity)

        # Create the result command object on the slave to send back to the master.
        processor.return_object(Frame_order_result_command(processor=processor, memo_id=self.memo_id, results=results, A_5D_bc=target_fn.A_5D_bc, pcs_theta=target_fn.pcs_theta, rdc_theta=target_fn.rdc_theta, completed=completed))



class Frame_order_result_command(Result_command):
    """Class for processing the frame order results.

    This object will be sent from the slave back to the master to have its run() method executed.
    """

    def __init__(self, processor=None, memo_id=None, results=None, A_5D_bc=None, pcs_theta=None, rdc_theta=None, completed=False):
        """Set up the class, placing the minimisation results here.

        @keyword processor:     The processor object.
        @type processor:        multi.processor.Processor instance
        @keyword memo_id:       The memo identification string.
        @type memo_id:          str
        @keyword results:       The results as returned by minfx.
        @type results:          tuple
        @keyword A_5D_bc:       The reduced back-calculated alignment tensors from the target function.
        @type A_5D_bc:          numpy float64 array
        @keyword pcs_theta:     The back calculated PCS values from the target function.
        @type pcs_theta:        numpy float64 array
        @keyword rdc_theta:     The back calculated RDC values from the target function.
        @type rdc_theta:        numpy float64 array
        @keyword model:         The target function class instance which has been optimised.
        @type model:            class instance
        @keyword completed:     A flag which if True signals that the optimisation successfully completed.
        @type completed:        bool
        """

        # Execute the base class __init__() method.
        super(Frame_order_result_command, self).__init__(processor=processor, completed=completed)

        # Store the arguments.
        self.memo_id = memo_id
        self.results = results
        self.A_5D_bc = A_5D_bc
        self.pcs_theta = pcs_theta
        self.rdc_theta = rdc_theta


    def run(self, processor, memo):
        """Disassemble the frame order optimisation results.

        @param processor:   Unused!
        @type processor:    None
        @param memo:        The model-free memo.
        @type memo:         memo
        """

        # Printout.
        if memo.sim_index != None:
            print("Simulation %i" % (memo.sim_index+1))

        # Disassemble the results.
        if len(self.results) == 4:    # Grid search.
            param_vector, func, iter_count, warning = self.results
            f_count = iter_count
            g_count = 0.0
            h_count = 0.0
        else:
            param_vector, func, iter_count, f_count, g_count, h_count, warning = self.results

        # Check if the chi-squared value is lower - required for a parallelised grid search to work.
        if memo.sim_index == None:
            if hasattr(cdp, 'chi2') and cdp.chi2 != None:
                # No improvement, so exit the function.
                if func > cdp.chi2:
                    print("Discarding the optimisation results, the optimised chi-squared value is higher than the current value (%s > %s)." % (func, cdp.chi2))
                    return

                # New minimum.
                print("Storing the optimisation results, the optimised chi-squared value is lower than the current value (%s < %s)." % (func, cdp.chi2))

            # Just print something to avoid user confusion in parallelised grid searches.
            else:
                print("Storing the optimisation results, no optimised values currently exist.")

        # Unpack the results.
        unpack_opt_results(param_vector, func, iter_count, f_count, g_count, h_count, warning, memo.scaling_matrix, memo.sim_index)

        # Store the back-calculated data.
        store_bc_data(A_5D_bc=self.A_5D_bc, pcs_theta=self.pcs_theta, rdc_theta=self.rdc_theta)
