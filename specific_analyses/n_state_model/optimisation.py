###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
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
"""The N-state model or structural ensemble analysis optimisation functions."""

# Python module imports.
from numpy import array, dot, float64, ones, zeros
from numpy.linalg import inv
from numpy.ma import fix_invalid

# relax module imports.
from lib.errors import RelaxError, RelaxNoModelError
from pipe_control import align_tensor
from pipe_control.align_tensor import opt_uses_align_data, opt_uses_tensor
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import return_spin, spin_loop
from pipe_control.pcs import return_pcs_data
from pipe_control.rdc import check_rdcs, return_rdc_data
from specific_analyses.n_state_model.data import base_data_types, tensor_loop
from specific_analyses.n_state_model.parameters import assemble_param_vector, update_model
from target_functions.n_state_model import N_state_opt


def minimise_bc_data(model):
    """Extract and unpack the back calculated data.

    @param model:   The instantiated class containing the target function.
    @type model:    class instance
    """

    # No alignment tensors, so nothing to do.
    if not hasattr(cdp, 'align_tensors'):
        return

    # Loop over each alignment.
    align_index = 0
    for i in range(len(cdp.align_ids)):
        # Skip non-optimised tensors.
        if not opt_uses_tensor(cdp.align_tensors[i]):
            continue

        # The alignment ID.
        align_id = cdp.align_ids[i]

        # Data flags
        rdc_flag = False
        if hasattr(cdp, 'rdc_ids') and align_id in cdp.rdc_ids:
            rdc_flag = True
        pcs_flag = False
        if hasattr(cdp, 'pcs_ids') and align_id in cdp.pcs_ids:
            pcs_flag = True

        # Spin loop.
        pcs_index = 0
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Spins with PCS data.
            if pcs_flag and hasattr(spin, 'pcs'):
                # Initialise the data structure if necessary.
                if not hasattr(spin, 'pcs_bc'):
                    spin.pcs_bc = {}

                # Add the back calculated PCS (in ppm).
                spin.pcs_bc[align_id] = model.deltaij_theta[align_index, pcs_index] * 1e6

                # Increment the data index if the spin container has data.
                pcs_index = pcs_index + 1

        # Interatomic data container loop.
        rdc_index = 0
        for interatom in interatomic_loop():
            # Get the spins.
            spin1 = return_spin(interatom.spin_id1)
            spin2 = return_spin(interatom.spin_id2)

            # RDC checks.
            if not check_rdcs(interatom):
                continue

            # Containers with RDC data.
            if rdc_flag and hasattr(interatom, 'rdc'):
                # Initialise the data structure if necessary.
                if not hasattr(interatom, 'rdc_bc'):
                    interatom.rdc_bc = {}

                # Append the back calculated PCS.
                interatom.rdc_bc[align_id] = model.rdc_theta[align_index, rdc_index]

                # Increment the data index if the interatom container has data.
                rdc_index = rdc_index + 1

        # Increment the alignment index (for the optimised tensors).
        align_index += 1


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
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # Only use spins with alignment/paramagnetic data.
        if not hasattr(spin, 'pcs') and not hasattr(spin, 'pre'):
            continue

        # The position list.
        if type(spin.pos[0]) in [float, float64]:
            atomic_pos.append([spin.pos])
        else:
            atomic_pos.append(spin.pos)

    # Convert to numpy objects.
    atomic_pos = array(atomic_pos, float64)

    # The paramagnetic centre.
    if not hasattr(cdp, 'paramagnetic_centre'):
        paramag_centre = zeros(3, float64)
    elif sim_index != None and not cdp.paramag_centre_fixed:
        if not hasattr(cdp, 'paramagnetic_centre_sim') or cdp.paramagnetic_centre_sim[sim_index] == None:
            paramag_centre = zeros(3, float64)
        else:
            paramag_centre = array(cdp.paramagnetic_centre_sim[sim_index])
    else:
        paramag_centre = array(cdp.paramagnetic_centre)

    # Return the data structures.
    return atomic_pos, paramag_centre


def minimise_setup_tensors(sim_index=None):
    """Set up the data structures for optimisation using alignment tensors as base data sets.

    @keyword sim_index: The index of the simulation to optimise.  This should be None if
                        normal optimisation is desired.
    @type sim_index:    None or int
    @return:            The assembled data structures for using alignment tensors as the base
                        data for optimisation.  These include:
                            - full_tensors, the data of the full alignment tensors.
                            - red_tensor_elem, the tensors as concatenated rank-1 5D arrays.
                            - red_tensor_err, the tensor errors as concatenated rank-1 5D
                            arrays.
                            - full_in_ref_frame, flags specifying if the tensor in the reference
                            frame is the full or reduced tensor.
    @rtype:             tuple of (list, numpy rank-1 array, numpy rank-1 array, numpy rank-1
                        array)
    """

    # Initialise.
    n = len(cdp.align_tensors.reduction)
    full_tensors = zeros(n*5, float64)
    red_tensors  = zeros(n*5, float64)
    red_err = ones(n*5, float64) * 1e-5
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

    # Loop over the reduced tensors.
    for i, tensor in tensor_loop(red=True):
        # The reduced tensor (simulation data).
        if sim_index != None:
            red_tensors[5*i + 0] = tensor.Axx_sim[sim_index]
            red_tensors[5*i + 1] = tensor.Ayy_sim[sim_index]
            red_tensors[5*i + 2] = tensor.Axy_sim[sim_index]
            red_tensors[5*i + 3] = tensor.Axz_sim[sim_index]
            red_tensors[5*i + 4] = tensor.Ayz_sim[sim_index]

        # The reduced tensor.
        else:
            red_tensors[5*i + 0] = tensor.Axx
            red_tensors[5*i + 1] = tensor.Ayy
            red_tensors[5*i + 2] = tensor.Axy
            red_tensors[5*i + 3] = tensor.Axz
            red_tensors[5*i + 4] = tensor.Ayz

        # The reduced tensor errors.
        if hasattr(tensor, 'Axx_err'):
            red_err[5*i + 0] = tensor.Axx_err
            red_err[5*i + 1] = tensor.Ayy_err
            red_err[5*i + 2] = tensor.Axy_err
            red_err[5*i + 3] = tensor.Axz_err
            red_err[5*i + 4] = tensor.Ayz_err

    # Return the data structures.
    return full_tensors, red_tensors, red_err, full_in_ref_frame


def minimise_setup_fixed_tensors():
    """Set up the data structures for the fixed alignment tensors.

    @return:            The assembled data structures for the fixed alignment tensors.
    @rtype:             numpy rank-1 array.
    """

    # Initialise.
    n = align_tensor.num_tensors(skip_fixed=False) - align_tensor.num_tensors(skip_fixed=True)
    tensors = zeros(n*5, float64)

    # Nothing to do.
    if n == 0:
        return None

    # Loop over the tensors.
    index = 0
    for i in range(len(cdp.align_tensors)):
        # Skip non-optimised data.
        if not opt_uses_align_data(cdp.align_tensors[i].name):
            continue

        # No parameters have been set.
        if not hasattr(cdp.align_tensors[i], 'Axx'):
            continue

        # The real tensors.
        tensors[5*index + 0] = cdp.align_tensors[i].Axx
        tensors[5*index + 1] = cdp.align_tensors[i].Ayy
        tensors[5*index + 2] = cdp.align_tensors[i].Axy
        tensors[5*index + 3] = cdp.align_tensors[i].Axz
        tensors[5*index + 4] = cdp.align_tensors[i].Ayz

        # Increment the index.
        index += 1

    # Return the data structure.
    return tensors


def target_fn_setup(sim_index=None, scaling_matrix=None, verbosity=0):
    """Initialise the target function for optimisation or direct calculation.

    @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:            None or int
    @keyword scaling_matrix:    The diagonal and square scaling matrix.
    @type scaling_matrix:       numpy rank-2, float64 array or None
    @keyword verbosity:         A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:            int
    """

    # Test if the N-state model has been set up.
    if not hasattr(cdp, 'model'):
        raise RelaxNoModelError('N-state')

    # '2-domain' model setup tests.
    if cdp.model == '2-domain':
        # The number of states.
        if not hasattr(cdp, 'N'):
            raise RelaxError("The number of states has not been set.")

        # The reference domain.
        if not hasattr(cdp, 'ref_domain'):
            raise RelaxError("The reference domain has not been set.")

    # Update the model parameters if necessary.
    update_model()

    # Create the initial parameter vector.
    param_vector = assemble_param_vector(sim_index=sim_index)

    # Replace all NaNs with 0.0.
    fix_invalid(param_vector, copy=False, fill_value=0.0)

    # Determine if alignment tensors or RDCs are to be used.
    data_types = base_data_types()

    # The probabilities.
    probs = None
    if hasattr(cdp, 'probs') and len(cdp.probs) and cdp.probs[0] != None:
        probs = cdp.probs

    # Diagonal scaling.
    if len(param_vector) and scaling_matrix != None:
        param_vector = dot(inv(scaling_matrix), param_vector)

    # Get the data structures for optimisation using the tensors as base data sets.
    full_tensors, red_tensor_elem, red_tensor_err, full_in_ref_frame = None, None, None, None
    if 'tensor' in data_types:
        full_tensors, red_tensor_elem, red_tensor_err, full_in_ref_frame = minimise_setup_tensors(sim_index=sim_index)

    # Get the data structures for optimisation using PCSs as base data sets.
    pcs, pcs_err, pcs_weight, temp, frq, pcs_pseudo_flags = None, None, None, None, None, None
    if 'pcs' in data_types:
        pcs, pcs_err, pcs_weight, temp, frq, pcs_pseudo_flags = return_pcs_data(sim_index=sim_index, verbosity=verbosity)

    # Get the data structures for optimisation using RDCs as base data sets.
    rdcs, rdc_err, rdc_weight, rdc_vector, rdc_dj, absolute_rdc, T_flags, j_couplings, rdc_pseudo_flags = None, None, None, None, None, None, None, None, None
    if 'rdc' in data_types:
        # The data.
        rdcs, rdc_err, rdc_weight, rdc_vector, rdc_dj, absolute_rdc, T_flags, j_couplings, rdc_pseudo_flags = return_rdc_data(sim_index=sim_index, verbosity=verbosity)

    # Get the fixed tensors.
    fixed_tensors = None
    if 'rdc' in data_types or 'pcs' in data_types:
        full_tensors = minimise_setup_fixed_tensors()

        # The flag list.
        fixed_tensors = []
        for i in range(len(cdp.align_tensors)):
            # Skip non-optimised data.
            if not opt_uses_align_data(cdp.align_tensors[i].name):
                continue

            if cdp.align_tensors[i].fixed:
                fixed_tensors.append(True)
            else:
                fixed_tensors.append(False)

    # Get the atomic_positions.
    atomic_pos, paramag_centre, centre_fixed = None, None, True
    if 'pcs' in data_types or 'pre' in data_types:
        atomic_pos, paramag_centre = minimise_setup_atomic_pos(sim_index=sim_index)

        # Optimisation of the centre.
        if hasattr(cdp, 'paramag_centre_fixed'):
            centre_fixed = cdp.paramag_centre_fixed

    # Set up the class instance containing the target function.
    model = N_state_opt(model=cdp.model, N=cdp.N, init_params=param_vector, probs=probs, full_tensors=full_tensors, red_data=red_tensor_elem, red_errors=red_tensor_err, full_in_ref_frame=full_in_ref_frame, fixed_tensors=fixed_tensors, pcs=pcs, rdcs=rdcs, pcs_errors=pcs_err, rdc_errors=rdc_err, T_flags=T_flags, j_couplings=j_couplings, rdc_pseudo_flags=rdc_pseudo_flags, pcs_pseudo_flags=pcs_pseudo_flags, pcs_weights=pcs_weight, rdc_weights=rdc_weight, rdc_vect=rdc_vector, temp=temp, frq=frq, dip_const=rdc_dj, absolute_rdc=absolute_rdc, atomic_pos=atomic_pos, paramag_centre=paramag_centre, scaling_matrix=scaling_matrix, centre_fixed=centre_fixed)

    # Return the data.
    return model, param_vector, data_types
