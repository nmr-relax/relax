###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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
"""The model-free analysis parameter functions."""

# Python module imports.
from math import pi
from numpy import float64, array, identity, zeros
from re import search

# relax module imports.
from lib.errors import RelaxError, RelaxNoSequenceError, RelaxNoTensorError
from pipe_control import diffusion_tensor
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop


def are_mf_params_set(spin):
    """Test if the model-free parameter values are set.

    @param spin:    The spin container object.
    @type spin:     SpinContainer instance
    @return:        The name of the first parameter in the parameter list in which the
                    corresponding parameter value is None.  If all parameters are set, then None
                    is returned.
    @rtype:         str or None
    """

    # Deselected residue.
    if spin.select == 0:
        return

    # Loop over the model-free parameters.
    for j in range(len(spin.params)):
        # Local tm.
        if spin.params[j] == 'local_tm' and spin.local_tm == None:
            return spin.params[j]

        # S2.
        elif spin.params[j] == 's2' and spin.s2 == None:
            return spin.params[j]

        # S2f.
        elif spin.params[j] == 's2f' and spin.s2f == None:
            return spin.params[j]

        # S2s.
        elif spin.params[j] == 's2s' and spin.s2s == None:
            return spin.params[j]

        # te.
        elif spin.params[j] == 'te' and spin.te == None:
            return spin.params[j]

        # tf.
        elif spin.params[j] == 'tf' and spin.tf == None:
            return spin.params[j]

        # ts.
        elif spin.params[j] == 'ts' and spin.ts == None:
            return spin.params[j]

        # Rex.
        elif spin.params[j] == 'rex' and spin.rex == None:
            return spin.params[j]

        # r.
        elif spin.params[j] == 'r' and spin.r == None:
            return spin.params[j]

        # CSA.
        elif spin.params[j] == 'csa' and spin.csa == None:
            return spin.params[j]


def assemble_param_names(model_type, spin_id=None):
    """Function for assembling a list of all the model parameter names.

    @param model_type:  The model-free model type.  This must be one of 'mf', 'local_tm',
                        'diff', or 'all'.
    @type model_type:   str
    @param spin_id:     The spin identification string.
    @type spin_id:      str
    @return:            A list containing all the parameters of the model-free model.
    @rtype:             list of str
    """

    # Initialise.
    param_names = []

    # Diffusion tensor parameters.
    if model_type == 'diff' or model_type == 'all':
        # Spherical diffusion.
        if cdp.diff_tensor.type == 'sphere':
            param_names.append('tm')

        # Spheroidal diffusion.
        elif cdp.diff_tensor.type == 'spheroid':
            param_names.append('tm')
            param_names.append('Da')
            param_names.append('theta')
            param_names.append('phi')

        # Ellipsoidal diffusion.
        elif cdp.diff_tensor.type == 'ellipsoid':
            param_names.append('tm')
            param_names.append('Da')
            param_names.append('Dr')
            param_names.append('alpha')
            param_names.append('beta')
            param_names.append('gamma')

    # Model-free parameters (spin specific parameters).
    if model_type != 'diff':
        # Loop over the spins.
        for spin in spin_loop(spin_id):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Add the spin specific model-free parameters.
            param_names = param_names + spin.params

    # Return the parameter names.
    return param_names


def assemble_param_vector(spin=None, spin_id=None, sim_index=None, model_type=None):
    """Assemble the model-free parameter vector (as numpy array).

    If the spin argument is supplied, then the spin_id argument will be ignored.

    @keyword spin:          The spin data container.
    @type spin:             SpinContainer instance
    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @keyword sim_index:     The optional MC simulation index.
    @type sim_index:        int
    @keyword model_type:    The optional model type, one of 'all', 'diff', 'mf', or 'local_tm'.
    @type model_type:       str or None
    @return:                An array of the parameter values of the model-free model.
    @rtype:                 numpy array
    """

    # Initialise.
    param_vector = []

    # Determine the model type.
    if not model_type:
        model_type = determine_model_type()

    # Diffusion tensor parameters.
    if model_type == 'diff' or model_type == 'all':
        # Normal parameters.
        if sim_index == None:
            # Spherical diffusion.
            if cdp.diff_tensor.type == 'sphere':
                param_vector.append(cdp.diff_tensor.tm)

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                param_vector.append(cdp.diff_tensor.tm)
                param_vector.append(cdp.diff_tensor.Da)
                param_vector.append(cdp.diff_tensor.theta)
                param_vector.append(cdp.diff_tensor.phi)

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                param_vector.append(cdp.diff_tensor.tm)
                param_vector.append(cdp.diff_tensor.Da)
                param_vector.append(cdp.diff_tensor.Dr)
                param_vector.append(cdp.diff_tensor.alpha)
                param_vector.append(cdp.diff_tensor.beta)
                param_vector.append(cdp.diff_tensor.gamma)

        # Monte Carlo diffusion tensor parameters.
        else:
            # Spherical diffusion.
            if cdp.diff_tensor.type == 'sphere':
                param_vector.append(cdp.diff_tensor.tm_sim[sim_index])

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                param_vector.append(cdp.diff_tensor.tm_sim[sim_index])
                param_vector.append(cdp.diff_tensor.Da_sim[sim_index])
                param_vector.append(cdp.diff_tensor.theta_sim[sim_index])
                param_vector.append(cdp.diff_tensor.phi_sim[sim_index])

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                param_vector.append(cdp.diff_tensor.tm_sim[sim_index])
                param_vector.append(cdp.diff_tensor.Da_sim[sim_index])
                param_vector.append(cdp.diff_tensor.Dr_sim[sim_index])
                param_vector.append(cdp.diff_tensor.alpha_sim[sim_index])
                param_vector.append(cdp.diff_tensor.beta_sim[sim_index])
                param_vector.append(cdp.diff_tensor.gamma_sim[sim_index])

    # Model-free parameters (spin specific parameters).
    if model_type != 'diff':
        # The loop.
        if spin:
            loop = [spin]
        else:
            loop = spin_loop(spin_id)

        # Loop over the spins.
        for spin in loop:
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins with no parameters.
            if not hasattr(spin, 'params'):
                continue

            # Loop over the model-free parameters.
            for i in range(len(spin.params)):
                # local tm.
                if spin.params[i] == 'local_tm':
                    if sim_index == None:
                        param_vector.append(spin.local_tm)
                    else:
                        param_vector.append(spin.local_tm_sim[sim_index])

                # S2.
                elif spin.params[i] == 's2':
                    if sim_index == None:
                        param_vector.append(spin.s2)
                    else:
                        param_vector.append(spin.s2_sim[sim_index])

                # S2f.
                elif spin.params[i] == 's2f':
                    if sim_index == None:
                        param_vector.append(spin.s2f)
                    else:
                        param_vector.append(spin.s2f_sim[sim_index])

                # S2s.
                elif spin.params[i] == 's2s':
                    if sim_index == None:
                        param_vector.append(spin.s2s)
                    else:
                        param_vector.append(spin.s2s_sim[sim_index])

                # te.
                elif spin.params[i] == 'te':
                    if sim_index == None:
                        param_vector.append(spin.te)
                    else:
                        param_vector.append(spin.te_sim[sim_index])

                # tf.
                elif spin.params[i] == 'tf':
                    if sim_index == None:
                        param_vector.append(spin.tf)
                    else:
                        param_vector.append(spin.tf_sim[sim_index])

                # ts.
                elif spin.params[i] == 'ts':
                    if sim_index == None:
                        param_vector.append(spin.ts)
                    else:
                        param_vector.append(spin.ts_sim[sim_index])

                # Rex.
                elif spin.params[i] == 'rex':
                    if sim_index == None:
                        param_vector.append(spin.rex)
                    else:
                        param_vector.append(spin.rex_sim[sim_index])

                # r.
                elif spin.params[i] == 'r':
                    if sim_index == None:
                        param_vector.append(spin.r)
                    else:
                        param_vector.append(spin.r_sim[sim_index])

                # CSA.
                elif spin.params[i] == 'csa':
                    if sim_index == None:
                        param_vector.append(spin.csa)
                    else:
                        param_vector.append(spin.csa_sim[sim_index])

                # Unknown parameter.
                else:
                    raise RelaxError("Unknown parameter.")

    # Replace all instances of None with 0.0 to allow the list to be converted to a numpy array.
    for i in range(len(param_vector)):
        if param_vector[i] == None:
            param_vector[i] = 0.0

    # Return a numpy array.
    return array(param_vector, float64)


def assemble_scaling_matrix(num_params, model_type=None, spin=None, spin_id=None, scaling=True):
    """Create and return the scaling matrix.

    If the spin argument is supplied, then the spin_id argument will be ignored.

    @param num_params:      The number of parameters in the model.
    @type num_params:       int
    @keyword model_type:    The model type, one of 'all', 'diff', 'mf', or 'local_tm'.
    @type model_type:       str
    @keyword spin:          The spin data container.
    @type spin:             SpinContainer instance
    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @return:                The diagonal and square scaling matrix.
    @rtype:                 numpy diagonal matrix
    """

    # Initialise.
    if num_params == 0:
        scaling_matrix = zeros((0, 0), float64)
    else:
        scaling_matrix = identity(num_params, float64)
    i = 0

    # No diagonal scaling, so return the identity matrix.
    if not scaling:
        return scaling_matrix

    # tm, te, tf, and ts (must all be the same for diagonal scaling!).
    ti_scaling = 1e-12

    # Diffusion tensor parameters.
    if model_type == 'diff' or model_type == 'all':
        # Spherical diffusion.
        if cdp.diff_tensor.type == 'sphere':
            # tm.
            scaling_matrix[i, i] = ti_scaling

            # Increment i.
            i = i + 1

        # Spheroidal diffusion.
        elif cdp.diff_tensor.type == 'spheroid':
            # tm, Da, theta, phi
            scaling_matrix[i, i] = ti_scaling
            scaling_matrix[i+1, i+1] = 1e7
            scaling_matrix[i+2, i+2] = 1.0
            scaling_matrix[i+3, i+3] = 1.0

            # Increment i.
            i = i + 4

        # Ellipsoidal diffusion.
        elif cdp.diff_tensor.type == 'ellipsoid':
            # tm, Da, Dr, alpha, beta, gamma.
            scaling_matrix[i, i] = ti_scaling
            scaling_matrix[i+1, i+1] = 1e7
            scaling_matrix[i+2, i+2] = 1.0
            scaling_matrix[i+3, i+3] = 1.0
            scaling_matrix[i+4, i+4] = 1.0
            scaling_matrix[i+5, i+5] = 1.0

            # Increment i.
            i = i + 6

    # Model-free parameters.
    if model_type != 'diff':
        # The loop.
        if spin:
            loop = [spin]
        else:
            loop = spin_loop(spin_id)

        # Loop over the spins.
        for spin in loop:
            # Skip deselected spins.
            if not spin.select:
                continue

            # Loop over the model-free parameters.
            for k in range(len(spin.params)):
                # Local tm, te, tf, and ts (must all be the same for diagonal scaling!).
                if spin.params[k] == 'local_tm' or search('^t', spin.params[k]):
                    scaling_matrix[i, i] = ti_scaling

                # Rex.
                elif spin.params[k] == 'rex':
                    scaling_matrix[i, i] = 1.0 / (2.0 * pi * cdp.spectrometer_frq[cdp.ri_ids[0]]) ** 2

                # Interatomic distances.
                elif spin.params[k] == 'r':
                    scaling_matrix[i, i] = 1e-10

                # CSA.
                elif spin.params[k] == 'csa':
                    scaling_matrix[i, i] = 1e-4

                # Increment i.
                i = i + 1

    # Return the scaling matrix.
    return scaling_matrix


def conv_factor_rex():
    """Calculate and return the Rex conversion factor.

    @return:    The Rex conversion factor.
    @rtype:     float
    """

    # No frequency info.
    if not hasattr(cdp, 'spectrometer_frq'):
        raise RelaxError("No spectrometer frequency information is present in the current data pipe.")

    # The 1st spectrometer frequency.
    if hasattr(cdp, 'ri_ids'):
        frq = cdp.spectrometer_frq[cdp.ri_ids[0]]

    # Take the highest frequency, if all else fails.
    else:
        frqs = sorted(cdp.spectrometer_frq.values())
        frq = frqs[-1]

    # The factor.
    return 1.0 / (2.0 * pi * frq)**2


def determine_model_type():
    """Determine the global model type.

    @return:    The name of the model type, which will be one of 'all', 'diff', 'mf', or 'local_tm'.  If all parameters are fixed (and no spins selected), None is returned.
    @rtype:     str or None
    """

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # If there is a local tm, fail if not all residues have a local tm parameter.
    local_tm = False
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # No params.
        if not hasattr(spin, 'params') or not spin.params:
            continue

        # Local tm.
        if not local_tm and 'local_tm' in spin.params:
            local_tm = True

        # Inconsistencies.
        elif local_tm and not 'local_tm' in spin.params:
            raise RelaxError("All spins must either have a local tm parameter or not.")

    # Check if any model-free parameters are allowed to vary.
    mf_all_fixed = True
    mf_all_deselected = True
    for spin in spin_loop():
        # Skip deselected spins.
        if not spin.select:
            continue

        # At least one spin is selected.
        mf_all_deselected = False

        # Test the fixed flag.
        if not hasattr(spin, 'fixed'):
            mf_all_fixed = False
            break
        if not spin.fixed:
            mf_all_fixed = False
            break

    # No spins selected?!?
    if mf_all_deselected:
        # All parameters fixed!
        if not hasattr(cdp, 'diff_tensor') or cdp.diff_tensor.fixed:
            return None

        return 'diff'

    # Local tm.
    if local_tm:
        return 'local_tm'

    # Test if the diffusion tensor data is loaded.
    if not diffusion_tensor.diff_data_exists():
        # Catch when the local tm value is set but not in the parameter list.
        for spin in spin_loop():
            if hasattr(spin, 'local_tm') and spin.local_tm != None and not 'local_tm' in spin.params:
                raise RelaxError("The local tm value is set but not located in the model parameter list.")

        # Normal error.
        raise RelaxNoTensorError('diffusion')

    # 'diff' model type.
    if mf_all_fixed:
        # All parameters fixed!
        if cdp.diff_tensor.fixed:
            return None

        return 'diff'

    # 'mf' model type.
    if cdp.diff_tensor.fixed:
        return 'mf'

    # 'all' model type.
    else:
        return 'all'


def model_map(model):
    """Return the equation name and parameter list corresponding to the given model.

    @param model:   The model-free model.
    @type model:    str
    @return:        The equation type (either 'mf_orig' or 'mf_ext') and the model-free parameter list corresponding to the model.
    @rtype:         str, list
    """

    # Block 1.
    if model == 'm0':
        equation = 'mf_orig'
        params = []
    elif model == 'm1':
        equation = 'mf_orig'
        params = ['s2']
    elif model == 'm2':
        equation = 'mf_orig'
        params = ['s2', 'te']
    elif model == 'm3':
        equation = 'mf_orig'
        params = ['s2', 'rex']
    elif model == 'm4':
        equation = 'mf_orig'
        params = ['s2', 'te', 'rex']
    elif model == 'm5':
        equation = 'mf_ext'
        params = ['s2f', 's2', 'ts']
    elif model == 'm6':
        equation = 'mf_ext'
        params = ['s2f', 'tf', 's2', 'ts']
    elif model == 'm7':
        equation = 'mf_ext'
        params = ['s2f', 's2', 'ts', 'rex']
    elif model == 'm8':
        equation = 'mf_ext'
        params = ['s2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'm9':
        equation = 'mf_orig'
        params = ['rex']

    # Block 2.
    elif model == 'm10':
        equation = 'mf_orig'
        params = ['csa']
    elif model == 'm11':
        equation = 'mf_orig'
        params = ['csa', 's2']
    elif model == 'm12':
        equation = 'mf_orig'
        params = ['csa', 's2', 'te']
    elif model == 'm13':
        equation = 'mf_orig'
        params = ['csa', 's2', 'rex']
    elif model == 'm14':
        equation = 'mf_orig'
        params = ['csa', 's2', 'te', 'rex']
    elif model == 'm15':
        equation = 'mf_ext'
        params = ['csa', 's2f', 's2', 'ts']
    elif model == 'm16':
        equation = 'mf_ext'
        params = ['csa', 's2f', 'tf', 's2', 'ts']
    elif model == 'm17':
        equation = 'mf_ext'
        params = ['csa', 's2f', 's2', 'ts', 'rex']
    elif model == 'm18':
        equation = 'mf_ext'
        params = ['csa', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'm19':
        equation = 'mf_orig'
        params = ['csa', 'rex']

    # Block 3.
    elif model == 'm20':
        equation = 'mf_orig'
        params = ['r']
    elif model == 'm21':
        equation = 'mf_orig'
        params = ['r', 's2']
    elif model == 'm22':
        equation = 'mf_orig'
        params = ['r', 's2', 'te']
    elif model == 'm23':
        equation = 'mf_orig'
        params = ['r', 's2', 'rex']
    elif model == 'm24':
        equation = 'mf_orig'
        params = ['r', 's2', 'te', 'rex']
    elif model == 'm25':
        equation = 'mf_ext'
        params = ['r', 's2f', 's2', 'ts']
    elif model == 'm26':
        equation = 'mf_ext'
        params = ['r', 's2f', 'tf', 's2', 'ts']
    elif model == 'm27':
        equation = 'mf_ext'
        params = ['r', 's2f', 's2', 'ts', 'rex']
    elif model == 'm28':
        equation = 'mf_ext'
        params = ['r', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'm29':
        equation = 'mf_orig'
        params = ['r', 'rex']

    # Block 4.
    elif model == 'm30':
        equation = 'mf_orig'
        params = ['r', 'csa']
    elif model == 'm31':
        equation = 'mf_orig'
        params = ['r', 'csa', 's2']
    elif model == 'm32':
        equation = 'mf_orig'
        params = ['r', 'csa', 's2', 'te']
    elif model == 'm33':
        equation = 'mf_orig'
        params = ['r', 'csa', 's2', 'rex']
    elif model == 'm34':
        equation = 'mf_orig'
        params = ['r', 'csa', 's2', 'te', 'rex']
    elif model == 'm35':
        equation = 'mf_ext'
        params = ['r', 'csa', 's2f', 's2', 'ts']
    elif model == 'm36':
        equation = 'mf_ext'
        params = ['r', 'csa', 's2f', 'tf', 's2', 'ts']
    elif model == 'm37':
        equation = 'mf_ext'
        params = ['r', 'csa', 's2f', 's2', 'ts', 'rex']
    elif model == 'm38':
        equation = 'mf_ext'
        params = ['r', 'csa', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'm39':
        equation = 'mf_orig'
        params = ['r', 'csa', 'rex']


    # Preset models with local correlation time.
    ############################################

    # Block 1.
    elif model == 'tm0':
        equation = 'mf_orig'
        params = ['local_tm']
    elif model == 'tm1':
        equation = 'mf_orig'
        params = ['local_tm', 's2']
    elif model == 'tm2':
        equation = 'mf_orig'
        params = ['local_tm', 's2', 'te']
    elif model == 'tm3':
        equation = 'mf_orig'
        params = ['local_tm', 's2', 'rex']
    elif model == 'tm4':
        equation = 'mf_orig'
        params = ['local_tm', 's2', 'te', 'rex']
    elif model == 'tm5':
        equation = 'mf_ext'
        params = ['local_tm', 's2f', 's2', 'ts']
    elif model == 'tm6':
        equation = 'mf_ext'
        params = ['local_tm', 's2f', 'tf', 's2', 'ts']
    elif model == 'tm7':
        equation = 'mf_ext'
        params = ['local_tm', 's2f', 's2', 'ts', 'rex']
    elif model == 'tm8':
        equation = 'mf_ext'
        params = ['local_tm', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'tm9':
        equation = 'mf_orig'
        params = ['local_tm', 'rex']

    # Block 2.
    elif model == 'tm10':
        equation = 'mf_orig'
        params = ['local_tm', 'csa']
    elif model == 'tm11':
        equation = 'mf_orig'
        params = ['local_tm', 'csa', 's2']
    elif model == 'tm12':
        equation = 'mf_orig'
        params = ['local_tm', 'csa', 's2', 'te']
    elif model == 'tm13':
        equation = 'mf_orig'
        params = ['local_tm', 'csa', 's2', 'rex']
    elif model == 'tm14':
        equation = 'mf_orig'
        params = ['local_tm', 'csa', 's2', 'te', 'rex']
    elif model == 'tm15':
        equation = 'mf_ext'
        params = ['local_tm', 'csa', 's2f', 's2', 'ts']
    elif model == 'tm16':
        equation = 'mf_ext'
        params = ['local_tm', 'csa', 's2f', 'tf', 's2', 'ts']
    elif model == 'tm17':
        equation = 'mf_ext'
        params = ['local_tm', 'csa', 's2f', 's2', 'ts', 'rex']
    elif model == 'tm18':
        equation = 'mf_ext'
        params = ['local_tm', 'csa', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'tm19':
        equation = 'mf_orig'
        params = ['local_tm', 'csa', 'rex']

    # Block 3.
    elif model == 'tm20':
        equation = 'mf_orig'
        params = ['local_tm', 'r']
    elif model == 'tm21':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 's2']
    elif model == 'tm22':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 's2', 'te']
    elif model == 'tm23':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 's2', 'rex']
    elif model == 'tm24':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 's2', 'te', 'rex']
    elif model == 'tm25':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 's2f', 's2', 'ts']
    elif model == 'tm26':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 's2f', 'tf', 's2', 'ts']
    elif model == 'tm27':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 's2f', 's2', 'ts', 'rex']
    elif model == 'tm28':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'tm29':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'rex']

    # Block 4.
    elif model == 'tm30':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa']
    elif model == 'tm31':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa', 's2']
    elif model == 'tm32':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa', 's2', 'te']
    elif model == 'tm33':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa', 's2', 'rex']
    elif model == 'tm34':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa', 's2', 'te', 'rex']
    elif model == 'tm35':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 'csa', 's2f', 's2', 'ts']
    elif model == 'tm36':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 'csa', 's2f', 'tf', 's2', 'ts']
    elif model == 'tm37':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 'csa', 's2f', 's2', 'ts', 'rex']
    elif model == 'tm38':
        equation = 'mf_ext'
        params = ['local_tm', 'r', 'csa', 's2f', 'tf', 's2', 'ts', 'rex']
    elif model == 'tm39':
        equation = 'mf_orig'
        params = ['local_tm', 'r', 'csa', 'rex']

    # Invalid model.
    else:
        raise RelaxError("The model '%s' is invalid." % model)

    # Return the values.
    return equation, params


def units_rex():
    """Return the units for the Rex parameter.

    @return:    The field strength dependent Rex units.
    @rtype:     str
    """

    # No frequency info.
    if not hasattr(cdp, 'frq_labels') or len(cdp.frq_labels) == 0:
        return ''

    # The units.
    return cdp.frq_labels[0] + ' MHz'


def disassemble_param_vector(model_type, param_vector=None, spin=None, spin_id=None, sim_index=None):
    """Disassemble the model-free parameter vector.

    @param model_type:      The model-free model type.  This must be one of 'mf', 'local_tm',
                            'diff', or 'all'.
    @type model_type:       str
    @keyword param_vector:  The model-free parameter vector.
    @type param_vector:     numpy array
    @keyword spin:          The spin data container.  If this argument is supplied, then the spin_id
                            argument will be ignored.
    @type spin:             SpinContainer instance
    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @keyword sim_index:     The optional MC simulation index.
    @type sim_index:        int
    """

    # Initialise.
    param_index = 0

    # Diffusion tensor parameters of the Monte Carlo simulations.
    if sim_index != None and (model_type == 'diff' or model_type == 'all'):
        # Spherical diffusion.
        if cdp.diff_tensor.type == 'sphere':
            # Sim values.
            cdp.diff_tensor.set(param='tm', value=param_vector[0], category='sim', sim_index=sim_index)

            # Parameter index.
            param_index = param_index + 1

        # Spheroidal diffusion.
        elif cdp.diff_tensor.type == 'spheroid':
            # Sim values.
            cdp.diff_tensor.set(param='tm', value=param_vector[0], category='sim', sim_index=sim_index)
            cdp.diff_tensor.set(param='Da', value=param_vector[1], category='sim', sim_index=sim_index)
            cdp.diff_tensor.set(param='theta', value=param_vector[2], category='sim', sim_index=sim_index)
            cdp.diff_tensor.set(param='phi', value=param_vector[3], category='sim', sim_index=sim_index)
            diffusion_tensor.fold_angles(sim_index=sim_index)

            # Parameter index.
            param_index = param_index + 4

        # Ellipsoidal diffusion.
        elif cdp.diff_tensor.type == 'ellipsoid':
            # Sim values.
            cdp.diff_tensor.set(param='tm', value=param_vector[0], category='sim', sim_index=sim_index)
            cdp.diff_tensor.set(param='Da', value=param_vector[1], category='sim', sim_index=sim_index)
            cdp.diff_tensor.set(param='Dr', value=param_vector[2], category='sim', sim_index=sim_index)
            cdp.diff_tensor.set(param='alpha', value=param_vector[3], category='sim', sim_index=sim_index)
            cdp.diff_tensor.set(param='beta', value=param_vector[4], category='sim', sim_index=sim_index)
            cdp.diff_tensor.set(param='gamma', value=param_vector[5], category='sim', sim_index=sim_index)
            diffusion_tensor.fold_angles(sim_index=sim_index)

            # Parameter index.
            param_index = param_index + 6

    # Diffusion tensor parameters.
    elif model_type == 'diff' or model_type == 'all':
        # Spherical diffusion.
        if cdp.diff_tensor.type == 'sphere':
            # Values.
            cdp.diff_tensor.set(param='tm', value=param_vector[0])

            # Parameter index.
            param_index = param_index + 1

        # Spheroidal diffusion.
        elif cdp.diff_tensor.type == 'spheroid':
            # Values.
            cdp.diff_tensor.set(param='tm', value=param_vector[0])
            cdp.diff_tensor.set(param='Da', value=param_vector[1])
            cdp.diff_tensor.set(param='theta', value=param_vector[2])
            cdp.diff_tensor.set(param='phi', value=param_vector[3])
            diffusion_tensor.fold_angles()

            # Parameter index.
            param_index = param_index + 4

        # Ellipsoidal diffusion.
        elif cdp.diff_tensor.type == 'ellipsoid':
            # Values.
            cdp.diff_tensor.set(param='tm', value=param_vector[0])
            cdp.diff_tensor.set(param='Da', value=param_vector[1])
            cdp.diff_tensor.set(param='Dr', value=param_vector[2])
            cdp.diff_tensor.set(param='alpha', value=param_vector[3])
            cdp.diff_tensor.set(param='beta', value=param_vector[4])
            cdp.diff_tensor.set(param='gamma', value=param_vector[5])
            diffusion_tensor.fold_angles()

            # Parameter index.
            param_index = param_index + 6

    # Model-free parameters.
    if model_type != 'diff':
        # The loop.
        if spin:
            loop = [spin]
        else:
            loop = spin_loop(spin_id)

        # Loop over the spins.
        for spin in loop:
            # Skip deselected spins.
            if not spin.select:
                continue

            # Loop over the model-free parameters.
            for j in range(len(spin.params)):
                # Local tm.
                if spin.params[j] == 'local_tm':
                    if sim_index == None:
                        spin.local_tm = param_vector[param_index]
                    else:
                        spin.local_tm_sim[sim_index] = param_vector[param_index]

                # S2.
                elif spin.params[j] == 's2':
                    if sim_index == None:
                        spin.s2 = param_vector[param_index]
                    else:
                        spin.s2_sim[sim_index] = param_vector[param_index]

                # S2f.
                elif spin.params[j] == 's2f':
                    if sim_index == None:
                        spin.s2f = param_vector[param_index]
                    else:
                        spin.s2f_sim[sim_index] = param_vector[param_index]

                # S2s.
                elif spin.params[j] == 's2s':
                    if sim_index == None:
                        spin.s2s = param_vector[param_index]
                    else:
                        spin.s2s_sim[sim_index] = param_vector[param_index]

                # te.
                elif spin.params[j] == 'te':
                    if sim_index == None:
                        spin.te = param_vector[param_index]
                    else:
                        spin.te_sim[sim_index] = param_vector[param_index]

                # tf.
                elif spin.params[j] == 'tf':
                    if sim_index == None:
                        spin.tf = param_vector[param_index]
                    else:
                        spin.tf_sim[sim_index] = param_vector[param_index]

                # ts.
                elif spin.params[j] == 'ts':
                    if sim_index == None:
                        spin.ts = param_vector[param_index]
                    else:
                        spin.ts_sim[sim_index] = param_vector[param_index]

                # Rex.
                elif spin.params[j] == 'rex':
                    if sim_index == None:
                        spin.rex = param_vector[param_index]
                    else:
                        spin.rex_sim[sim_index] = param_vector[param_index]

                # r.
                elif spin.params[j] == 'r':
                    if sim_index == None:
                        spin.r = param_vector[param_index]
                    else:
                        spin.r_sim[sim_index] = param_vector[param_index]

                # CSA.
                elif spin.params[j] == 'csa':
                    if sim_index == None:
                        spin.csa = param_vector[param_index]
                    else:
                        spin.csa_sim[sim_index] = param_vector[param_index]

                # Unknown parameter.
                else:
                    raise RelaxError("Unknown parameter.")

                # Increment the parameter index.
                param_index = param_index + 1

    # Calculate all order parameters after unpacking the vector.
    if model_type != 'diff':
        # The loop.
        if spin:
            loop = [spin]
        else:
            loop = spin_loop(spin_id)

        # Loop over the spins.
        for spin in loop:
            # Skip deselected residues.
            if not spin.select:
                continue

            # Normal values.
            if sim_index == None:
                # S2.
                if 's2' not in spin.params and 's2f' in spin.params and 's2s' in spin.params:
                    spin.s2 = spin.s2f * spin.s2s

                # S2f.
                if 's2f' not in spin.params and 's2' in spin.params and 's2s' in spin.params:
                    if spin.s2s == 0.0:
                        spin.s2f = 1e99
                    else:
                        spin.s2f = spin.s2 / spin.s2s

                # S2s.
                if 's2s' not in spin.params and 's2' in spin.params and 's2f' in spin.params:
                    if spin.s2f == 0.0:
                        spin.s2s = 1e99
                    else:
                        spin.s2s = spin.s2 / spin.s2f

            # Simulation values.
            else:
                # S2.
                if 's2' not in spin.params and 's2f' in spin.params and 's2s' in spin.params:
                    spin.s2_sim[sim_index] = spin.s2f_sim[sim_index] * spin.s2s_sim[sim_index]

                # S2f.
                if 's2f' not in spin.params and 's2' in spin.params and 's2s' in spin.params:
                    if spin.s2s_sim[sim_index] == 0.0:
                        spin.s2f_sim[sim_index] = 1e99
                    else:
                        spin.s2f_sim[sim_index] = spin.s2_sim[sim_index] / spin.s2s_sim[sim_index]

                # S2s.
                if 's2s' not in spin.params and 's2' in spin.params and 's2f' in spin.params:
                    if spin.s2f_sim[sim_index] == 0.0:
                        spin.s2s_sim[sim_index] = 1e99
                    else:
                        spin.s2s_sim[sim_index] = spin.s2_sim[sim_index] / spin.s2f_sim[sim_index]
