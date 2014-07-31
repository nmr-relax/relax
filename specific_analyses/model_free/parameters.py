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
from numpy import array, float64, int8, zeros
from re import match

# relax module imports.
from lib.errors import RelaxError
from pipe_control import diffusion_tensor
from pipe_control.mol_res_spin import spin_loop
from specific_analyses.model_free.model import determine_model_type


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
                if hasattr(cdp.diff_tensor, 'tm'):
                    param_vector.append(cdp.diff_tensor.tm)
                else:
                    param_vector.append(None)

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                if hasattr(cdp.diff_tensor, 'tm'):
                    param_vector.append(cdp.diff_tensor.tm)
                    param_vector.append(cdp.diff_tensor.Da)
                    param_vector.append(cdp.diff_tensor.theta)
                    param_vector.append(cdp.diff_tensor.phi)
                else:
                    param_vector += [None, None, None, None]

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                if hasattr(cdp.diff_tensor, 'tm'):
                    param_vector.append(cdp.diff_tensor.tm)
                    param_vector.append(cdp.diff_tensor.Da)
                    param_vector.append(cdp.diff_tensor.Dr)
                    param_vector.append(cdp.diff_tensor.alpha)
                    param_vector.append(cdp.diff_tensor.beta)
                    param_vector.append(cdp.diff_tensor.gamma)
                else:
                    param_vector += [None, None, None, None, None, None]

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

    # Return a numpy array.
    return array(param_vector, float64)


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


def linear_constraints(num_params, model_type=None, spin=None, spin_id=None, scaling_matrix=None):
    """Set up the model-free linear constraint matrices A and b.

    Standard notation
    =================

    The order parameter constraints are::

        0 <= S2 <= 1
        0 <= S2f <= 1
        0 <= S2s <= 1

    By substituting the formula S2 = S2f.S2s into the above inequalities, the additional two
    inequalities can be derived::

        S2 <= S2f
        S2 <= S2s

    Correlation time constraints are::

        te >= 0
        tf >= 0
        ts >= 0

        tf <= ts

        te, tf, ts <= 2 * tm

    Additional constraints used include::

        Rex >= 0
        0.9e-10 <= r <= 2e-10
        -300e-6 <= CSA <= 0


    Rearranged notation
    ===================

    The above inequality constraints can be rearranged into::

        S2 >= 0
        -S2 >= -1
        S2f >= 0
        -S2f >= -1
        S2s >= 0
        -S2s >= -1
        S2f - S2 >= 0
        S2s - S2 >= 0
        te >= 0
        tf >= 0
        ts >= 0
        ts - tf >= 0
        Rex >= 0
        r >= 0.9e-10
        -r >= -2e-10
        CSA >= -300e-6
        -CSA >= 0


    Matrix notation
    ===============

    In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
    values, and b is a vector of scalars, these inequality constraints are::

        | 1  0  0  0  0  0  0  0  0 |                  |    0    |
        |                           |                  |         |
        |-1  0  0  0  0  0  0  0  0 |                  |   -1    |
        |                           |                  |         |
        | 0  1  0  0  0  0  0  0  0 |                  |    0    |
        |                           |                  |         |
        | 0 -1  0  0  0  0  0  0  0 |                  |   -1    |
        |                           |                  |         |
        | 0  0  1  0  0  0  0  0  0 |     | S2  |      |    0    |
        |                           |     |     |      |         |
        | 0  0 -1  0  0  0  0  0  0 |     | S2f |      |   -1    |
        |                           |     |     |      |         |
        |-1  1  0  0  0  0  0  0  0 |     | S2s |      |    0    |
        |                           |     |     |      |         |
        |-1  0  1  0  0  0  0  0  0 |     | te  |      |    0    |
        |                           |     |     |      |         |
        | 0  0  0  1  0  0  0  0  0 |  .  | tf  |  >=  |    0    |
        |                           |     |     |      |         |
        | 0  0  0  0  1  0  0  0  0 |     | ts  |      |    0    |
        |                           |     |     |      |         |
        | 0  0  0  0  0  1  0  0  0 |     | Rex |      |    0    |
        |                           |     |     |      |         |
        | 0  0  0  0 -1  1  0  0  0 |     |  r  |      |    0    |
        |                           |     |     |      |         |
        | 0  0  0  0  0  0  1  0  0 |     | CSA |      |    0    |
        |                           |                  |         |
        | 0  0  0  0  0  0  0  1  0 |                  | 0.9e-10 |
        |                           |                  |         |
        | 0  0  0  0  0  0  0 -1  0 |                  | -2e-10  |
        |                           |                  |         |
        | 0  0  0  0  0  0  0  0  1 |                  | -300e-6 |
        |                           |                  |         |
        | 0  0  0  0  0  0  0  0 -1 |                  |    0    |


    @param num_params:          The number of parameters in the model.
    @type num_params:           int
    @keyword model_type:        The model type, one of 'all', 'diff', 'mf', or 'local_tm'.
    @type model_type:           str
    @keyword spin:              The spin data container.  If this argument is supplied, then the
                                spin_id argument will be ignored.
    @type spin:                 SpinContainer instance
    @keyword spin_id:           The spin identification string.
    @type spin_id:              str
    @keyword scaling_matrix:    The diagonal, square scaling matrix.
    @type scaling_matrix:       numpy diagonal matrix
    """

    # Upper limit flag for correlation times.
    upper_time_limit = 1

    # Initialisation (0..j..m).
    A = []
    b = []
    zero_array = zeros(num_params, float64)
    i = 0
    j = 0

    # Diffusion tensor parameters.
    if model_type != 'mf' and diffusion_tensor.diff_data_exists():
        # Spherical diffusion.
        if cdp.diff_tensor.type == 'sphere':
            # 0 <= tm <= 200 ns.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            A[j+1][i] = -1.0
            b.append(0.0 / scaling_matrix[i, i])
            b.append(-200.0 * 1e-9 / scaling_matrix[i, i])
            i = i + 1
            j = j + 2

        # Spheroidal diffusion.
        elif cdp.diff_tensor.type == 'spheroid':
            # 0 <= tm <= 200 ns.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            A[j+1][i] = -1.0
            b.append(0.0 / scaling_matrix[i, i])
            b.append(-200.0 * 1e-9 / scaling_matrix[i, i])
            i = i + 1
            j = j + 2

            # Prolate diffusion, Da >= 0.
            if cdp.diff_tensor.spheroid_type == 'prolate':
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Add two to i for the theta and phi parameters.
                i = i + 2

            # Oblate diffusion, Da <= 0.
            elif cdp.diff_tensor.spheroid_type == 'oblate':
                A.append(zero_array * 0.0)
                A[j][i] = -1.0
                b.append(0.0 / scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Add two to i for the theta and phi parameters.
                i = i + 2

            else:
                # Add three to i for the Da, theta and phi parameters.
                i = i + 3

        # Ellipsoidal diffusion.
        elif cdp.diff_tensor.type == 'ellipsoid':
            # 0 <= tm <= 200 ns.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            A[j+1][i] = -1.0
            b.append(0.0 / scaling_matrix[i, i])
            b.append(-200.0 * 1e-9 / scaling_matrix[i, i])
            i = i + 1
            j = j + 2

            # Da >= 0.
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            b.append(0.0 / scaling_matrix[i, i])
            i = i + 1
            j = j + 1

            # 0 <= Dr <= 1.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            A[j+1][i] = -1.0
            b.append(0.0 / scaling_matrix[i, i])
            b.append(-1.0 / scaling_matrix[i, i])
            i = i + 1
            j = j + 2

            # Add three to i for the alpha, beta, and gamma parameters.
            i = i + 3

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

            # Save current value of i.
            old_i = i

            # Loop over the model-free parameters.
            for l in range(len(spin.params)):
                # Local tm.
                if spin.params[l] == 'local_tm':
                    if upper_time_limit:
                        # 0 <= tm <= 200 ns.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.0 / scaling_matrix[i, i])
                        b.append(-200.0 * 1e-9 / scaling_matrix[i, i])
                        j = j + 2
                    else:
                        # 0 <= tm.
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        b.append(0.0 / scaling_matrix[i, i])
                        j = j + 1

                # Order parameters {S2, S2f, S2s}.
                elif match('s2', spin.params[l]):
                    # 0 <= S2 <= 1.
                    A.append(zero_array * 0.0)
                    A.append(zero_array * 0.0)
                    A[j][i] = 1.0
                    A[j+1][i] = -1.0
                    b.append(0.0 / scaling_matrix[i, i])
                    b.append(-1.0 / scaling_matrix[i, i])
                    j = j + 2

                    # S2 <= S2f and S2 <= S2s.
                    if spin.params[l] == 's2':
                        for m in range(len(spin.params)):
                            if spin.params[m] == 's2f' or spin.params[m] == 's2s':
                                A.append(zero_array * 0.0)
                                A[j][i] = -1.0
                                A[j][old_i+m] = 1.0
                                b.append(0.0)
                                j = j + 1

                # Correlation times {te, tf, ts}.
                elif match('t[efs]', spin.params[l]):
                    # te, tf, ts >= 0.
                    A.append(zero_array * 0.0)
                    A[j][i] = 1.0
                    b.append(0.0 / scaling_matrix[i, i])
                    j = j + 1

                    # tf <= ts.
                    if spin.params[l] == 'ts':
                        for m in range(len(spin.params)):
                            if spin.params[m] == 'tf':
                                A.append(zero_array * 0.0)
                                A[j][i] = 1.0
                                A[j][old_i+m] = -1.0
                                b.append(0.0)
                                j = j + 1

                    # te, tf, ts <= 2 * tm.  (tf not needed because tf <= ts).
                    if upper_time_limit:
                        if not spin.params[l] == 'tf':
                            if model_type == 'mf':
                                A.append(zero_array * 0.0)
                                A[j][i] = -1.0
                                b.append(-2.0 * cdp.diff_tensor.tm / scaling_matrix[i, i])
                            else:
                                A.append(zero_array * 0.0)
                                A[j][0] = 2.0
                                A[j][i] = -1.0
                                b.append(0.0)

                            j = j + 1

                # Rex.
                elif spin.params[l] == 'rex':
                    A.append(zero_array * 0.0)
                    A[j][i] = 1.0
                    b.append(0.0 / scaling_matrix[i, i])
                    j = j + 1

                # Bond length.
                elif spin.params[l] == 'r':
                    # 0.9e-10 <= r <= 2e-10.
                    A.append(zero_array * 0.0)
                    A.append(zero_array * 0.0)
                    A[j][i] = 1.0
                    A[j+1][i] = -1.0
                    b.append(0.9e-10 / scaling_matrix[i, i])
                    b.append(-2e-10 / scaling_matrix[i, i])
                    j = j + 2

                # CSA.
                elif spin.params[l] == 'csa':
                    # -300e-6 <= CSA <= 0.
                    A.append(zero_array * 0.0)
                    A.append(zero_array * 0.0)
                    A[j][i] = 1.0
                    A[j+1][i] = -1.0
                    b.append(-300e-6 / scaling_matrix[i, i])
                    b.append(0.0 / scaling_matrix[i, i])
                    j = j + 2

                # Increment i.
                i = i + 1

    # Convert to numpy data structures.
    A = array(A, int8)
    b = array(b, float64)

    return A, b


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
