###############################################################################
#                                                                             #
# Copyright (C) 2003-2011 Edward d'Auvergne                                   #
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

# Python module imports.
from math import pi
from minfx.generic import generic_minimise
from minfx.grid import grid
from numpy import float64, array, dot, zeros
from numpy.linalg import inv
from re import match, search
import sys
from warnings import warn

# relax module imports.
from float import isNaN, isInf
from generic_fns import diffusion_tensor, pipes
from generic_fns.diffusion_tensor import diff_data_exists
from generic_fns.mol_res_spin import count_spins, exists_mol_res_spin_data, return_spin_from_index, spin_loop
from maths_fns.mf import Mf
from physical_constants import h_bar, mu0, return_gyromagnetic_ratio
from relax_errors import RelaxError, RelaxInfError, RelaxLenError, RelaxNaNError, RelaxNoModelError, RelaxNoPdbError, RelaxNoResError, RelaxNoSequenceError, RelaxNoTensorError, RelaxNoValueError, RelaxNoVectorsError, RelaxNucleusError, RelaxProtonTypeError, RelaxSpinTypeError
from relax_warnings import RelaxWarning



class Mf_minimise:
    """Class containing functions specific to model-free optimisation."""

    def _disassemble_param_vector(self, model_type, param_vector=None, spin=None, spin_id=None, sim_index=None):
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
                cdp.diff_tensor.tm_sim[sim_index] = param_vector[0]

                # Parameter index.
                param_index = param_index + 1

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                # Sim values.
                cdp.diff_tensor.tm_sim[sim_index] = param_vector[0]
                cdp.diff_tensor.Da_sim[sim_index] = param_vector[1]
                cdp.diff_tensor.theta_sim[sim_index] = param_vector[2]
                cdp.diff_tensor.phi_sim[sim_index] = param_vector[3]
                diffusion_tensor.fold_angles(sim_index=sim_index)

                # Parameter index.
                param_index = param_index + 4

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                # Sim values.
                cdp.diff_tensor.tm_sim[sim_index] = param_vector[0]
                cdp.diff_tensor.Da_sim[sim_index] = param_vector[1]
                cdp.diff_tensor.Dr_sim[sim_index] = param_vector[2]
                cdp.diff_tensor.alpha_sim[sim_index] = param_vector[3]
                cdp.diff_tensor.beta_sim[sim_index] = param_vector[4]
                cdp.diff_tensor.gamma_sim[sim_index] = param_vector[5]
                diffusion_tensor.fold_angles(sim_index=sim_index)

                # Parameter index.
                param_index = param_index + 6

        # Diffusion tensor parameters.
        elif model_type == 'diff' or model_type == 'all':
            # Spherical diffusion.
            if cdp.diff_tensor.type == 'sphere':
                # Values.
                cdp.diff_tensor.tm = param_vector[0]

                # Parameter index.
                param_index = param_index + 1

            # Spheroidal diffusion.
            elif cdp.diff_tensor.type == 'spheroid':
                # Values.
                cdp.diff_tensor.tm = param_vector[0]
                cdp.diff_tensor.Da = param_vector[1]
                cdp.diff_tensor.theta = param_vector[2]
                cdp.diff_tensor.phi = param_vector[3]
                diffusion_tensor.fold_angles()

                # Parameter index.
                param_index = param_index + 4

            # Ellipsoidal diffusion.
            elif cdp.diff_tensor.type == 'ellipsoid':
                # Values.
                cdp.diff_tensor.tm = param_vector[0]
                cdp.diff_tensor.Da = param_vector[1]
                cdp.diff_tensor.Dr = param_vector[2]
                cdp.diff_tensor.alpha = param_vector[3]
                cdp.diff_tensor.beta = param_vector[4]
                cdp.diff_tensor.gamma = param_vector[5]
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
                for j in xrange(len(spin.params)):
                    # Local tm.
                    if spin.params[j] == 'local_tm':
                        if sim_index == None:
                            spin.local_tm = param_vector[param_index]
                        else:
                            spin.local_tm_sim[sim_index] = param_vector[param_index]

                    # S2.
                    elif spin.params[j] == 'S2':
                        if sim_index == None:
                            spin.s2 = param_vector[param_index]
                        else:
                            spin.s2_sim[sim_index] = param_vector[param_index]

                    # S2f.
                    elif spin.params[j] == 'S2f':
                        if sim_index == None:
                            spin.s2f = param_vector[param_index]
                        else:
                            spin.s2f_sim[sim_index] = param_vector[param_index]

                    # S2s.
                    elif spin.params[j] == 'S2s':
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
                    elif spin.params[j] == 'Rex':
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
                    elif spin.params[j] == 'CSA':
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
                    if 'S2' not in spin.params and 'S2f' in spin.params and 'S2s' in spin.params:
                        spin.s2 = spin.s2f * spin.s2s

                    # S2f.
                    if 'S2f' not in spin.params and 'S2' in spin.params and 'S2s' in spin.params:
                        if spin.s2s == 0.0:
                            spin.s2f = 1e99
                        else:
                            spin.s2f = spin.s2 / spin.s2s

                    # S2s.
                    if 'S2s' not in spin.params and 'S2' in spin.params and 'S2f' in spin.params:
                        if spin.s2f == 0.0:
                            spin.s2s = 1e99
                        else:
                            spin.s2s = spin.s2 / spin.s2f

                # Simulation values.
                else:
                    # S2.
                    if 'S2' not in spin.params and 'S2f' in spin.params and 'S2s' in spin.params:
                        spin.s2_sim[sim_index] = spin.s2f_sim[sim_index] * spin.s2s_sim[sim_index]

                    # S2f.
                    if 'S2f' not in spin.params and 'S2' in spin.params and 'S2s' in spin.params:
                        if spin.s2s_sim[sim_index] == 0.0:
                            spin.s2f_sim[sim_index] = 1e99
                        else:
                            spin.s2f_sim[sim_index] = spin.s2_sim[sim_index] / spin.s2s_sim[sim_index]

                    # S2s.
                    if 'S2s' not in spin.params and 'S2' in spin.params and 'S2f' in spin.params:
                        if spin.s2f_sim[sim_index] == 0.0:
                            spin.s2s_sim[sim_index] = 1e99
                        else:
                            spin.s2s_sim[sim_index] = spin.s2_sim[sim_index] / spin.s2f_sim[sim_index]


    def _grid_search_config(self, num_params, spin=None, spin_id=None, lower=None, upper=None, inc=None, scaling_matrix=None, verbosity=1):
        """Configure the grid search.

        @param num_params:          The number of parameters in the model.
        @type num_params:           int
        @keyword spin:              The spin data container.
        @type spin:                 SpinContainer instance
        @keyword spin_id:           The spin identification string.
        @type spin_id:              str
        @keyword lower:             The lower bounds of the grid search which must be equal to the
                                    number of parameters in the model.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the
                                    number of parameters in the model.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid
                                    search.  The number of elements in the array must equal to the
                                    number of parameters in the model.
        @type inc:                  array of int
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        @keyword verbosity:         A flag specifying the amount of information to print.  The
                                    higher the value, the greater the verbosity.
        @type verbosity:            int
        """

        # Test the grid search options.
        self.test_grid_ops(lower=lower, upper=upper, inc=inc, n=num_params)

        # If inc is a single int, convert it into an array of that value.
        if isinstance(inc, int):
            inc = [inc]*num_params

        # Set up the default bounds.
        if not lower:
            # Init.
            lower = []
            upper = []

            # Determine the model type.
            model_type = self._determine_model_type()

            # Minimisation options for diffusion tensor parameters.
            if model_type == 'diff' or model_type == 'all':
                # Get the diffusion tensor specific configuration.
                self._grid_search_diff_bounds(lower, upper)

            # Model-free parameters (residue specific parameters).
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

                    # Get the spin specific configuration.
                    self._grid_search_spin_bounds(spin, lower, upper)

        # Diagonal scaling of minimisation options.
        for i in xrange(num_params):
            lower[i] = lower[i] / scaling_matrix[i, i]
            upper[i] = upper[i] / scaling_matrix[i, i]

        # Return the minimisation options.
        return inc, lower, upper


    def _grid_search_diff_bounds(self, lower, upper):
        """Set up the default grid search bounds the diffusion tensor.

        This method appends the default bounds to the lower and upper lists.

        @param lower:       The lower bound list to append to.
        @type lower:        list
        @param upper:       The upper bound list to append to.
        @type upper:        list
        """

        # Spherical diffusion {tm}.
        if cdp.diff_tensor.type == 'sphere':
            lower.append(1.0 * 1e-9)
            upper.append(12.0 * 1e-9)

        # Spheroidal diffusion {tm, Da, theta, phi}.
        if cdp.diff_tensor.type == 'spheroid':
            # tm.
            lower.append(1.0 * 1e-9)
            upper.append(12.0 * 1e-9)

            # Da.
            if cdp.diff_tensor.spheroid_type == 'prolate':
                lower.append(0.0)
                upper.append(1e7)
            elif cdp.diff_tensor.spheroid_type == 'oblate':
                lower.append(-1e7)
                upper.append(0.0)
            else:
                lower.append(-1e7)
                upper.append(1e7)

            # theta.
            lower.append(0.0)
            upper.append(pi)

            # phi.
            lower.append(0.0)
            upper.append(pi)

        # Ellipsoidal diffusion {tm, Da, Dr, alpha, beta, gamma}.
        elif cdp.diff_tensor.type == 'ellipsoid':
            # tm.
            lower.append(1.0 * 1e-9)
            upper.append(12.0 * 1e-9)

            # Da.
            lower.append(0.0)
            upper.append(1e7)

            # Dr.
            lower.append(0.0)
            upper.append(1.0)

            # alpha.
            lower.append(0.0)
            upper.append(pi)

            # beta.
            lower.append(0.0)
            upper.append(pi)

            # gamma.
            lower.append(0.0)
            upper.append(pi)


    def _grid_search_spin_bounds(self, spin, lower, upper):
        """Set up the default grid search bounds for a single spin.

        This method appends the default bounds to the lower and upper lists.  The ordering of the
        lists in min_options matches that of the params list in the spin container.

        @param spin:        A SpinContainer object.
        @type spin:         class instance
        @param lower:       The lower bound list to append to.
        @type lower:        list
        @param upper:       The upper bound list to append to.
        @type upper:        list
        """

        # Loop over the model-free parameters.
        for i in xrange(len(spin.params)):
            # Local tm.
            if spin.params[i] == 'local_tm':
                lower.append(1.0 * 1e-9)
                upper.append(12.0 * 1e-9)

            # {S2, S2f, S2s}.
            elif match('S2', spin.params[i]):
                lower.append(0.0)
                upper.append(1.0)

            # {te, tf, ts}.
            elif match('t', spin.params[i]):
                lower.append(0.0)
                upper.append(500.0 * 1e-12)

            # Rex.
            elif spin.params[i] == 'Rex':
                lower.append(0.0)
                upper.append(5.0 / (2.0 * pi * spin.frq[0])**2)

            # Bond length.
            elif spin.params[i] == 'r':
                lower.append(1.0 * 1e-10)
                upper.append(1.05 * 1e-10)

            # CSA.
            elif spin.params[i] == 'CSA':
                lower.append(-120 * 1e-6)
                upper.append(-200 * 1e-6)

            # Unknown option.
            else:
                raise RelaxError("Unknown model-free parameter.")


    def _linear_constraints(self, num_params, model_type=None, spin=None, spin_id=None, scaling_matrix=None):
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
                for l in xrange(len(spin.params)):
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
                    elif match('S2', spin.params[l]):
                        # 0 <= S2 <= 1.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.0 / scaling_matrix[i, i])
                        b.append(-1.0 / scaling_matrix[i, i])
                        j = j + 2

                        # S2 <= S2f and S2 <= S2s.
                        if spin.params[l] == 'S2':
                            for m in xrange(len(spin.params)):
                                if spin.params[m] == 'S2f' or spin.params[m] == 'S2s':
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
                            for m in xrange(len(spin.params)):
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
                    elif spin.params[l] == 'Rex':
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
                    elif spin.params[l] == 'CSA':
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
        A = array(A, float64)
        b = array(b, float64)

        return A, b


    def _minimise_data_setup(self, model_type, min_algor, num_data_sets, min_options, spin=None, sim_index=None):
        """Set up all the data required for minimisation.

        @param model_type:      The model type, one of 'all', 'diff', 'mf', or 'local_tm'.
        @type model_type:       str
        @param min_algor:       The minimisation algorithm to use.
        @type min_algor:        str
        @param num_data_sets:   The number of data sets.
        @type num_data_sets:    int
        @param min_options:     The minimisation options array.
        @type min_options:      list
        @keyword spin:          The spin data container.
        @type spin:             SpinContainer instance
        @keyword sim_index:     The optional MC simulation index.
        @type sim_index:        int
        @return:                An insane tuple.  The full tuple is (ri_data, ri_data_err, equations, param_types, param_values, r, csa, num_frq, frq, num_ri, remap_table, noe_r1_table, ri_labels, num_params, xh_unit_vectors, diff_type, diff_params)
        @rtype:                 tuple
        """

        # Initialise the data structures for the model-free function.
        ri_data = []
        ri_data_err = []
        equations = []
        param_types = []
        param_values = None
        r = []
        csa = []
        num_frq = []
        frq = []
        num_ri = []
        remap_table = []
        noe_r1_table = []
        ri_labels = []
        gx = []
        gh = []
        num_params = []
        xh_unit_vectors = []
        if model_type == 'local_tm':
            mf_params = []
        elif model_type == 'diff':
            param_values = []

        # Set up the data for the back_calc function.
        if min_algor == 'back_calc':
            # The data.
            ri_data = [0.0]
            ri_data_err = [0.000001]
            equations = [spin.equation]
            param_types = [spin.params]
            r = [spin.r]
            csa = [spin.csa]
            num_frq = [1]
            frq = [[min_options[3]]]
            num_ri = [1]
            remap_table = [[0]]
            noe_r1_table = [[None]]
            ri_labels = [[min_options[1]]]
            gx = [return_gyromagnetic_ratio(spin.heteronuc_type)]
            gh = [return_gyromagnetic_ratio(spin.proton_type)]
            if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere':
                xh_unit_vectors = [spin.xh_vect]
            else:
                xh_unit_vectors = [None]

            # Count the number of model-free parameters for the spin index.
            num_params = [len(spin.params)]

        # Loop over the number of data sets.
        for j in xrange(num_data_sets):
            # Set the spin index and get the spin, if not already set.
            if model_type == 'diff' or model_type == 'all':
                spin_index = j
                spin = return_spin_from_index(global_index=spin_index)

            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins where there is no data or errors.
            if not hasattr(spin, 'ri_data') or not hasattr(spin, 'ri_data_err'):
                continue

            # The relaxation data.
            for ri_id in cdp.ri_ids:
                # Make sure that the errors are strictly positive numbers.
                if spin.ri_data_err[ri_id] == 0.0:
                    raise RelaxError("Zero error for spin '" + repr(spin.num) + " " + spin.name + "', minimisation not possible.")
                elif spin.ri_data_err[ri_id] < 0.0:
                    raise RelaxError("Negative error for spin '" + repr(spin.num) + " " + spin.name + "', minimisation not possible.")

                # The relaxation data optimisation structures.
                data = self._relax_data_opt_structs(spin, sim_index=sim_index)

                # Append the data.
                ri_data.append(data[0])
                ri_data_err.append(data[1])
                num_frq.append(data[2])
                num_ri.append(data[3])
                ri_labels.append(data[4])
                frq.append(data[5])
                remap_table.append(data[6])
                noe_r1_table.append(data[7])

            # Repackage the data.
            equations.append(spin.equation)
            param_types.append(spin.params)
            gx.append(return_gyromagnetic_ratio(spin.heteronuc_type))
            gh.append(return_gyromagnetic_ratio(spin.proton_type))
            if sim_index == None or model_type == 'diff':
                r.append(spin.r)
                csa.append(spin.csa)
            else:
                r.append(spin.r_sim[sim_index])
                csa.append(spin.csa_sim[sim_index])

            # Model-free parameter values.
            if model_type == 'local_tm':
                pass

            # Vectors.
            if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere':
                xh_unit_vectors.append(spin.xh_vect)
            else:
                xh_unit_vectors.append(None)

            # Count the number of model-free parameters for the spin index.
            num_params.append(len(spin.params))

            # Repackage the parameter values for minimising just the diffusion tensor parameters.
            if model_type == 'diff':
                param_values.append(self._assemble_param_vector(model_type='mf'))

        # Convert to numpy arrays.
        for k in xrange(len(ri_data)):
            ri_data[k] = array(ri_data[k], float64)
            ri_data_err[k] = array(ri_data_err[k], float64)

        # Diffusion tensor type.
        if model_type == 'local_tm':
            diff_type = 'sphere'
        else:
            diff_type = cdp.diff_tensor.type

        # Package the diffusion tensor parameters.
        diff_params = None
        if model_type == 'mf':
            # Spherical diffusion.
            if diff_type == 'sphere':
                diff_params = [cdp.diff_tensor.tm]

            # Spheroidal diffusion.
            elif diff_type == 'spheroid':
                diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.theta, cdp.diff_tensor.phi]

            # Ellipsoidal diffusion.
            elif diff_type == 'ellipsoid':
                diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.Dr, cdp.diff_tensor.alpha, cdp.diff_tensor.beta, cdp.diff_tensor.gamma]
        elif min_algor == 'back_calc' and model_type == 'local_tm':
            # Spherical diffusion.
            diff_params = [spin.local_tm]

        # Return all the data.
        return ri_data, ri_data_err, equations, param_types, param_values, r, csa, num_frq, frq, num_ri, remap_table, noe_r1_table, ri_labels, gx, gh, num_params, xh_unit_vectors, diff_type, diff_params


    def _relax_data_opt_structs(self, spin, sim_index=None):
        """Package the relaxation data into the data structures used for optimisation.

        @param spin:        The spin container to extract the data from.
        @type spin:         SpinContainer instance
        @keyword sim_index: The optional MC simulation index.
        @type sim_index:    int
        @return:            The structures ri_data, ri_data_err, num_frq, num_ri, ri_labels, frq, remap_table, noe_r1_table.
        @rtype:             tuple
        """

        # Initialise the data.
        ri_data = []
        ri_data_err = []
        ri_labels = []
        frq = []
        remap_table = []
        noe_r1_table = []

        # Loop over the relaxation data.
        for ri_id in cdp.ri_ids:
            # The Rx data.
            ri_data.append(spin.ri_data[ri_id])
            ri_data_err.append(spin.ri_data_err[ri_id])

            # The labels.
            ri_labels.append(cdp.ri_types[ri_id])

            # The frequencies.
            if cdp.frq[ri_id] not in frq:
                frq.append(cdp.frq[ri_id])

            # The remap table.
            remap_table.append(frq.index(cdp.frq[ri_id]))

            # The NOE to R1 mapping table.
            noe_r1_table.append(None)

        # The number of data sets.
        num_ri = len(cdp.ri_ids)

        # Fill the NOE to R1 mapping table.
        for i in range(num_ri):
            # If the data corresponds to 'NOE', try to find if the corresponding R1 data.
            if cdp.ri_types[cdp.ri_ids[i]] == 'NOE':
                for j in range(num_ri):
                    if cdp.ri_types[cdp.ri_ids[j]] == 'R1' and cdp.frq[cdp.ri_ids[i]] == cdp.frq[cdp.ri_ids[j]]:
                        noe_r1_table[i] = j

        # Return the structures.
        return ri_data, ri_data_err, len(frq), num_ri, ri_labels, frq, remap_table, noe_r1_table


    def _reset_min_stats(self):
        """Reset all the minimisation statistics.

        All global and spin specific values will be set to None.
        """

        # Global stats.
        if hasattr(cdp, 'chi2'):
            cdp.chi2 = None
            cdp.iter = None
            cdp.f_count = None
            cdp.g_count = None
            cdp.h_count = None
            cdp.warning = None

        # Spin specific stats.
        for spin in spin_loop():
            if hasattr(spin, 'chi2'):
                spin.chi2 = None
                spin.iter = None
                spin.f_count = None
                spin.g_count = None
                spin.h_count = None
                spin.warning = None


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Calculation of the model-free chi-squared value.

        @keyword spin_id:   The spin identification string.
        @type spin_id:      str
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The optional MC simulation index.
        @type sim_index:    int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Determine the model type.
        model_type = self._determine_model_type()

        # Test if diffusion tensor data exists.
        if model_type != 'local_tm' and not diff_data_exists():
            raise RelaxNoTensorError('diffusion')

        # Test if the PDB file has been loaded.
        if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere' and not hasattr(cdp, 'structure'):
            raise RelaxNoPdbError

        # Loop over the spins.
        for spin in spin_loop(spin_id):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Test if the model-free model has been setup.
            if not spin.model:
                raise RelaxNoModelError

            # Test if unit vectors exist.
            if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere' and not hasattr(spin, 'xh_vect'):
                raise RelaxNoVectorsError

            # Test if the spin type has been set.
            if not hasattr(spin, 'heteronuc_type'):
                raise RelaxSpinTypeError

            # Test if the type attached proton has been set.
            if not hasattr(spin, 'proton_type'):
                raise RelaxProtonTypeError

            # Test if the model-free parameter values exist.
            unset_param = self._are_mf_params_set(spin)
            if unset_param != None:
                raise RelaxNoValueError(unset_param)

            # Test if the CSA value has been set.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError("CSA")

            # Test if the bond length value has been set.
            if not hasattr(spin, 'r') or spin.r == None:
                raise RelaxNoValueError("bond length")

            # Skip spins where there is no data or errors.
            if not hasattr(spin, 'ri_data') or not hasattr(spin, 'relax_error'):
                continue

            # Make sure that the errors are strictly positive numbers.
            for j in xrange(len(spin.relax_error)):
                if spin.relax_error[j] == 0.0:
                    raise RelaxError("Zero error for spin '" + repr(spin.num) + " " + spin.name + "', calculation not possible.")
                elif spin.relax_error[j] < 0.0:
                    raise RelaxError("Negative error for spin '" + repr(spin.num) + " " + spin.name + "', calculation not possible.")

            # Create the initial parameter vector.
            param_vector = self._assemble_param_vector(spin=spin, sim_index=sim_index)

            # The relaxation data optimisation structures.
            data = self._relax_data_opt_structs(spin, sim_index=sim_index)

            # Append the data.
            ri_data = [array(data[0])]
            ri_data_err = [array(data[1])]
            num_frq = [data[2]]
            num_ri = [data[3]]
            ri_labels = [data[4]]
            frq = [data[5]]
            remap_table = [data[6]]
            noe_r1_table = [data[7]]

            # Repackage the spin.
            if sim_index == None:
                r = [spin.r]
                csa = [spin.csa]
            else:
                r = [spin.r_sim[sim_index]]
                csa = [spin.csa_sim[sim_index]]

            # Vectors.
            if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere':
                xh_unit_vectors = [spin.xh_vect]
            else:
                xh_unit_vectors = [None]

            # Gyromagnetic ratios.
            gx = [return_gyromagnetic_ratio(spin.heteronuc_type)]
            gh = [return_gyromagnetic_ratio(spin.proton_type)]

            # Count the number of model-free parameters for the residue index.
            num_params = [len(spin.params)]

            # Repackage the parameter values as a local model (ignore if the diffusion tensor is not fixed).
            param_values = [self._assemble_param_vector(model_type='mf')]

            # Package the diffusion tensor parameters.
            if model_type == 'local_tm':
                diff_params = [spin.local_tm]
                diff_type = 'sphere'
            else:
                # Diff type.
                diff_type = cdp.diff_tensor.type

                # Spherical diffusion.
                if diff_type == 'sphere':
                    diff_params = [cdp.diff_tensor.tm]

                # Spheroidal diffusion.
                elif diff_type == 'spheroid':
                    diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.theta, cdp.diff_tensor.phi]

                # Ellipsoidal diffusion.
                elif diff_type == 'ellipsoid':
                    diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.Dr, cdp.diff_tensor.alpha, cdp.diff_tensor.beta, cdp.diff_tensor.gamma]

            # Initialise the model-free function.
            mf = Mf(init_params=param_vector, model_type='mf', diff_type=diff_type, diff_params=diff_params, num_spins=1, equations=[spin.equation], param_types=[spin.params], param_values=param_values, relax_data=ri_data, errors=ri_data_err, bond_length=r, csa=csa, num_frq=num_frq, frq=frq, num_ri=num_ri, remap_table=remap_table, noe_r1_table=noe_r1_table, ri_labels=ri_labels, gx=gx, gh=gh, h_bar=h_bar, mu0=mu0, num_params=num_params, vectors=xh_unit_vectors)

            # Chi-squared calculation.
            try:
                chi2 = mf.func(param_vector)
            except OverflowError:
                chi2 = 1e200

            # Global chi-squared value.
            if model_type == 'all' or model_type == 'diff':
                cdp.chi2 = cdp.chi2 + chi2
            else:
                spin.chi2 = chi2


    def grid_search(self, lower=None, upper=None, inc=None, constraints=True, verbosity=1, sim_index=None):
        """The model-free grid search function.

        @keyword lower:         The lower bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type lower:            array of numbers
        @keyword upper:         The upper bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type upper:            array of numbers
        @keyword inc:           The increments for each dimension of the space for the grid search.
                                The number of elements in the array must equal to the number of
                                parameters in the model.
        @type inc:              array of int
        @keyword constraints:   If True, constraints are applied during the grid search (eliminating
                                parts of the grid).  If False, no constraints are used.
        @type constraints:      bool
        @keyword verbosity:     A flag specifying the amount of information to print.  The higher
                                the value, the greater the verbosity.
        @type verbosity:        int
        @keyword sim_index:     The index of the simulation to apply the grid search to.  If None,
                                the normal model is optimised.
        @type sim_index:        int
        """

        # Minimisation.
        self.minimise(min_algor='grid', lower=lower, upper=upper, inc=inc, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Model-free minimisation function.

        Three categories of models exist for which the approach to minimisation is different.  These
        are:

        Single spin optimisations:  The 'mf' and 'local_tm' model types which are the
        model-free parameters for single spins, optionally with a local tm parameter.  These
        models have no global parameters.

        Diffusion tensor optimisations:  The 'diff' diffusion tensor model type.  No spin
        specific parameters exist.

        Optimisation of everything:  The 'all' model type consisting of all model-free and all
        diffusion tensor parameters.


        @keyword min_algor:         The minimisation algorithm to use.
        @type min_algor:            str
        @keyword min_options:       An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.
                                    Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.
                                    Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword constraints:       If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword scaling:           If True, diagonal scaling is enabled during optimisation to allow
                                    the problem to be better conditioned.
        @type scaling:              bool
        @keyword verbosity:         The amount of information to print.  The higher the value, the
                                    greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if
                                    normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The lower bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is only
                                    used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is only
                                    used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search.
                                    The number of elements in the array must equal to the number of
                                    parameters in the model.  This argument is only used when doing a
                                    grid search.
        @type inc:                  array of int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the model-free model has been setup, and that the heteronucleus and attached proton type have been set.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Not setup.
            if not spin.model:
                raise RelaxNoModelError

            # Test if the spin type has been set.
            if not hasattr(spin, 'heteronuc_type'):
                raise RelaxSpinTypeError

            # Test if the type attached proton has been set.
            if not hasattr(spin, 'proton_type'):
                raise RelaxProtonTypeError

        # Reset the minimisation statistics.
        if sim_index == None and min_algor != 'back_calc':
            self._reset_min_stats()

        # Determine the model type.
        model_type = self._determine_model_type()
        if not model_type:
            return

        # Model type for the back-calculate function.
        if min_algor == 'back_calc' and model_type != 'local_tm':
            model_type = 'mf'

        # Test if diffusion tensor data exists.
        if model_type != 'local_tm' and not diffusion_tensor.diff_data_exists():
            raise RelaxNoTensorError('diffusion')

        # Tests for the PDB file and unit vectors.
        if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere':
            # Test if the structure file has been loaded.
            if not hasattr(cdp, 'structure'):
                raise RelaxNoPdbError

            # Test if unit vectors exist.
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Unit vector.
                if not hasattr(spin, 'xh_vect'):
                    raise RelaxNoVectorsError

        # Test if the model-free parameter values are set for minimising diffusion tensor parameters by themselves.
        if model_type == 'diff':
            # Loop over the sequence.
            for spin in spin_loop():
                unset_param = self._are_mf_params_set(spin)
                if unset_param != None:
                    raise RelaxNoValueError(unset_param)

        # Print out.
        if verbosity >= 1:
            if model_type == 'mf':
                print("Only the model-free parameters for single spins will be used.")
            elif model_type == 'local_mf':
                print("Only a local tm value together with the model-free parameters for single spins will be used.")
            elif model_type == 'diff':
                print("Only diffusion tensor parameters will be used.")
            elif model_type == 'all':
                print("The diffusion tensor parameters together with the model-free parameters for all spins will be used.")

        # Test if the CSA and bond length values have been set.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # CSA value.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError("CSA")

            # Bond length value.
            if not hasattr(spin, 'r') or spin.r == None:
                raise RelaxNoValueError("bond length")

        # Number of spins, minimisation instances, and data sets for each model type.
        if model_type == 'mf' or model_type == 'local_tm':
            num_instances = count_spins(skip_desel=False)
            num_data_sets = 1
            num_spins = 1
        elif model_type == 'diff' or model_type == 'all':
            num_instances = 1
            num_data_sets = count_spins(skip_desel=False)
            num_spins = count_spins()

        # Number of spins, minimisation instances, and data sets for the back-calculate function.
        if min_algor == 'back_calc':
            num_instances = 1
            num_data_sets = 0
            num_spins = 1


        # Loop over the minimisation instances.
        #######################################

        for i in xrange(num_instances):
            # Get the spin container if required.
            if model_type == 'diff' or model_type == 'all':
                spin_index = None
                spin, spin_id = None, None
            elif min_algor == 'back_calc':
                spin_index = min_options[0]
                spin, spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)
            else:
                spin_index = i
                spin, spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)

            # Individual spin stuff.
            if spin and (model_type == 'mf' or model_type == 'local_tm') and not min_algor == 'back_calc':
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins missing relaxation data or errors.
                if not hasattr(spin, 'ri_data') or not hasattr(spin, 'ri_data_err'):
                    continue

            # Print out.
            if verbosity >= 1:
                # Individual spin stuff.
                if model_type == 'mf' or model_type == 'local_tm':
                    if verbosity >= 2:
                        print("\n\n")
                    string = "Fitting to spin " + repr(spin_id)
                    print(("\n\n" + string))
                    print((len(string) * '~'))

            # Parameter vector and diagonal scaling.
            if min_algor == 'back_calc':
                # Create the initial parameter vector.
                param_vector = self._assemble_param_vector(spin=spin, model_type=model_type)

                # Diagonal scaling.
                scaling_matrix = None

            else:
                # Create the initial parameter vector.
                param_vector = self._assemble_param_vector(spin=spin, sim_index=sim_index)

                # The number of parameters.
                num_params = len(param_vector)

                # Diagonal scaling.
                scaling_matrix = self._assemble_scaling_matrix(num_params, model_type=model_type, spin=spin, scaling=scaling)
                if len(scaling_matrix):
                    param_vector = dot(inv(scaling_matrix), param_vector)

            # Configure the grid search.
            if match('^[Gg]rid', min_algor):
                inc_new, lower_new, upper_new = self._grid_search_config(num_params, spin=spin, lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix)

            # Scaling of values for the set function.
            if match('^[Ss]et', min_algor):
                min_options = dot(inv(scaling_matrix), min_options)

            # Linear constraints.
            if constraints:
                A, b = self._linear_constraints(num_params, model_type=model_type, spin=spin, scaling_matrix=scaling_matrix)
            else:
                A, b = None, None

            # Initialise the iteration counter and function, gradient, and Hessian call counters.
            iter_count = 0
            f_count = 0
            g_count = 0
            h_count = 0

            # Get the data for minimisation.
            ri_data, ri_data_err, equations, param_types, param_values, r, csa, num_frq, frq, num_ri, remap_table, noe_r1_table, ri_labels, gx, gh, num_params, xh_unit_vectors, diff_type, diff_params = self._minimise_data_setup(model_type, min_algor, num_data_sets, min_options, spin=spin, sim_index=sim_index)


            # Initialise the function to minimise.
            ######################################

            self.mf = Mf(init_params=param_vector, model_type=model_type, diff_type=diff_type, diff_params=diff_params, scaling_matrix=scaling_matrix, num_spins=num_spins, equations=equations, param_types=param_types, param_values=param_values, relax_data=ri_data, errors=ri_data_err, bond_length=r, csa=csa, num_frq=num_frq, frq=frq, num_ri=num_ri, remap_table=remap_table, noe_r1_table=noe_r1_table, ri_labels=ri_labels, gx=gx, gh=gh, h_bar=h_bar, mu0=mu0, num_params=num_params, vectors=xh_unit_vectors)


            # Setup the minimisation algorithm when constraints are present.
            ################################################################

            if constraints and not match('^[Gg]rid', min_algor):
                algor = min_options[0]
            else:
                algor = min_algor


            # Levenberg-Marquardt minimisation.
            ###################################

            if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                # Total number of ri.
                number_ri = 0
                for k in xrange(len(relax_error)):
                    number_ri = number_ri + len(relax_error[k])

                # Reconstruct the error data structure.
                lm_error = zeros(number_ri, float64)
                index = 0
                for k in xrange(len(relax_error)):
                    lm_error[index:index+len(relax_error[k])] = relax_error[k]
                    index = index + len(relax_error[k])

                min_options = min_options + (self.mf.lm_dri, lm_error)


            # Back-calculation.
            ###################

            if min_algor == 'back_calc':
                return self.mf.calc_ri()


            # Minimisation.
            ###############

            # Grid search.
            if search('^[Gg]rid', min_algor):
                results = grid(func=self.mf.func, args=(), num_incs=inc_new, lower=lower_new, upper=upper_new, A=A, b=b, verbosity=verbosity)

                # Unpack the results.
                param_vector, func, iter, warning = results
                fc = iter
                gc = 0.0
                hc = 0.0

            # Minimisation.
            else:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=verbosity)

                # Unpack the results.
                if results == None:
                    continue
                param_vector, func, iter, fc, gc, hc, warning = results

            # Update the stats.
            iter_count = iter_count + iter
            f_count = f_count + fc
            g_count = g_count + gc
            h_count = h_count + hc

            # Catch infinite chi-squared values.
            if isInf(func):
                raise RelaxInfError('chi-squared')

            # Catch chi-squared values of NaN.
            if isNaN(func):
                raise RelaxNaNError('chi-squared')

            # Scaling.
            if scaling:
                param_vector = dot(scaling_matrix, param_vector)

            # Disassemble the parameter vector.
            self._disassemble_param_vector(model_type, param_vector=param_vector, spin=spin, sim_index=sim_index)

            # Monte Carlo minimisation statistics.
            if sim_index != None:
                # Sequence specific minimisation statistics.
                if model_type == 'mf' or model_type == 'local_tm':
                    # Chi-squared statistic.
                    spin.chi2_sim[sim_index] = func

                    # Iterations.
                    spin.iter_sim[sim_index] = iter_count

                    # Function evaluations.
                    spin.f_count_sim[sim_index] = f_count

                    # Gradient evaluations.
                    spin.g_count_sim[sim_index] = g_count

                    # Hessian evaluations.
                    spin.h_count_sim[sim_index] = h_count

                    # Warning.
                    spin.warning_sim[sim_index] = warning

                # Global minimisation statistics.
                elif model_type == 'diff' or model_type == 'all':
                    # Chi-squared statistic.
                    cdp.chi2_sim[sim_index] = func

                    # Iterations.
                    cdp.iter_sim[sim_index] = iter_count

                    # Function evaluations.
                    cdp.f_count_sim[sim_index] = f_count

                    # Gradient evaluations.
                    cdp.g_count_sim[sim_index] = g_count

                    # Hessian evaluations.
                    cdp.h_count_sim[sim_index] = h_count

                    # Warning.
                    cdp.warning_sim[sim_index] = warning

            # Normal statistics.
            else:
                # Sequence specific minimisation statistics.
                if model_type == 'mf' or model_type == 'local_tm':
                    # Chi-squared statistic.
                    spin.chi2 = func

                    # Iterations.
                    spin.iter = iter_count

                    # Function evaluations.
                    spin.f_count = f_count

                    # Gradient evaluations.
                    spin.g_count = g_count

                    # Hessian evaluations.
                    spin.h_count = h_count

                    # Warning.
                    spin.warning = warning

                # Global minimisation statistics.
                elif model_type == 'diff' or model_type == 'all':
                    # Chi-squared statistic.
                    cdp.chi2 = func

                    # Iterations.
                    cdp.iter = iter_count

                    # Function evaluations.
                    cdp.f_count = f_count

                    # Gradient evaluations.
                    cdp.g_count = g_count

                    # Hessian evaluations.
                    cdp.h_count = h_count

                    # Warning.
                    cdp.warning = warning
