###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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
from copy import deepcopy
from data.diff_tensor import DiffTensorSimList
from math import pi
from numpy import float64, array, identity, transpose, zeros
from re import match, search
from string import replace, split
import sys

# relax module imports.
from data import Data as relax_data_store
from float import isNaN,isInf
from generic_fns import diffusion_tensor
from generic_fns.selection import count_spins, exists_mol_res_spin_data, return_spin, return_spin_from_index, spin_loop
from maths_fns.mf import Mf
from minimise.generic import generic_minimise
from physical_constants import N15_CSA, NH_BOND_LENGTH
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxInfError, RelaxInvalidDataError, RelaxLenError, RelaxNaNError, RelaxNoModelError, RelaxNoPdbError, RelaxNoResError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoTensorError, RelaxNoValueError, RelaxNoVectorsError, RelaxNucleusError, RelaxTensorError
import specific_fns



class Model_free_main:
    """Class containing functions specific to model-free analysis."""

    def are_mf_params_set(self, spin):
        """Test if the model-free parameter values are set.

        @param spin:    The spin container object.
        @type spin:     SpinContainer instance
        @return:        The name of the first parameter in the parameter list in which the
                        corresponding parameter value is None.  If all parameters are set, then None
                        is returned.
        @rtype:         str or None
        """

        # Unselected residue.
        if spin.select == 0:
            return

        # Loop over the model-free parameters.
        for j in xrange(len(spin.params)):
            # Local tm.
            if spin.params[j] == 'local_tm' and spin.local_tm == None:
                return spin.params[j]

            # S2.
            elif spin.params[j] == 'S2' and spin.s2 == None:
                return spin.params[j]

            # S2f.
            elif spin.params[j] == 'S2f' and spin.s2f == None:
                return spin.params[j]

            # S2s.
            elif spin.params[j] == 'S2s' and spin.s2s == None:
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
            elif spin.params[j] == 'Rex' and spin.rex == None:
                return spin.params[j]

            # r.
            elif spin.params[j] == 'r' and spin.r == None:
                return spin.params[j]

            # CSA.
            elif spin.params[j] == 'CSA' and spin.csa == None:
                return spin.params[j]


    def assemble_param_names(self, model_type, spin_id=None):
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

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
                # Skip unselected residues.
                if not spin.select:
                    continue

                # Add the spin specific model-free parameters.
                param_names = param_names + spin.params


    def assemble_param_vector(self, spin=None, spin_id=None, sim_index=None, model_type=None):
        """Assemble the model-free parameter vector (as numpy array).

        If the spin argument is supplied, then the spin_id argument will be ignored.

        @keyword spin:          The spin data container.
        @type spin:             SpinContainer instance
        @keyword spin_id:       The spin identification string.
        @type spin_id:          str
        @keyword sim_index:     The optional MC simulation index.
        @type sim_index:        int
        @keyword model_type:    The optional parameter set, one of 'all', 'diff', 'mf', or
                                'local_tm'. 
        @type model_type:       str or None
        @return:                An array of the parameter values of the model-free model.
        @rtype:                 numpy array
        """

        # Initialise.
        param_vector = []

        # Determine the model type.
        if not model_type:
            model_type = self.determine_param_set_type()

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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

        # Model-free parameters (residue specific parameters).
        if model_type != 'diff':
            # The loop.
            if spin:
                loop = [spin]
            else:
                loop = spin_loop(spin_id)

            # Loop over the spins.
            for spin in loop:
                # Skip unselected residues.
                if not spin.select:
                    continue

                # Loop over the model-free parameters.
                for i in xrange(len(spin.params)):
                    # local tm.
                    if spin.params[i] == 'local_tm':
                        if sim_index == None:
                            param_vector.append(spin.local_tm)
                        else:
                            param_vector.append(spin.local_tm_sim[sim_index])

                    # S2.
                    elif spin.params[i] == 'S2':
                        if sim_index == None:
                            param_vector.append(spin.s2)
                        else:
                            param_vector.append(spin.s2_sim[sim_index])

                    # S2f.
                    elif spin.params[i] == 'S2f':
                        if sim_index == None:
                            param_vector.append(spin.s2f)
                        else:
                            param_vector.append(spin.s2f_sim[sim_index])

                    # S2s.
                    elif spin.params[i] == 'S2s':
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
                    elif spin.params[i] == 'Rex':
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
                    elif spin.params[i] == 'CSA':
                        if sim_index == None:
                            param_vector.append(spin.csa)
                        else:
                            param_vector.append(spin.csa_sim[sim_index])

                    # Unknown parameter.
                    else:
                        raise RelaxError, "Unknown parameter."

        # Replace all instances of None with 0.0 to allow the list to be converted to a numpy array.
        for i in xrange(len(param_vector)):
            if param_vector[i] == None:
                param_vector[i] = 0.0

        # Return a numpy array.
        return array(param_vector, float64)


    def assemble_scaling_matrix(self, num_params, param_set=None, spin=None, spin_id=None, scaling=True):
        """Create and return the scaling matrix.

        If the spin argument is supplied, then the spin_id argument will be ignored.

        @param num_params:      The number of parameters in the model.
        @type num_params:       int
        @keyword param_set:     The parameter set, one of 'all', 'diff', 'mf', or 'local_tm'.
        @type param_set:        str
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
        if param_set == 'diff' or param_set == 'all':
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
        if param_set != 'diff':
            # The loop.
            if spin:
                loop = [spin]
            else:
                loop = spin_loop(spin_id)

            # Loop over the spins.
            for spin in loop:
                # Skip unselected spins.
                if not spin.select:
                    continue

                # Loop over the model-free parameters.
                for k in xrange(len(spin.params)):
                    # Local tm, te, tf, and ts (must all be the same for diagonal scaling!).
                    if spin.params[k] == 'local_tm' or search('^t', spin.params[k]):
                        scaling_matrix[i, i] = ti_scaling

                    # Rex.
                    elif spin.params[k] == 'Rex':
                        scaling_matrix[i, i] = 1.0 / (2.0 * pi * spin.frq[0]) ** 2

                    # Bond length.
                    elif spin.params[k] == 'r':
                        scaling_matrix[i, i] = 1e-10

                    # CSA.
                    elif spin.params[k] == 'CSA':
                        scaling_matrix[i, i] = 1e-4

                    # Increment i.
                    i = i + 1

        # Return the scaling matrix.
        return scaling_matrix


    def create_mc_data(self, run, i):
        """Function for creating the Monte Carlo Ri data."""

        # Arguments
        self.run = run

        # Initialise the data data structure.
        data = []

        # Test if the model is set.
        if not hasattr(relax_data_store.res[self.run][i], 'model') or not relax_data_store.res[self.run][i].model:
            raise RelaxNoModelError, self.run

        # Loop over the relaxation data.
        for j in xrange(len(relax_data_store.res[run][i].relax_data)):
            # Back calculate the value.
            value = self.back_calc(run=run, index=i, ri_label=relax_data_store.res[run][i].ri_labels[j], frq_label=relax_data_store.res[run][i].frq_labels[relax_data_store.res[run][i].remap_table[j]], frq=relax_data_store.res[run][i].frq[relax_data_store.res[run][i].remap_table[j]])

            # Append the value.
            data.append(value)

        # Return the data.
        return data


    def create_model(self, model=None, equation=None, params=None, spin_id=None):
        """Function for creating a custom model-free model.

        @param model:       The name of the model.
        @type model:        str
        @param equation:    The equation type to use.  The 3 allowed types are:  'mf_orig' for the
                            original model-free equations with parameters {S2, te}; 'mf_ext' for the
                            extended model-free equations with parameters {S2f, tf, S2, ts}; and
                            'mf_ext2' for the extended model-free equations with parameters {S2f,
                            tf, S2s, ts}.
        @type equation:     str
        @param params:      A list of the parameters to include in the model.  The allowed parameter
                            names includes those for the equation type as well as chemical exchange
                            'Rex', the bond length 'r', and the chemical shift anisotropy 'CSA'.
        @type params:       list of str
        @param spin_id:     The spin identification string.
        @type spin_id:      str
        """

        # Test if the current data pipe exists.
        if not relax_data_store.current_pipe:
            raise RelaxNoPipeError

        # Test if the pipe type is 'mf'.
        function_type = relax_data_store[relax_data_store.current_pipe].pipe_type
        if function_type != 'mf':
            raise RelaxFuncSetupError, specific_fns.get_string(function_type)

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Check the validity of the model-free equation type.
        valid_types = ['mf_orig', 'mf_ext', 'mf_ext2']
        if not equation in valid_types:
            raise RelaxError, "The model-free equation type argument " + `equation` + " is invalid and should be one of " + `valid_types` + "."

        # Check the validity of the parameter array.
        s2, te, s2f, tf, s2s, ts, rex, csa, r = 0, 0, 0, 0, 0, 0, 0, 0, 0
        for i in xrange(len(params)):
            # Invalid parameter flag.
            invalid_param = 0

            # S2.
            if params[i] == 'S2':
                # Does the array contain more than one instance of S2.
                if s2:
                    invalid_param = 1
                s2 = 1

                # Does the array contain S2s.
                s2s_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2s':
                        s2s_flag = 1
                if s2s_flag:
                    invalid_param = 1

            # te.
            elif params[i] == 'te':
                # Does the array contain more than one instance of te and has the extended model-free formula been selected.
                if equation == 'mf_ext' or te:
                    invalid_param = 1
                te = 1

                # Does the array contain the parameter S2.
                s2_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2':
                        s2_flag = 1
                if not s2_flag:
                    invalid_param = 1

            # S2f.
            elif params[i] == 'S2f':
                # Does the array contain more than one instance of S2f and has the original model-free formula been selected.
                if equation == 'mf_orig' or s2f:
                    invalid_param = 1
                s2f = 1

            # S2s.
            elif params[i] == 'S2s':
                # Does the array contain more than one instance of S2s and has the original model-free formula been selected.
                if equation == 'mf_orig' or s2s:
                    invalid_param = 1
                s2s = 1

            # tf.
            elif params[i] == 'tf':
                # Does the array contain more than one instance of tf and has the original model-free formula been selected.
                if equation == 'mf_orig' or tf:
                    invalid_param = 1
                tf = 1

                # Does the array contain the parameter S2f.
                s2f_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2f':
                        s2f_flag = 1
                if not s2f_flag:
                    invalid_param = 1

            # ts.
            elif params[i] == 'ts':
                # Does the array contain more than one instance of ts and has the original model-free formula been selected.
                if equation == 'mf_orig' or ts:
                    invalid_param = 1
                ts = 1

                # Does the array contain the parameter S2 or S2s.
                flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2' or params[j] == 'S2f':
                        flag = 1
                if not flag:
                    invalid_param = 1

            # Rex.
            elif params[i] == 'Rex':
                if rex:
                    invalid_param = 1
                rex = 1

            # Bond length.
            elif params[i] == 'r':
                if r:
                    invalid_param = 1
                r = 1

            # CSA.
            elif params[i] == 'CSA':
                if csa:
                    invalid_param = 1
                csa = 1

            # Unknown parameter.
            else:
                raise RelaxError, "The parameter " + params[i] + " is not supported."

            # The invalid parameter flag is set.
            if invalid_param:
                raise RelaxError, "The parameter array " + `params` + " contains an invalid combination of parameters."

        # Set up the model.
        self.model_setup(model, equation, params, spin_id)


    def data_init(self, spin):
        """Function for initialising the spin specific data structures.

        @param spin:    The spin data container.
        @type spin:     SpinContainer instance
        """

        # Get the data names.
        data_names = self.data_names()

        # Loop over the data structure names.
        for name in data_names:
            # Data structures which are initially empty arrays.
            list_data = [ 'params' ]
            if name in list_data:
                init_data = []

            # Data structures which are initially None.
            none_data = [ 'equation',
                          'model',
                          's2',
                          's2f',
                          's2s',
                          'local_tm',
                          'te',
                          'tf',
                          'ts',
                          'rex',
                          'r',
                          'csa',
                          'nucleus',
                          'chi2',
                          'iter',
                          'f_count',
                          'g_count',
                          'h_count',
                          'warning' ]
            if name in none_data:
                init_data = None

            # If the name is not in 'spin', add it.
            if not hasattr(spin, name):
                setattr(spin, name, init_data)


    def data_names(self, set='all'):
        """Function for returning a list of names of data structures.

        Description
        ~~~~~~~~~~~

        The names are as follows:

        model:  The model-free model name.

        equation:  The model-free equation type.

        params:  An array of the model-free parameter names associated with the model.

        s2:  S2.

        s2f:  S2f.

        s2s:  S2s.

        local_tm:  local tm.

        te:  te.

        tf:  tf.

        ts:  ts.

        rex:  Rex.

        r:  Bond length.

        csa:  CSA value.

        nucleus:  The heteronucleus type.

        chi2:  Chi-squared value.

        iter:  Iterations.

        f_count:  Function count.

        g_count:  Gradient count.

        h_count:  Hessian count.

        warning:  Minimisation warning.
        """

        # Initialise.
        names = []

        # Generic.
        if set == 'all' or set == 'generic':
            names.append('model')
            names.append('equation')
            names.append('params')

        # Parameters.
        if set == 'all' or set == 'params':
            names.append('s2')
            names.append('s2f')
            names.append('s2s')
            names.append('local_tm')
            names.append('te')
            names.append('tf')
            names.append('ts')
            names.append('rex')
            names.append('r')
            names.append('csa')
            names.append('nucleus')

        # Minimisation statistics.
        if set == 'all' or set == 'min':
            names.append('chi2')
            names.append('iter')
            names.append('f_count')
            names.append('g_count')
            names.append('h_count')
            names.append('warning')

        return names


    def default_value(self, param):
        """
        Model-free default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~

        _______________________________________________________________________________________
        |                                       |                    |                        |
        | Data type                             | Object name        | Value                  |
        |_______________________________________|____________________|________________________|
        |                                       |                    |                        |
        | Local tm                              | 'local_tm'         | 10 * 1e-9              |
        |                                       |                    |                        |
        | Order parameters S2, S2f, and S2s     | 's2', 's2f', 's2s' | 0.8                    |
        |                                       |                    |                        |
        | Correlation time te                   | 'te'               | 100 * 1e-12            |
        |                                       |                    |                        |
        | Correlation time tf                   | 'tf'               | 10 * 1e-12             |
        |                                       |                    |                        |
        | Correlation time ts                   | 'ts'               | 1000 * 1e-12           |
        |                                       |                    |                        |
        | Chemical exchange relaxation          | 'rex'              | 0.0                    |
        |                                       |                    |                        |
        | Bond length                           | 'r'                | 1.02 * 1e-10           |
        |                                       |                    |                        |
        | CSA                                   | 'csa'              | -172 * 1e-6            |
        |                                       |                    |                        |
        | Heteronucleus type                    | 'heteronuc_type'   | '15N'                  |
        |                                       |                    |                        |
        | Proton type                           | 'proton_type'      | '1H'                   |
        |_______________________________________|____________________|________________________|

        """
        __docformat__ = "plaintext"

        # Local tm.
        if param == 'local_tm':
            return 10.0 * 1e-9

        # {S2, S2f, S2s}.
        elif search('^s2', param):
            return 0.8

        # te.
        elif param == 'te':
            return 100.0 * 1e-12

        # tf.
        elif param == 'tf':
            return 10.0 * 1e-12

        # ts.
        elif param == 'ts':
            return 1000.0 * 1e-12

        # Rex.
        elif param == 'rex':
            return 0.0

        # Bond length.
        elif param == 'r':
            return NH_BOND_LENGTH

        # CSA.
        elif param == 'csa':
            return N15_CSA

        # Heteronucleus type.
        elif param == 'heteronuc_type':
            return '15N'

        # Proton type.
        elif param == 'proton_type':
            return '1H'


    def delete(self, run):
        """Function for deleting all model-free data."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if the run type is set to 'mf'.
        function_type = relax_data_store.run_types[relax_data_store.run_names.index(self.run)]
        if function_type != 'mf':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if the sequence data is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Get all data structure names.
        names = self.data_names()

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure 'relax_data_store.res[self.run][i]'.
            data = relax_data_store.res[self.run][i]

            # Loop through the data structure names.
            for name in names:
                # Skip the data structure if it does not exist.
                if not hasattr(data, name):
                    continue

                # Delete the data.
                delattr(data, name)

        # Clean up the runs.
        self.relax.generic.runs.eliminate_unused_runs()


    def determine_param_set_type(self):
        """Determine the type of parameter set.

        @return:    The name of the parameter set, which is one of 'all', 'diff', 'mf', or
                    'local_tm'.
        @rtype:     str
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # If there is a local tm, fail if not all residues have a local tm parameter.
        local_tm = 0
        for spin in spin_loop():
            # Skip unselected residues.
            # This code causes a bug after model elimination if the model has been eliminated (select = 0).
            #if not spin.select:
            #    continue

            # No params.
            if not hasattr(spin, 'params') or not spin.params:
                continue

            # Local tm.
            if local_tm == 0 and 'local_tm' in spin.params:
                local_tm = 1

            # Inconsistencies.
            elif local_tm == 1 and not 'local_tm' in spin.params:
                raise RelaxError, "All residues must either have a local tm parameter or not."

        # Check if any model-free parameters are allowed to vary.
        mf_all_fixed = 1
        for spin in spin_loop():
            # Skip unselected residues.
            # This code causes a bug after model elimination if the model has been eliminated (select = 0).
            #if not spin.select:
            #    continue

            # Test the fixed flag.
            if not hasattr(spin, 'fixed'):
                mf_all_fixed = 0
                break
            if not spin.fixed:
                mf_all_fixed = 0
                break

        # Local tm.
        if local_tm:
            return 'local_tm'

        # Test if the diffusion tensor data is loaded.
        if not diffusion_tensor.diff_data_exists():
            raise RelaxNoTensorError, 'diffusion'

        # 'diff' parameter set.
        if mf_all_fixed:
            # All parameters fixed!
            if cdp.diff_tensor.fixed:
                raise RelaxError, "All parameters are fixed."

            return 'diff'

        # 'mf' parameter set.
        if cdp.diff_tensor.fixed:
            return 'mf'

        # 'all' parameter set.
        else:
            return 'all'


    def duplicate_data(self, new_run=None, old_run=None, instance=None, global_stats=0):
        """Function for duplicating data."""

        # self.run for determining the parameter set.
        self.run = old_run

        # Duplicate all non-residue specific data.
        for data_name in dir(relax_data_store):
            # Skip 'res'.
            if data_name == 'res':
                continue

            # Get the object.
            data = getattr(relax_data_store, data_name)

            # Skip the data if it is not a dictionary (or equivalent).
            if not hasattr(data, 'has_key'):
                continue

            # Skip the data if it doesn't contain the key 'old_run'.
            if not data.has_key(old_run):
                continue

            # If the dictionary already contains the key 'new_run', but the data is different, raise an error (skip PDB and diffusion data).
            if data_name != 'pdb' and data_name != 'diff' and data.has_key(new_run) and data[old_run] != data[new_run]:
                raise RelaxError, "The data between run " + `new_run` + " and run " + `old_run` + " is not consistent."

            # Skip the data if it contains the key 'new_run'.
            if data.has_key(new_run):
                continue

            # Duplicate the data.
            data[new_run] = deepcopy(data[old_run])

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Sequence specific data.
        if self.param_set == 'mf' or (self.param_set == 'local_tm' and not global_stats):
            # Create the sequence data if it does not exist.
            if not relax_data_store.res.has_key(new_run) or not len(relax_data_store.res[new_run]):
                # Add the new run to 'relax_data_store.res'.
                relax_data_store.res.add_list(new_run)

                # Fill the array 'relax_data_store.res[new_run]' with empty data containers and place sequence data into the array.
                for i in xrange(len(relax_data_store.res[old_run])):
                    # Append a data container.
                    relax_data_store.res[new_run].add_item()

                    # Insert the data.
                    relax_data_store.res[new_run][i].num = relax_data_store.res[old_run][i].num
                    relax_data_store.res[new_run][i].name = relax_data_store.res[old_run][i].name
                    relax_data_store.res[new_run][i].select = relax_data_store.res[old_run][i].select

            # Duplicate the residue specific data.
            relax_data_store.res[new_run][instance] = deepcopy(relax_data_store.res[old_run][instance])

        # Other data types.
        else:
            # Duplicate the residue specific data.
            relax_data_store.res[new_run] = deepcopy(relax_data_store.res[old_run])


    def eliminate(self, name, value, run, i, args):
        """
        Local tm model elimination rule
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        The local tm, in some cases, may exceed the value expected for a global correlation time.
        Generally the tm value will be stuck at the upper limit defined for the parameter.  These
        models are eliminated using the rule:

            tm >= c

        The default value of c is 50 ns, although this can be overridden by supplying the value (in
        seconds) as the first element of the args tuple.


        Internal correlation times {te, tf, ts} model elimination rules
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        These parameters may experience the same problem as the local tm in that the model fails and
        the parameter value is stuck at the upper limit.  These parameters are constrained using the
        formula (te, tf, ts <= 2tm).  These failed models are eliminated using the rule:

            te, tf, ts >= c . tm

        The default value of c is 1.5.  Because of round-off errors and the constraint algorithm,
        setting c to 2 will result in no models being eliminated as the minimised parameters will
        always be less than 2tm.  The value can be changed by supplying the value as the second
        element of the tuple.


        Arguments
        ~~~~~~~~~

        The 'args' argument must be a tuple of length 2, the elements of which must be numbers.  For
        example, to eliminate models which have a local tm value greater than 25 ns and models with
        internal correlation times greater than 1.5 times tm, set 'args' to (25 * 1e-9, 1.5).
        """
        __docformat__ = "plaintext"

        # Default values.
        c1 = 50.0 * 1e-9
        c2 = 1.5

        # Depack the arguments.
        if args != None:
            c1, c2 = args

        # Get the tm value.
        if self.param_set == 'local_tm':
            tm = relax_data_store.res[run][i].local_tm
        else:
            tm = relax_data_store.diff[run].tm

        # Local tm.
        if name == 'local_tm' and value >= c1:
            print "The local tm parameter of " + `value` + " is greater than " + `c1` + ", eliminating spin system " + `relax_data_store.res[run][i].num` + " " + relax_data_store.res[run][i].name + " of the run " + `run`
            return 1

        # Internal correlation times.
        if match('t[efs]', name) and value >= c2 * tm:
            print "The " + name + " value of " + `value` + " is greater than " + `c2 * tm` + ", eliminating spin system " + `relax_data_store.res[run][i].num` + " " + relax_data_store.res[run][i].name + " of the run " + `run`
            return 1

        # Accept model.
        return 0


    def get_param_names(self, run, i):
        """Function for returning a vector of parameter names."""

        # Arguments
        self.run = run

        # Skip residues where there is no data or errors.
        if not hasattr(relax_data_store.res[self.run][i], 'relax_data') or not hasattr(relax_data_store.res[self.run][i], 'relax_error'):
            return

        # Test if the model-free model has been setup.
        for j in xrange(len(relax_data_store.res[self.run])):
            # Skip unselected residues.
            if not relax_data_store.res[self.run][j].select:
                continue

            # Not setup.
            if not relax_data_store.res[self.run][j].model:
                raise RelaxNoModelError, self.run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Residue index.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            index = i
        else:
            index = None

        # Assemble the parameter names.
        self.assemble_param_names(index=index)

        # Return the parameter names.
        return self.param_names


    def get_param_values(self, run, i, sim_index=None):
        """Function for returning a vector of parameter values."""

        # Arguments
        self.run = run

        # Skip residues where there is no data or errors.
        if not hasattr(relax_data_store.res[self.run][i], 'relax_data') or not hasattr(relax_data_store.res[self.run][i], 'relax_error'):
            return

        # Test if the model-free model has been setup.
        for j in xrange(len(relax_data_store.res[self.run])):
            # Skip unselected residues.
            if not relax_data_store.res[self.run][j].select:
                continue

            # Not setup.
            if not relax_data_store.res[self.run][j].model:
                raise RelaxNoModelError, self.run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Residue index.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            index = i
        else:
            index = None

        # Assemble the parameter values.
        self.param_vector = self.assemble_param_vector(index=index, sim_index=sim_index)

        # Return the parameter names.
        return self.param_vector


    def is_spin_param(self, name):
        """Determine whether the given parameter is spin specific.

        Unless a diffusion parameter is encountered, this method will return true.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        If the parameter is a diffusion parameter, False I returned.  Otherwise True
                        is returned.
        @rtype:         bool
        """

        # Catch a diffusion parameter.
        if diffusion_tensor.return_data_name(name):
            return False

        # All the rest:
        else:
            return True


    def linear_constraints(self, num_params, param_set=None, spin=None, spin_id=None, scaling_matrix=None):
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
        @keyword param_set:         The parameter set, one of 'all', 'diff', 'mf', or 'local_tm'.
        @type param_set:            str
        @keyword spin:              The spin data container.  If this argument is supplied, then the
                                    spin_id argument will be ignored.
        @type spin:                 SpinContainer instance
        @keyword spin_id:           The spin identification string.
        @type spin_id:              str
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Upper limit flag for correlation times.
        upper_time_limit = 1

        # Initialisation (0..j..m).
        A = []
        b = []
        zero_array = zeros(num_params, float64)
        i = 0
        j = 0

        # Diffusion tensor parameters.
        if param_set != 'mf' and diffusion_tensor.diff_data_exists():
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
        if param_set != 'diff':
            # The loop.
            if spin:
                loop = [spin]
            else:
                loop = spin_loop(spin_id)

            # Loop over the spins.
            for spin in loop:
                # Skip unselected spins.
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
                                if param_set == 'mf':
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


    def map_bounds(self, param, spin_id):
        """Create bounds for the OpenDX mapping function.

        @param param:   The name of the parameter to return the lower and upper bounds of.
        @type param:    str
        @param spin_id:     The spin identification string.
        @type spin_id:      str
        @return:        The upper and lower bounds of the parameter.
        @rtype:         list of float
        """

        # Get the spin.
        spin = return_spin(spin_id)

        # {S2, S2f, S2s}.
        if search('^s2', param):
            return [0.0, 1.0]

        # {local tm, te, tf, ts}.
        elif search('^t', param) or param == 'local_tm':
            return [0.0, 1e-8]

        # Rex.
        elif param == 'rex':
            return [0.0, 30.0 / (2.0 * pi * spin.frq[0])**2]

        # Bond length.
        elif param == 'r':
            return [1.0 * 1e-10, 1.1 * 1e-10]

        # CSA.
        elif param == 'csa':
            return [-100 * 1e-6, -300 * 1e-6]


    def model_setup(self, model=None, equation=None, params=None, spin_id=None):
        """Function for updating various data structures depending on the model selected.

        @param model:       The name of the model.
        @type model:        str
        @param equation:    The equation type to use.  The 3 allowed types are:  'mf_orig' for the
                            original model-free equations with parameters {S2, te}; 'mf_ext' for the
                            extended model-free equations with parameters {S2f, tf, S2, ts}; and
                            'mf_ext2' for the extended model-free equations with parameters {S2f,
                            tf, S2s, ts}.
        @type equation:     str
        @param params:      A list of the parameters to include in the model.  The allowed parameter
                            names includes those for the equation type as well as chemical exchange
                            'Rex', the bond length 'r', and the chemical shift anisotropy 'CSA'.
        @type params:       list of str
        @param spin_id:     The spin identification string.
        @type spin_id:      str
        """

        # Test that no diffusion tensor exists if local tm is a parameter in the model.
        if params:
            for param in params:
                if param == 'local_tm' and hasattr(relax_data_store, 'diff'):
                    raise RelaxTensorError, 'diffusion'

        # Loop over the sequence.
        for spin in spin_loop(spin_id):
            # Initialise the data structures (if needed).
            self.data_init(spin)

            # Model-free model, equation, and parameter types.
            if model:
                spin.model = model
            if equation:
                spin.equation = equation
            if params:
                spin.params = params


    def model_statistics(self, instance=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword instance:      This is the optimisation instance index.  Either this or the spin_id
                                keyword argument must be supplied.
        @type instance:         None or int
        @keyword spin_id:       The spin identification string.  Either this or the instance keyword
                                argument must be supplied.
        @type spin_id:          None or str
        @keyword global_stats:  A parameter which determines if global or local statistics are
                                returned.  If None, then the appropriateness of global or local
                                statistics is automatically determined.
        @type global_stats:     None or bool
        @return:                The optimisation statistics, in tuple format, of the number of
                                parameters (k), the number of data points (n), and the chi-squared
                                value (chi2).
        @rtype:                 tuple of (int, int, float)
        """

        # Bad argument combination.
        if instance == None and spin_id == None:
            raise RelaxError, "Either the instance or spin_id argument must be supplied."
        elif instance != None and spin_id != None:
            raise RelaxError, "The instance arg " + `instance` + " and spin_id arg " + `spin_id` + " clash.  Only one should be supplied."

        # Determine if local or global statistics will be returned.
        if global_stats == None:
            global_stats = 1
            for spin in spin_loop():
                if hasattr(spin, 'chi2') and spin.chi2 != None:
                    global_stats = 0
                    break

        # Determine the parameter set type.
        param_set = self.determine_param_set_type()

        # Statistics for a single residue.
        if not global_stats:
            # Get the SpinContainer.
            if spin_id:
                spin = return_spin(spin_id)
            else:
                spin = return_spin_from_index(instance)

            # Skip unselected residues.
            if not spin.select:
                return None, None, None

            # Missing data sets.
            if not hasattr(spin, 'relax_data'):
                return None, None, None

            # Count the number of parameters.
            param_vector = self.assemble_param_vector(spin=spin)
            k = len(param_vector)

            # Count the number of data points.
            n = len(spin.relax_data)

            # The chi2 value.
            chi2 = spin.chi2

        # Global stats.
        elif global_stats:
            # Count the number of parameters.
            param_vector = self.assemble_param_vector()
            k = len(param_vector)

            # Count the number of data points.
            n = 0
            chi2 = 0
            for spin in spin_loop():
                # Skip unselected residues.
                if not spin.select:
                    continue

                # Skip residues with no relaxation data.
                if not hasattr(spin, 'relax_data') or not len(spin.relax_data):
                    continue

                n = n + len(spin.relax_data)

                # Local tm models.
                if param_set == 'local_tm':
                    chi2 = chi2 + spin.chi2

            # The chi2 value.
            if param_set != 'local_tm':
                chi2 = relax_data_store[relax_data_store.current_pipe].chi2

        # Return the data.
        return k, n, chi2


    def num_instances(self):
        """Function for returning the number of instances.

        @return:    The number of instances used for optimisation.  Either the number of spins if
                    the local optimisations are setup ('mf' and 'local_tm'), or 1 for the global
                    models.
        @rtype:     int
        """

        # Test if sequence data exists.
        if not exists_mol_res_spin_data():
            return 0

        # Determine the parameter set type.
        param_set = self.determine_param_set_type()

        # Sequence specific data.
        if param_set == 'mf' or param_set == 'local_tm':
            return count_spins()

        # Other data.
        elif param_set == 'diff' or param_set == 'all':
            return 1

        # Should not be here.
        else:
            raise RelaxFault


    def overfit_deselect(self):
        """Function for deselecting residues without sufficient data to support minimisation"""

        # Test sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Is structural data required?
        need_vect = False
        if hasattr(cdp, 'diff') and (cdp.diff_tensor.type == 'spheroid' or cdp.diff_tensor.type == 'ellipsoid'):
            need_vect = True

        # Loop over the sequence.
        for spin in spin_loop():
            # Relaxation data must exist!
            if not hasattr(spin, 'relax_data'):
                spin.select = False

            # Require 3 or more relaxation data points.
            elif len(spin.relax_data) < 3:
                spin.select = False

            # Require at least as many data points as params to prevent over-fitting.
            elif hasattr(spin, 'params') and len(spin.params) > len(spin.relax_data):
                spin.select = False

            # Test for structural data if required.
            elif need_vect and not hasattr(spin, 'xh_vect'):
                spin.select = False


    def read_columnar_col_numbers(self, header):
        """Function for sorting the column numbers from the columnar formatted results file."""

        # Initialise the hash.
        self.col = {}

        # Loop over the columns.
        for i in xrange(len(header)):
            # Residue info.
            if header[i] == 'Num':
                self.col['num'] = i
            elif header[i] == 'Name':
                self.col['name'] = i
            elif header[i] == 'Selected':
                self.col['select'] = i
            elif header[i] == 'Data_set':
                self.col['data_set'] = i
            elif header[i] == 'Nucleus':
                self.col['nucleus'] = i
            elif header[i] == 'Model':
                self.col['model'] = i
            elif header[i] == 'Equation':
                self.col['eqi'] = i
            elif header[i] == 'Params':
                self.col['params'] = i
            elif header[i] == 'Param_set':
                self.col['param_set'] = i

            # Parameters.
            elif header[i] == 'S2':
                self.col['s2'] = i
            elif header[i] == 'S2f':
                self.col['s2f'] = i
            elif header[i] == 'S2s':
                self.col['s2s'] = i
            elif search('^Local_tm', header[i]):
                self.col['local_tm'] = i
            elif search('^te', header[i]):
                self.col['te'] = i
            elif search('^tf', header[i]):
                self.col['tf'] = i
            elif search('^ts', header[i]):
                self.col['ts'] = i
            elif search('^Rex', header[i]):
                self.col['rex'] = i
            elif search('^Bond_length', header[i]):
                self.col['r'] = i
            elif search('^CSA', header[i]):
                self.col['csa'] = i

            # Minimisation info.
            elif header[i] == 'Chi-squared':
                self.col['chi2'] = i
            elif header[i] == 'Iter':
                self.col['iter'] = i
            elif header[i] == 'f_count':
                self.col['f_count'] = i
            elif header[i] == 'g_count':
                self.col['g_count'] = i
            elif header[i] == 'h_count':
                self.col['h_count'] = i
            elif header[i] == 'Warning':
                self.col['warn'] = i

            # Diffusion tensor.
            elif header[i] == 'Diff_type':
                self.col['diff_type'] = i
            elif header[i] == 'tm_(s)':
                self.col['tm'] = i
            elif header[i] == 'Da_(1/s)':
                self.col['da'] = i
            elif header[i] == 'theta_(deg)':
                self.col['theta'] = i
            elif header[i] == 'phi_(deg)':
                self.col['phi'] = i
            elif header[i] == 'Da_(1/s)':
                self.col['da'] = i
            elif header[i] == 'Dr_(1/s)':
                self.col['dr'] = i
            elif header[i] == 'alpha_(deg)':
                self.col['alpha'] = i
            elif header[i] == 'beta_(deg)':
                self.col['beta'] = i
            elif header[i] == 'gamma_(deg)':
                self.col['gamma'] = i

            # PDB and XH vector.
            elif header[i] == 'PDB':
                self.col['pdb'] = i
            elif header[i] == 'PDB_model':
                self.col['pdb_model'] = i
            elif header[i] == 'PDB_heteronuc':
                self.col['pdb_heteronuc'] = i
            elif header[i] == 'PDB_proton':
                self.col['pdb_proton'] = i
            elif header[i] == 'XH_vector':
                self.col['xh_vect'] = i

            # Relaxation data.
            elif header[i] == 'Ri_labels':
                self.col['ri_labels'] = i
            elif header[i] == 'Remap_table':
                self.col['remap_table'] = i
            elif header[i] == 'Frq_labels':
                self.col['frq_labels'] = i
            elif header[i] == 'Frequencies':
                self.col['frq'] = i


    def read_columnar_diff_tensor(self):
        """Function for setting up the diffusion tensor from the columnar formatted results file."""

        # The diffusion tensor type.
        diff_type = self.file_line[self.col['diff_type']]
        if diff_type == 'None':
            diff_type = None

        # Sphere.
        if diff_type == 'sphere':
            # Convert the parameters to floating point numbers.
            try:
                tm = float(self.file_line[self.col['tm']])
            except ValueError:
                # Errors or simulation values set to None.
                if self.data_set != 'value' and self.file_line[self.col['tm']] == 'None':
                    return

                # Genuine error.
                raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Values.
            if self.data_set == 'value':
                diff_params = tm

            # Errors.
            elif self.data_set == 'error':
                relax_data_store.diff[self.run].tm_err = tm

            # Simulation values.
            else:
                # Create the data structure if it doesn't exist.
                if not hasattr(relax_data_store.diff[self.run], 'tm_sim'):
                    relax_data_store.diff[self.run].tm_sim = DiffTensorSimList('tm', relax_data_store.diff[self.run])

                # Append the value.
                relax_data_store.diff[self.run].tm_sim.append(tm)


        # Spheroid.
        elif diff_type == 'spheroid' or diff_type == 'oblate' or diff_type == 'prolate':
            # Convert the parameters to floating point numbers.
            try:
                tm = float(self.file_line[self.col['tm']])
                Da = float(self.file_line[self.col['da']])
                theta = float(self.file_line[self.col['theta']]) / 360.0 * 2.0 * pi
                phi = float(self.file_line[self.col['phi']]) / 360.0 * 2.0 * pi
            except ValueError:
                # Errors or simulation values set to None.
                if self.data_set != 'value' and self.file_line[self.col['tm']] == 'None':
                    return

                # Genuine error.
                raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Values.
            if self.data_set == 'value':
                diff_params = [tm, Da, theta, phi]

            # Errors.
            elif self.data_set == 'error':
                relax_data_store.diff[self.run].tm_err = tm
                relax_data_store.diff[self.run].Da_err = Da
                relax_data_store.diff[self.run].theta_err = theta
                relax_data_store.diff[self.run].phi_err = phi

            # Simulation values.
            else:
                # Create the data structure if it doesn't exist.
                if not hasattr(relax_data_store.diff[self.run], 'tm_sim'):
                    relax_data_store.diff[self.run].tm_sim = DiffTensorSimList('tm', relax_data_store.diff[self.run])
                if not hasattr(relax_data_store.diff[self.run], 'Da_sim'):
                    relax_data_store.diff[self.run].Da_sim = DiffTensorSimList('Da', relax_data_store.diff[self.run])
                if not hasattr(relax_data_store.diff[self.run], 'theta_sim'):
                    relax_data_store.diff[self.run].theta_sim = DiffTensorSimList('theta', relax_data_store.diff[self.run])
                if not hasattr(relax_data_store.diff[self.run], 'phi_sim'):
                    relax_data_store.diff[self.run].phi_sim = DiffTensorSimList('phi', relax_data_store.diff[self.run])

                # Append the value.
                relax_data_store.diff[self.run].tm_sim.append(tm)
                relax_data_store.diff[self.run].Da_sim.append(Da)
                relax_data_store.diff[self.run].theta_sim.append(theta)
                relax_data_store.diff[self.run].phi_sim.append(phi)


        # Ellipsoid.
        elif diff_type == 'ellipsoid':
            # Convert the parameters to floating point numbers.
            try:
                tm = float(self.file_line[self.col['tm']])
                Da = float(self.file_line[self.col['da']])
                Dr = float(self.file_line[self.col['dr']])
                alpha = float(self.file_line[self.col['alpha']]) / 360.0 * 2.0 * pi
                beta = float(self.file_line[self.col['beta']]) / 360.0 * 2.0 * pi
                gamma = float(self.file_line[self.col['gamma']]) / 360.0 * 2.0 * pi
            except ValueError:
                # Errors or simulation values set to None.
                if self.data_set != 'value' and self.file_line[self.col['tm']] == 'None':
                    return

                # Genuine error.
                raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Values.
            if self.data_set == 'value':
                diff_params = [tm, Da, Dr, alpha, beta, gamma]

            # Errors.
            elif self.data_set == 'error':
                relax_data_store.diff[self.run].tm_err = tm
                relax_data_store.diff[self.run].Da_err = Da
                relax_data_store.diff[self.run].Dr_err = Dr
                relax_data_store.diff[self.run].alpha_err = alpha
                relax_data_store.diff[self.run].beta_err = beta
                relax_data_store.diff[self.run].gamma_err = gamma

            # Simulation values.
            else:
                # Create the data structure if it doesn't exist.
                if not hasattr(relax_data_store.diff[self.run], 'tm_sim'):
                    relax_data_store.diff[self.run].tm_sim = DiffTensorSimList('tm', relax_data_store.diff[self.run])
                if not hasattr(relax_data_store.diff[self.run], 'Da_sim'):
                    relax_data_store.diff[self.run].Da_sim = DiffTensorSimList('Da', relax_data_store.diff[self.run])
                if not hasattr(relax_data_store.diff[self.run], 'Dr_sim'):
                    relax_data_store.diff[self.run].Dr_sim = DiffTensorSimList('Dr', relax_data_store.diff[self.run])
                if not hasattr(relax_data_store.diff[self.run], 'alpha_sim'):
                    relax_data_store.diff[self.run].alpha_sim = DiffTensorSimList('alpha', relax_data_store.diff[self.run])
                if not hasattr(relax_data_store.diff[self.run], 'beta_sim'):
                    relax_data_store.diff[self.run].beta_sim = DiffTensorSimList('beta', relax_data_store.diff[self.run])
                if not hasattr(relax_data_store.diff[self.run], 'gamma_sim'):
                    relax_data_store.diff[self.run].gamma_sim = DiffTensorSimList('gamma', relax_data_store.diff[self.run])

                # Append the value.
                relax_data_store.diff[self.run].tm_sim.append(tm)
                relax_data_store.diff[self.run].Da_sim.append(Da)
                relax_data_store.diff[self.run].Dr_sim.append(Dr)
                relax_data_store.diff[self.run].alpha_sim.append(alpha)
                relax_data_store.diff[self.run].beta_sim.append(beta)
                relax_data_store.diff[self.run].gamma_sim.append(gamma)


        # Set the diffusion tensor.
        if self.data_set == 'value' and diff_type:
            # Sort out the spheroid type.
            spheroid_type = None
            if diff_type == 'oblate' or diff_type == 'prolate':
                spheroid_type = diff_type

            # Set the diffusion tensor.
            self.relax.generic.diffusion_tensor.init(run=self.run, params=diff_params, angle_units='rad', spheroid_type=spheroid_type)


    def read_columnar_find_index(self):
        """Function for generating the sequence and or returning the residue index."""

        # Residue number and name.
        try:
            self.res_num = int(self.file_line[self.col['num']])
        except ValueError:
            raise RelaxError, "The residue number " + self.file_line[self.col['num']] + " is not an integer."
        self.res_name = self.file_line[self.col['name']]

        # Find the residue index.
        res_index = None
        for j in xrange(len(relax_data_store.res[self.run])):
            if relax_data_store.res[self.run][j].num == self.res_num and relax_data_store.res[self.run][j].name == self.res_name:
                res_index = j
                break
        if res_index == None:
            raise RelaxError, "Residue " + `self.res_num` + " " + self.res_name + " cannot be found in the sequence."

        # Return the index.
        return res_index


    def read_columnar_model_free_data(self):
        """Function for reading the model-free data."""

        # Reassign data structure.
        data = relax_data_store.res[self.run][self.res_index]

        # Set up the model-free models.
        if self.data_set == 'value':
            # Get the model-free model.
            model = self.file_line[self.col['model']]

            # Get the model-free equation.
            equation = self.file_line[self.col['eqi']]

            # Get the model-free parameters.
            params = eval(self.file_line[self.col['params']])

            # Fix for the 1.2 relax versions whereby the parameter 'tm' was renamed to 'local_tm' (which occurred in version 1.2.5).
            if params:
                for i in xrange(len(params)):
                    if params[i] == 'tm':
                        params[i] = 'local_tm'

            # Set up the model-free model.
            if model and equation:
                self.model_setup(self.run, model=model, equation=equation, params=params, res_num=self.res_num)

        # Values.
        if self.data_set == 'value':
            # S2.
            try:
                data.s2 = float(self.file_line[self.col['s2']]) * self.return_conversion_factor('s2')
            except ValueError:
                data.s2 = None

            # S2f.
            try:
                data.s2f = float(self.file_line[self.col['s2f']]) * self.return_conversion_factor('s2f')
            except ValueError:
                data.s2f = None

            # S2s.
            try:
                data.s2s = float(self.file_line[self.col['s2s']]) * self.return_conversion_factor('s2s')
            except ValueError:
                data.s2s = None

            # Local tm.
            try:
                data.local_tm = float(self.file_line[self.col['local_tm']]) * self.return_conversion_factor('local_tm')
            except ValueError:
                data.local_tm = None

            # te.
            try:
                data.te = float(self.file_line[self.col['te']]) * self.return_conversion_factor('te')
            except ValueError:
                data.te = None

            # tf.
            try:
                data.tf = float(self.file_line[self.col['tf']]) * self.return_conversion_factor('tf')
            except ValueError:
                data.tf = None

            # ts.
            try:
                data.ts = float(self.file_line[self.col['ts']]) * self.return_conversion_factor('ts')
            except ValueError:
                data.ts = None

            # Rex.
            try:
                data.rex = float(self.file_line[self.col['rex']]) * self.return_conversion_factor('rex')
            except ValueError:
                data.rex = None

            # Bond length.
            try:
                data.r = float(self.file_line[self.col['r']]) * self.return_conversion_factor('r')
            except ValueError:
                data.r = None

            # CSA.
            try:
                data.csa = float(self.file_line[self.col['csa']]) * self.return_conversion_factor('csa')
            except ValueError:
                data.csa = None

            # Minimisation details (global minimisation results).
            if self.param_set == 'diff' or self.param_set == 'all':
                relax_data_store.chi2[self.run] = eval(self.file_line[self.col['chi2']])
                relax_data_store.iter[self.run] = eval(self.file_line[self.col['iter']])
                relax_data_store.f_count[self.run] = eval(self.file_line[self.col['f_count']])
                relax_data_store.g_count[self.run] = eval(self.file_line[self.col['g_count']])
                relax_data_store.h_count[self.run] = eval(self.file_line[self.col['h_count']])
                if self.file_line[self.col['warn']] == 'None':
                    relax_data_store.warning[self.run] = None
                else:
                    relax_data_store.warning[self.run] = replace(self.file_line[self.col['warn']], '_', ' ')

            # Minimisation details (individual residue results).
            else:
                data.chi2 = eval(self.file_line[self.col['chi2']])
                data.iter = eval(self.file_line[self.col['iter']])
                data.f_count = eval(self.file_line[self.col['f_count']])
                data.g_count = eval(self.file_line[self.col['g_count']])
                data.h_count = eval(self.file_line[self.col['h_count']])
                if self.file_line[self.col['warn']] == 'None':
                    data.warning = None
                else:
                    data.warning = replace(self.file_line[self.col['warn']], '_', ' ')

        # Errors.
        if self.data_set == 'error':
            # S2.
            try:
                data.s2_err = float(self.file_line[self.col['s2']]) * self.return_conversion_factor('s2')
            except ValueError:
                data.s2_err = None

            # S2f.
            try:
                data.s2f_err = float(self.file_line[self.col['s2f']]) * self.return_conversion_factor('s2f')
            except ValueError:
                data.s2f_err = None

            # S2s.
            try:
                data.s2s_err = float(self.file_line[self.col['s2s']]) * self.return_conversion_factor('s2s')
            except ValueError:
                data.s2s_err = None

            # Local tm.
            try:
                data.local_tm_err = float(self.file_line[self.col['local_tm']]) * self.return_conversion_factor('local_tm')
            except ValueError:
                data.local_tm_err = None

            # te.
            try:
                data.te_err = float(self.file_line[self.col['te']]) * self.return_conversion_factor('te')
            except ValueError:
                data.te_err = None

            # tf.
            try:
                data.tf_err = float(self.file_line[self.col['tf']]) * self.return_conversion_factor('tf')
            except ValueError:
                data.tf_err = None

            # ts.
            try:
                data.ts_err = float(self.file_line[self.col['ts']]) * self.return_conversion_factor('ts')
            except ValueError:
                data.ts_err = None

            # Rex.
            try:
                data.rex_err = float(self.file_line[self.col['rex']]) * self.return_conversion_factor('rex')
            except ValueError:
                data.rex_err = None

            # Bond length.
            try:
                data.r_err = float(self.file_line[self.col['r']]) * self.return_conversion_factor('r')
            except ValueError:
                data.r_err = None

            # CSA.
            try:
                data.csa_err = float(self.file_line[self.col['csa']]) * self.return_conversion_factor('csa')
            except ValueError:
                data.csa_err = None


        # Construct the simulation data structures.
        if self.data_set == 'sim_0':
            # Get the parameter object names.
            param_names = self.data_names(set='params')

            # Get the minimisation statistic object names.
            min_names = self.data_names(set='min')

            # Loop over all the parameter names.
            for object_name in param_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(data, sim_object_name, [])

            # Loop over all the minimisation object names.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                if self.param_set == 'diff' or self.param_set == 'all':
                    setattr(relax_data_store, sim_object_name, {})
                    object = getattr(relax_data_store, sim_object_name)
                    object[self.run] = []
                else:
                    setattr(data, sim_object_name, [])

        # Simulations.
        if self.data_set != 'value' and self.data_set != 'error':
            # S2.
            try:
                data.s2_sim.append(float(self.file_line[self.col['s2']]) * self.return_conversion_factor('s2'))
            except ValueError:
                data.s2_sim.append(None)

            # S2f.
            try:
                data.s2f_sim.append(float(self.file_line[self.col['s2f']]) * self.return_conversion_factor('s2f'))
            except ValueError:
                data.s2f_sim.append(None)

            # S2s.
            try:
                data.s2s_sim.append(float(self.file_line[self.col['s2s']]) * self.return_conversion_factor('s2s'))
            except ValueError:
                data.s2s_sim.append(None)

            # Local tm.
            try:
                data.local_tm_sim.append(float(self.file_line[self.col['local_tm']]) * self.return_conversion_factor('local_tm'))
            except ValueError:
                data.local_tm_sim.append(None)

            # te.
            try:
                data.te_sim.append(float(self.file_line[self.col['te']]) * self.return_conversion_factor('te'))
            except ValueError:
                data.te_sim.append(None)

            # tf.
            try:
                data.tf_sim.append(float(self.file_line[self.col['tf']]) * self.return_conversion_factor('tf'))
            except ValueError:
                data.tf_sim.append(None)

            # ts.
            try:
                data.ts_sim.append(float(self.file_line[self.col['ts']]) * self.return_conversion_factor('ts'))
            except ValueError:
                data.ts_sim.append(None)

            # Rex.
            try:
                data.rex_sim.append(float(self.file_line[self.col['rex']]) * self.return_conversion_factor('rex'))
            except ValueError:
                data.rex_sim.append(None)

            # Bond length.
            try:
                data.r_sim.append(float(self.file_line[self.col['r']]) * self.return_conversion_factor('r'))
            except ValueError:
                data.r_sim.append(None)

            # CSA.
            try:
                data.csa_sim.append(float(self.file_line[self.col['csa']]) * self.return_conversion_factor('csa'))
            except ValueError:
                data.csa_sim.append(None)

            # Minimisation details (global minimisation results).
            if self.param_set == 'diff' or self.param_set == 'all':
                relax_data_store.chi2_sim[self.run].append(eval(self.file_line[self.col['chi2']]))
                relax_data_store.iter_sim[self.run].append(eval(self.file_line[self.col['iter']]))
                relax_data_store.f_count_sim[self.run].append(eval(self.file_line[self.col['f_count']]))
                relax_data_store.g_count_sim[self.run].append(eval(self.file_line[self.col['g_count']]))
                relax_data_store.h_count_sim[self.run].append(eval(self.file_line[self.col['h_count']]))
                if self.file_line[self.col['warn']] == 'None':
                    relax_data_store.warning_sim[self.run].append(None)
                else:
                    relax_data_store.warning_sim[self.run].append(replace(self.file_line[self.col['warn']], '_', ' '))

            # Minimisation details (individual residue results).
            else:
                data.chi2_sim.append(eval(self.file_line[self.col['chi2']]))
                data.iter_sim.append(eval(self.file_line[self.col['iter']]))
                data.f_count_sim.append(eval(self.file_line[self.col['f_count']]))
                data.g_count_sim.append(eval(self.file_line[self.col['g_count']]))
                data.h_count_sim.append(eval(self.file_line[self.col['h_count']]))
                if self.file_line[self.col['warn']] == 'None':
                    data.warning_sim.append(None)
                else:
                    data.warning_sim.append(replace(self.file_line[self.col['warn']], '_', ' '))


    def read_columnar_param_set(self):
        """Function for reading the parameter set."""

        # Extract the parameter set if it exists, otherwise return.
        if self.file_line[self.col['param_set']] != 'None':
            self.param_set = self.file_line[self.col['param_set']]
        else:
            return

        # Local tm and model-free only parameter sets.
        if self.param_set == 'local_tm' or self.param_set == 'mf':
            diff_fixed = 1
            res_fixed = 0

        # Diffusion tensor parameter set.
        elif self.param_set == 'diff':
            diff_fixed = 0
            res_fixed = 1

        # 'all' parameter set.
        elif self.param_set == 'all':
            diff_fixed = 0
            res_fixed = 0

        # No parameter set.
        elif self.param_set == 'None':
            self.param_set = None
            diff_fixed = None
            res_fixed = None

        # Set the diffusion tensor fixed flag.
        if self.param_set != 'local_tm' and diff_fixed != None:
            relax_data_store.diff[self.run].fixed = diff_fixed

        # Set the residue specific fixed flag.
        for i in xrange(len(relax_data_store.res[self.run])):
            if res_fixed != None:
                relax_data_store.res[self.run][i].fixed = res_fixed


    def read_columnar_pdb(self, verbosity=1):
        """Function for reading the PDB file."""

        # File name.
        pdb = self.file_line[self.col['pdb']]

        # PDB model.
        pdb_model = eval(self.file_line[self.col['pdb_model']])

        # Read the PDB file (if it exists).
        if not pdb == 'None':
            self.relax.generic.structure.read_pdb(run=self.run, file=pdb, model=pdb_model, fail=0, verbosity=verbosity)
            return 1
        else:
            return 0


    def read_columnar_relax_data(self):
        """Function for reading the relaxation data."""

        # Skip the error 'data_set'.
        if self.data_set == 'error':
            return

        # Relaxation data structures.
        self.ri_labels = eval(self.file_line[self.col['ri_labels']])
        self.remap_table = eval(self.file_line[self.col['remap_table']])
        self.frq_labels = eval(self.file_line[self.col['frq_labels']])
        self.frq = eval(self.file_line[self.col['frq']])

        # No relaxation data.
        if not self.ri_labels:
            return

        # Initialise the value and error arrays.
        values = []
        errors = []

        # Loop over the relaxation data of the residue.
        for i in xrange(len(self.ri_labels)):
            # Determine the data and error columns for this relaxation data set.
            data_col = self.col['frq'] + i + 1
            error_col = self.col['frq'] + len(self.ri_labels) + i + 1

            # Append the value and error.
            values.append(eval(self.file_line[data_col]))
            errors.append(eval(self.file_line[error_col]))

        # Simulations.
        sim = 0
        if self.data_set != 'value' and self.data_set != 'error':
            sim = 1

        # Add the relaxation data.
        self.relax.specific.relax_data.add_residue(run=self.run, res_index=self.res_index, ri_labels=self.ri_labels, remap_table=self.remap_table, frq_labels=self.frq_labels, frq=self.frq, values=values, errors=errors, sim=sim)


    def read_columnar_results(self, run, file_data, verbosity=1):
        """Function for reading the results file."""

        # Arguments.
        self.run = run

        # Extract and remove the header.
        header = file_data[0]
        file_data = file_data[1:]

        # Sort the column numbers.
        self.read_columnar_col_numbers(header)

        # Test the file.
        if len(self.col) < 2:
            raise RelaxInvalidDataError

        # Initialise some data structures and flags.
        nucleus_set = 0
        sim_num = None
        sims = []
        all_select_sim = []
        diff_data_set = 0
        diff_error_set = 0
        diff_sim_set = None
        self.param_set = None
        pdb = 0
        pdb_model = None
        pdb_heteronuc = None
        pdb_proton = None
        self.ri_labels = None

        # Generate the sequence.
        for self.file_line in file_data:
            # The data set.
            self.data_set = self.file_line[self.col['data_set']]

            # Stop creating the sequence once the data_set is no longer 'value'.
            if self.data_set != 'value':
                break

            # Sequence.
            self.read_columnar_sequence()


        # Loop over the lines of the file data.
        for self.file_line in file_data:
            # The data set.
            self.data_set = self.file_line[self.col['data_set']]

            # Find the residue index.
            self.res_index = self.read_columnar_find_index()

            # Reassign data structure.
            data = relax_data_store.res[self.run][self.res_index]

            # Backwards compatibility for the reading of the results file from versions 1.2.0 to 1.2.9.
            if len(self.file_line) == 4:
                continue

            # Set the nucleus type.
            if not nucleus_set:
                if self.file_line[self.col['nucleus']] != 'None':
                    self.relax.generic.nuclei.set_values(self.file_line[self.col['nucleus']])
                    nucleus_set = 1

            # Simulation number.
            if self.data_set != 'value' and self.data_set != 'error':
                # Extract the number from the self.data_set string.
                sim_num = split(self.data_set, '_')
                try:
                    sim_num = int(sim_num[1])
                except:
                    raise RelaxError, "The simulation number '%s' is invalid." % sim_num

                # A new simulation number.
                if sim_num not in sims:
                    # Update the sims array and append an empty array to the selected sims array.
                    sims.append(sim_num)
                    all_select_sim.append([])

                # Selected simulations.
                all_select_sim[-1].append(int(self.file_line[self.col['select']]))

            # Diffusion tensor data.
            if self.data_set == 'value' and not diff_data_set:
                self.read_columnar_diff_tensor()
                diff_data_set = 1

            # Diffusion tensor errors.
            elif self.data_set == 'error' and not diff_error_set:
                self.read_columnar_diff_tensor()
                diff_error_set = 1

            # Diffusion tensor simulation data.
            elif self.data_set != 'value' and self.data_set != 'error' and sim_num != diff_sim_set:
                self.read_columnar_diff_tensor()
                diff_sim_set = sim_num

            # Parameter set.
            if self.param_set == None:
                self.read_columnar_param_set()

            # PDB.
            if not pdb:
                if self.read_columnar_pdb(verbosity):
                    pdb = 1

            # XH vector, heteronucleus, and proton.
            if self.data_set == 'value':
                self.read_columnar_xh_vect()

            # Relaxation data.
            self.read_columnar_relax_data()

            # Model-free data.
            self.read_columnar_model_free_data()

        # Set up the simulations.
        if len(sims):
            # Convert the selected simulation array of arrays into a Numeric matrix and transpose it.
            all_select_sim = transpose(array(all_select_sim))

            # Set up the Monte Carlo simulations.
            self.relax.generic.monte_carlo.setup(self.run, number=len(sims), all_select_sim=all_select_sim)

            # Turn the simulation state to off!
            relax_data_store.sim_state[self.run] = 0


    def read_columnar_sequence(self):
        """Function for generating the sequence."""

        # Residue number and name.
        try:
            res_num = int(self.file_line[self.col['num']])
        except ValueError:
            raise RelaxError, "The residue number " + self.file_line[self.col['num']] + " is not an integer."
        res_name = self.file_line[self.col['name']]

        # Generate the sequence.
        self.relax.generic.sequence.add(self.run, res_num, res_name, select=int(self.file_line[self.col['select']]))


    def read_columnar_xh_vect(self):
        """Function for reading the XH unit vectors."""

        # The vector.
        xh_vect = eval(self.file_line[self.col['xh_vect']])
        if xh_vect:
            # Numeric array format.
            try:
                xh_vect = array(xh_vect, float64)
            except:
                raise RelaxError, "The XH unit vector " + self.file_line[self.col['xh_vect']] + " is invalid."

            # Set the vector.
            self.relax.generic.structure.set_vector(run=self.run, res=self.res_index, xh_vect=xh_vect)

        # The heteronucleus and proton names.
        relax_data_store.res[self.run][self.res_index].heteronuc = self.file_line[self.col['pdb_heteronuc']]
        relax_data_store.res[self.run][self.res_index].proton = self.file_line[self.col['pdb_proton']]


    def remove_tm(self, run, res_num):
        """Function for removing the local tm parameter from the model-free parameters."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if the run type is set to 'mf'.
        function_type = relax_data_store.run_types[relax_data_store.run_names.index(self.run)]
        if function_type != 'mf':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Remap the data structure.
            data = relax_data_store.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # If res_num is set, then skip all other residues.
            if res_num != None and res_num != data.num:
                continue

            # Test if a local tm parameter exists.
            if not hasattr(data, 'params') or not 'local_tm' in data.params:
                continue

            # Remove tm.
            data.params.remove('local_tm')

            # Model name.
            if match('^tm', data.model):
                data.model = data.model[1:]

            # Set the local tm value to None.
            data.local_tm = None

            # Set all the minimisation details to None.
            data.chi2 = None
            data.iter = None
            data.f_count = None
            data.g_count = None
            data.h_count = None
            data.warning = None

        # Set the global minimisation details to None.
        relax_data_store.chi2[self.run] = None
        relax_data_store.iter[self.run] = None
        relax_data_store.f_count[self.run] = None
        relax_data_store.g_count[self.run] = None
        relax_data_store.h_count[self.run] = None
        relax_data_store.warning[self.run] = None


    def return_conversion_factor(self, param, spin_id):
        """Return the factor of conversion between different parameter units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return 1e-12 for te.


        @param param:   The name of the parameter to return the conversion factor for.
        @type param:    str
        @param spin_id: The spin identification string.
        @type spin_id:  str
        @return:        The conversion factor.
        @rtype:         float
        """

        # Get the spin.
        spin = return_spin(spin_id)

        # Get the object name.
        object_name = self.return_data_name(param)

        # tm (nanoseconds).
        if object_name == 'tm' or object_name == 'local_tm':
            return 1e-9

        # te, tf, and ts (picoseconds).
        elif object_name in ['te', 'tf', 'ts']:
            return 1e-12

        # Rex (value at 1st field strength).
        elif object_name == 'rex':
            return 1.0 / (2.0 * pi * spin.frq[0])**2

        # Bond length (Angstrom).
        elif object_name == 'r':
            return 1e-10

        # CSA (ppm).
        elif object_name == 'csa':
            return 1e-6

        # No conversion factor.
        else:
            return 1.0


    def return_data_name(self, name):
        """
        Model-free data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |                  |                                              |
        | Data type              | Object name      | Patterns                                     |
        |________________________|__________________|______________________________________________|
        |                        |                  |                                              |
        | Local tm               | 'local_tm'       | '[Ll]ocal[ -_]tm'                            |
        |                        |                  |                                              |
        | Order parameter S2     | 's2'             | '^[Ss]2$'                                    |
        |                        |                  |                                              |
        | Order parameter S2f    | 's2f'            | '^[Ss]2f$'                                   |
        |                        |                  |                                              |
        | Order parameter S2s    | 's2s'            | '^[Ss]2s$'                                   |
        |                        |                  |                                              |
        | Correlation time te    | 'te'             | '^te$'                                       |
        |                        |                  |                                              |
        | Correlation time tf    | 'tf'             | '^tf$'                                       |
        |                        |                  |                                              |
        | Correlation time ts    | 'ts'             | '^ts$'                                       |
        |                        |                  |                                              |
        | Chemical exchange      | 'rex'            | '^[Rr]ex$' or '[Cc]emical[ -_][Ee]xchange'   |
        |                        |                  |                                              |
        | Bond length            | 'r'              | '^r$' or '[Bb]ond[ -_][Ll]ength'             |
        |                        |                  |                                              |
        | CSA                    | 'csa'            | '^[Cc][Ss][Aa]$'                             |
        |                        |                  |                                              |
        | Heteronucleus type     | 'heteronuc_type' | '^[Hh]eteronucleus$'                         |
        |                        |                  |                                              |
        | Proton type            | 'proton_type'    | '^[Pp]roton$'                                |
        |________________________|__________________|______________________________________________|

        """
        __docformat__ = "plaintext"

        # Local tm.
        if search('[Ll]ocal[ -_]tm', name):
            return 'local_tm'

        # Order parameter S2.
        if search('^[Ss]2$', name):
            return 's2'

        # Order parameter S2f.
        if search('^[Ss]2f$', name):
            return 's2f'

        # Order parameter S2s.
        if search('^[Ss]2s$', name):
            return 's2s'

        # Correlation time te.
        if search('^te$', name):
            return 'te'

        # Correlation time tf.
        if search('^tf$', name):
            return 'tf'

        # Correlation time ts.
        if search('^ts$', name):
            return 'ts'

        # Rex.
        if search('^[Rr]ex$', name) or search('[Cc]emical[ -_][Ee]xchange', name):
            return 'rex'

        # Bond length.
        if search('^r$', name) or search('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if search('^[Cc][Ss][Aa]$', name):
            return 'csa'

        # Heteronucleus type.
        if search('^[Hh]eteronucleus$', name):
            return 'heteronuc_type'

        # Proton type.
        if search('^[Pp]roton$', name):
            return 'proton_type'


    def return_grace_string(self, param):
        """Function for returning the Grace string representing the parameter for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(param)

        # Local tm.
        if object_name == 'tm' or object_name == 'local_tm':
            return '\\xt\\f{}\\sm'

        # Order parameter S2.
        elif object_name == 's2':
            return '\\qS\\v{0.4}\\z{0.71}2\\Q'

        # Order parameter S2f.
        elif object_name == 's2f':
            return '\\qS\\sf\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q'

        # Order parameter S2s.
        elif object_name == 's2s':
            return '\\qS\\ss\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q'

        # Correlation time te.
        elif object_name == 'te':
            return '\\xt\\f{}\\se'

        # Correlation time tf.
        elif object_name == 'tf':
            return '\\xt\\f{}\\sf'

        # Correlation time ts.
        elif object_name == 'ts':
            return '\\xt\\f{}\\ss'

        # Rex.
        elif object_name == 'rex':
            return '\\qR\\sex\\Q'

        # Bond length.
        elif object_name == 'r':
            return 'Bond length'

        # CSA.
        elif object_name == 'csa':
            return '\\qCSA\\Q'


    def return_units(self, param, spin_id):
        """Function for returning a string representing the parameters units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return the string
        'picoseconds' for te.


        @param param:   The name of the parameter to return the units string for.
        @type param:    str
        @param spin_id: The spin identification string.
        @type spin_id:  str
        @return:        The parameter units string.
        @rtype:         str
        """

        # Get the spin.
        spin = return_spin(spin_id)

        # Get the object name.
        object_name = self.return_data_name(param)

        # tm (nanoseconds).
        if object_name == 'tm' or object_name == 'local_tm':
            return 'ns'

        # te, tf, and ts (picoseconds).
        elif object_name in ['te', 'tf', 'ts']:
            return 'ps'

        # Rex (value at 1st field strength).
        elif object_name == 'rex':
            return spin.frq_labels[0] + ' MHz'

        # Bond length (Angstrom).
        elif object_name == 'r':
            return 'Angstrom'

        # CSA (ppm).
        elif object_name == 'csa':
            return 'ppm'


    def select_model(self, model=None, spin_id=None):
        """Function for the selection of a preset model-free model.

        @param model:   The name of the model.
        @type model:    str
        @param spin_id: The spin identification string.
        @type spin_id:  str
        """

        # Test if the current data pipe exists.
        if not relax_data_store.current_pipe:
            raise RelaxNoPipeError

        # Test if the pipe type is 'mf'.
        function_type = relax_data_store[relax_data_store.current_pipe].pipe_type
        if function_type != 'mf':
            raise RelaxFuncSetupError, specific_fns.get_string(function_type)

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError


        # Preset models.
        ################

        # Block 1.
        if model == 'm0':
            equation = 'mf_orig'
            params = []
        elif model == 'm1':
            equation = 'mf_orig'
            params = ['S2']
        elif model == 'm2':
            equation = 'mf_orig'
            params = ['S2', 'te']
        elif model == 'm3':
            equation = 'mf_orig'
            params = ['S2', 'Rex']
        elif model == 'm4':
            equation = 'mf_orig'
            params = ['S2', 'te', 'Rex']
        elif model == 'm5':
            equation = 'mf_ext'
            params = ['S2f', 'S2', 'ts']
        elif model == 'm6':
            equation = 'mf_ext'
            params = ['S2f', 'tf', 'S2', 'ts']
        elif model == 'm7':
            equation = 'mf_ext'
            params = ['S2f', 'S2', 'ts', 'Rex']
        elif model == 'm8':
            equation = 'mf_ext'
            params = ['S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm9':
            equation = 'mf_orig'
            params = ['Rex']

        # Block 2.
        elif model == 'm10':
            equation = 'mf_orig'
            params = ['CSA']
        elif model == 'm11':
            equation = 'mf_orig'
            params = ['CSA', 'S2']
        elif model == 'm12':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'te']
        elif model == 'm13':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'Rex']
        elif model == 'm14':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'te', 'Rex']
        elif model == 'm15':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'S2', 'ts']
        elif model == 'm16':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm17':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm18':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm19':
            equation = 'mf_orig'
            params = ['CSA', 'Rex']

        # Block 3.
        elif model == 'm20':
            equation = 'mf_orig'
            params = ['r']
        elif model == 'm21':
            equation = 'mf_orig'
            params = ['r', 'S2']
        elif model == 'm22':
            equation = 'mf_orig'
            params = ['r', 'S2', 'te']
        elif model == 'm23':
            equation = 'mf_orig'
            params = ['r', 'S2', 'Rex']
        elif model == 'm24':
            equation = 'mf_orig'
            params = ['r', 'S2', 'te', 'Rex']
        elif model == 'm25':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'S2', 'ts']
        elif model == 'm26':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm27':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm28':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm29':
            equation = 'mf_orig'
            params = ['r', 'Rex']

        # Block 4.
        elif model == 'm30':
            equation = 'mf_orig'
            params = ['r', 'CSA']
        elif model == 'm31':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2']
        elif model == 'm32':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'te']
        elif model == 'm33':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'Rex']
        elif model == 'm34':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'm35':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'm36':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm37':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm38':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm39':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'Rex']


        # Preset models with local correlation time.
        ############################################

        # Block 1.
        elif model == 'tm0':
            equation = 'mf_orig'
            params = ['local_tm']
        elif model == 'tm1':
            equation = 'mf_orig'
            params = ['local_tm', 'S2']
        elif model == 'tm2':
            equation = 'mf_orig'
            params = ['local_tm', 'S2', 'te']
        elif model == 'tm3':
            equation = 'mf_orig'
            params = ['local_tm', 'S2', 'Rex']
        elif model == 'tm4':
            equation = 'mf_orig'
            params = ['local_tm', 'S2', 'te', 'Rex']
        elif model == 'tm5':
            equation = 'mf_ext'
            params = ['local_tm', 'S2f', 'S2', 'ts']
        elif model == 'tm6':
            equation = 'mf_ext'
            params = ['local_tm', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm7':
            equation = 'mf_ext'
            params = ['local_tm', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm8':
            equation = 'mf_ext'
            params = ['local_tm', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm9':
            equation = 'mf_orig'
            params = ['local_tm', 'Rex']

        # Block 2.
        elif model == 'tm10':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA']
        elif model == 'tm11':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA', 'S2']
        elif model == 'tm12':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA', 'S2', 'te']
        elif model == 'tm13':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA', 'S2', 'Rex']
        elif model == 'tm14':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm15':
            equation = 'mf_ext'
            params = ['local_tm', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm16':
            equation = 'mf_ext'
            params = ['local_tm', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm17':
            equation = 'mf_ext'
            params = ['local_tm', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm18':
            equation = 'mf_ext'
            params = ['local_tm', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm19':
            equation = 'mf_orig'
            params = ['local_tm', 'CSA', 'Rex']

        # Block 3.
        elif model == 'tm20':
            equation = 'mf_orig'
            params = ['local_tm', 'r']
        elif model == 'tm21':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'S2']
        elif model == 'tm22':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'S2', 'te']
        elif model == 'tm23':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'S2', 'Rex']
        elif model == 'tm24':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'S2', 'te', 'Rex']
        elif model == 'tm25':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'S2f', 'S2', 'ts']
        elif model == 'tm26':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm27':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm28':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm29':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'Rex']

        # Block 4.
        elif model == 'tm30':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA']
        elif model == 'tm31':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA', 'S2']
        elif model == 'tm32':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA', 'S2', 'te']
        elif model == 'tm33':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA', 'S2', 'Rex']
        elif model == 'tm34':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm35':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm36':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm37':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm38':
            equation = 'mf_ext'
            params = ['local_tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm39':
            equation = 'mf_orig'
            params = ['local_tm', 'r', 'CSA', 'Rex']

        # Invalid model.
        else:
            raise RelaxError, "The model '" + model + "' is invalid."

        # Set up the model.
        self.model_setup(model, equation, params, spin_id)


    def set_doc(self):
        """
        Model-free set details
        ~~~~~~~~~~~~~~~~~~~~~~

        Setting a parameter value may have no effect depending on which model-free model is chosen,
        for example if S2f values and S2s values are set but the run corresponds to model-free model
        'm4' then, because these data values are not parameters of the model, they will have no
        effect.

        Note that the Rex values are scaled quadratically with field strength and should be supplied
        as a field strength independent value.  Use the following formula to get the correct value:

            value = Rex / (2.0 * pi * frequency) ** 2

        where:
            Rex is the chemical exchange value for the current frequency.
            pi is in the namespace of relax, ie just type 'pi'.
            frequency is the proton frequency corresponding to the data.
        """
        __docformat__ = "plaintext"


    def set_error(self, run, instance, index, error):
        """Function for setting parameter errors."""

        # Arguments.
        self.run = run

        # Parameter increment counter.
        inc = 0

        # Get the parameter object names.
        param_names = self.data_names(set='params')


        # Diffusion tensor parameter errors.
        ####################################

        if self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion.
            if relax_data_store.diff[self.run].type == 'sphere':
                # Return the parameter array.
                if index == 0:
                    relax_data_store.diff[self.run].tm_err = error

                # Increment.
                inc = inc + 1

            # Spheroidal diffusion.
            elif relax_data_store.diff[self.run].type == 'spheroid':
                # Return the parameter array.
                if index == 0:
                    relax_data_store.diff[self.run].tm_err = error
                elif index == 1:
                    relax_data_store.diff[self.run].Da_err = error
                elif index == 2:
                    relax_data_store.diff[self.run].theta_err = error
                elif index == 3:
                    relax_data_store.diff[self.run].phi_err = error

                # Increment.
                inc = inc + 4

            # Ellipsoidal diffusion.
            elif relax_data_store.diff[self.run].type == 'ellipsoid':
                # Return the parameter array.
                if index == 0:
                    relax_data_store.diff[self.run].tm_err = error
                elif index == 1:
                    relax_data_store.diff[self.run].Da_err = error
                elif index == 2:
                    relax_data_store.diff[self.run].Dr_err = error
                elif index == 3:
                    relax_data_store.diff[self.run].alpha_err = error
                elif index == 4:
                    relax_data_store.diff[self.run].beta_err = error
                elif index == 5:
                    relax_data_store.diff[self.run].gamma_err = error

                # Increment.
                inc = inc + 6


        # Model-free parameter errors for the parameter set 'all'.
        ##########################################################

        if self.param_set == 'all':
            # Loop over the sequence.
            for i in xrange(len(relax_data_store.res[self.run])):
                # Skip unselected residues.
                if not relax_data_store.res[self.run][i].select:
                    continue

                # Loop over the residue specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        setattr(relax_data_store.res[self.run][i], param + "_err", error)

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the parameter sets 'mf' and 'local_tm'.
        ###################################################################

        if self.param_set == 'mf' or self.param_set == 'local_tm':
            # Skip unselected residues.
            if not relax_data_store.res[self.run][instance].select:
                return

            # Loop over the residue specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    setattr(relax_data_store.res[self.run][instance], param + "_err", error)

                # Increment.
                inc = inc + 1


    def set_non_spin_params(self, value=None, param=None):
        """Set the non-spin specific model-free params (this is solely the diffusion params).

        @param value:   The parameter values.
        @type value:    None, number, or list of numbers
        @param param:   The parameter names.
        @type param:    None, str, or list of str
        """

        # Call the diffusion tensor parameter setting function.
        diffusion_tensor.set(value=value, param=param)


    def set_selected_sim(self, run, instance, select_sim):
        """Function for returning the array of selected simulation flags."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Single instance.
        if self.param_set == 'all' or self.param_set == 'diff':
            if not hasattr(relax_data_store, 'select_sim'):
                relax_data_store.select_sim = {}
            relax_data_store.select_sim[self.run] = select_sim

        # Multiple instances.
        else:
            relax_data_store.res[self.run][instance].select_sim = select_sim


    def set_update(self, param, spin):
        """Function to update the other model-free parameters.

        @param param:   The name of the parameter which has been changed.
        @type param:    str
        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        """

        # S2f parameter.
        if param == 'S2f':
            # Update S2 if S2s exists.
            if hasattr(spin, 's2s') and spin.s2s != None:
                spin.s2 = spin.s2f * spin.s2s


        # S2s parameter.
        if param == 'S2s':
            # Update S2 if S2f exists.
            if hasattr(spin, 's2f') and spin.s2f != None:
                spin.s2 = spin.s2f * spin.s2s


    def sim_init_values(self, run):
        """Function for initialising Monte Carlo parameter values."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')

        # List of diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion.
            if relax_data_store.diff[self.run].type == 'sphere':
                diff_params = ['tm']

            # Spheroidal diffusion.
            elif relax_data_store.diff[self.run].type == 'spheroid':
                diff_params = ['tm', 'Da', 'theta', 'phi']

            # Ellipsoidal diffusion.
            elif relax_data_store.diff[self.run].type == 'ellipsoid':
                diff_params = ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma']


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Diffusion tensor parameters and non residue specific minimisation statistics.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Loop over the parameters.
            for object_name in diff_params:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(relax_data_store.diff[self.run], sim_object_name):
                    raise RelaxError, "Monte Carlo parameter values have already been set."

            # Loop over the minimisation stats objects.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(relax_data_store, sim_object_name):
                    raise RelaxError, "Monte Carlo parameter values have already been set."

        # Residue specific parameters.
        if self.param_set != 'diff':
            for i in xrange(len(relax_data_store.res[self.run])):
                # Skip unselected residues.
                if not relax_data_store.res[self.run][i].select:
                    continue

                # Loop over all the parameter names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Test if the simulation object already exists.
                    if hasattr(relax_data_store.res[self.run][i], sim_object_name):
                        raise RelaxError, "Monte Carlo parameter values have already been set."


        # Set the Monte Carlo parameter values.
        #######################################

        # Loop over the global minimisation stats objects.
        for object_name in min_names:
            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Create the simulation object.
            setattr(relax_data_store, sim_object_name, {})

            # Get the simulation object.
            sim_object = getattr(relax_data_store, sim_object_name)

            # Add the run.
            sim_object[self.run] = []

            # Loop over the simulations.
            for j in xrange(relax_data_store.sim_number[self.run]):
                # Get the object.
                object = getattr(relax_data_store, object_name)

                # Test if the object has the key self.run.
                if not object.has_key(self.run):
                    continue

                # Copy and append the data.
                sim_object[self.run].append(deepcopy(object[self.run]))

        # Diffusion tensor parameters and non residue specific minimisation statistics.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Loop over the parameters.
            for object_name in diff_params:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(relax_data_store.diff[self.run], sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(relax_data_store.diff[self.run], sim_object_name)

                # Loop over the simulations.
                for j in xrange(relax_data_store.sim_number[self.run]):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(relax_data_store.diff[self.run], object_name)))

        # Residue specific parameters.
        if self.param_set != 'diff':
            for i in xrange(len(relax_data_store.res[self.run])):
                # Skip unselected residues.
                if not relax_data_store.res[self.run][i].select:
                    continue

                # Loop over all the data names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    setattr(relax_data_store.res[self.run][i], sim_object_name, [])

                    # Get the simulation object.
                    sim_object = getattr(relax_data_store.res[self.run][i], sim_object_name)

                    # Loop over the simulations.
                    for j in xrange(relax_data_store.sim_number[self.run]):
                        # Copy and append the data.
                        sim_object.append(deepcopy(getattr(relax_data_store.res[self.run][i], object_name)))

                # Loop over all the minimisation object names.
                for object_name in min_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    setattr(relax_data_store.res[self.run][i], sim_object_name, [])

                    # Get the simulation object.
                    sim_object = getattr(relax_data_store.res[self.run][i], sim_object_name)

                    # Loop over the simulations.
                    for j in xrange(relax_data_store.sim_number[self.run]):
                        # Copy and append the data.
                        sim_object.append(deepcopy(getattr(relax_data_store.res[self.run][i], object_name)))


    def sim_pack_data(self, run, i, sim_data):
        """Function for packing Monte Carlo simulation data."""

        # Test if the simulation data already exists.
        if hasattr(relax_data_store.res[run][i], 'relax_sim_data'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        relax_data_store.res[run][i].relax_sim_data = sim_data


    def sim_return_chi2(self, run, instance):
        """Function for returning the array of simulation chi-squared values."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Single instance.
        if self.param_set == 'all' or self.param_set == 'diff':
            return relax_data_store.chi2_sim[self.run]

        # Multiple instances.
        else:
            return relax_data_store.res[self.run][instance].chi2_sim


    def sim_return_param(self, run, instance, index):
        """Function for returning the array of simulation parameter values."""

        # Arguments.
        self.run = run

        # Parameter increment counter.
        inc = 0

        # Get the parameter object names.
        param_names = self.data_names(set='params')


        # Diffusion tensor parameters.
        ##############################

        if self.param_set == 'diff' or self.param_set == 'all':
            # Spherical diffusion.
            if relax_data_store.diff[self.run].type == 'sphere':
                # Return the parameter array.
                if index == 0:
                    return relax_data_store.diff[self.run].tm_sim

                # Increment.
                inc = inc + 1

            # Spheroidal diffusion.
            elif relax_data_store.diff[self.run].type == 'spheroid':
                # Return the parameter array.
                if index == 0:
                    return relax_data_store.diff[self.run].tm_sim
                elif index == 1:
                    return relax_data_store.diff[self.run].Da_sim
                elif index == 2:
                    return relax_data_store.diff[self.run].theta_sim
                elif index == 3:
                    return relax_data_store.diff[self.run].phi_sim

                # Increment.
                inc = inc + 4

            # Ellipsoidal diffusion.
            elif relax_data_store.diff[self.run].type == 'ellipsoid':
                # Return the parameter array.
                if index == 0:
                    return relax_data_store.diff[self.run].tm_sim
                elif index == 1:
                    return relax_data_store.diff[self.run].Da_sim
                elif index == 2:
                    return relax_data_store.diff[self.run].Dr_sim
                elif index == 3:
                    return relax_data_store.diff[self.run].alpha_sim
                elif index == 4:
                    return relax_data_store.diff[self.run].beta_sim
                elif index == 5:
                    return relax_data_store.diff[self.run].gamma_sim

                # Increment.
                inc = inc + 6


        # Model-free parameters for the parameter set 'all'.
        ####################################################

        if self.param_set == 'all':
            # Loop over the sequence.
            for i in xrange(len(relax_data_store.res[self.run])):
                # Skip unselected residues.
                if not relax_data_store.res[self.run][i].select:
                    continue

                # Loop over the residue specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        return getattr(relax_data_store.res[self.run][i], param + "_sim")

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the parameter sets 'mf' and 'local_tm'.
        ###################################################################

        if self.param_set == 'mf' or self.param_set == 'local_tm':
            # Skip unselected residues.
            if not relax_data_store.res[self.run][instance].select:
                return

            # Loop over the residue specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    return getattr(relax_data_store.res[self.run][instance], param + "_sim")

                # Increment.
                inc = inc + 1


    def sim_return_selected(self, run, instance):
        """Function for returning the array of selected simulation flags."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Single instance.
        if self.param_set == 'all' or self.param_set == 'diff':
            return relax_data_store.select_sim[self.run]

        # Multiple instances.
        else:
            return relax_data_store.res[self.run][instance].select_sim


    def skip_function(self, run=None, instance=None, min_instances=None, num_instances=None):
        """Function for skiping certain data."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # All residues.
        combine = 0
        if min_instances == 1 and min_instances != num_instances:
            combine = 1

        # Sequence specific data.
        if (self.param_set == 'mf' or self.param_set == 'local_tm') and not combine and not relax_data_store.res[self.run][instance].select:
            return 1

        # Don't skip.
        return 0


    def unselect(self, run, i, sim_index=None):
        """Function for unselecting models or simulations."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Simulation unselect.
        if sim_index != None:
            # Single instance.
            if self.param_set == 'mf' or self.param_set == 'local_tm':
                relax_data_store.res[self.run][i].select_sim[sim_index] = 0

            # Multiple instances.
            else:
                relax_data_store.select_sim[self.run][sim_index] = 0

        # Residue unselect.
        else:
            # Single residue.
            if self.param_set == 'mf' or self.param_set == 'local_tm':
                relax_data_store.res[self.run][i].select = 0


    def write_columnar_line(self, file=None, num=None, name=None, select=None, select_sim=None, data_set=None, nucleus=None, model=None, equation=None, params=None, param_set=None, s2=None, s2f=None, s2s=None, local_tm=None, te=None, tf=None, ts=None, rex=None, r=None, csa=None, chi2=None, i=None, f=None, g=None, h=None, warn=None, diff_type=None, diff_params=None, pdb=None, pdb_model=None, pdb_heteronuc=None, pdb_proton=None, xh_vect=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, ri=None, ri_error=None):
        """Function for printing a single line of the columnar formatted results."""

        # Residue number and name.
        file.write("%-4s %-5s " % (num, name))

        # Selected flag.
        if select_sim != None:
            file.write("%-9s " % select_sim)
        else:
            file.write("%-9s " % select)

        # Data set.
        file.write("%-9s " % data_set)

        # Nucleus.
        file.write("%-7s " % nucleus)

        # Model details.
        file.write("%-5s %-9s %-35s " % (model, equation, params))

        # Parameter set.
        file.write("%-10s " % param_set)

        # Parameters.
        file.write("%-25s " % s2)
        file.write("%-25s " % s2f)
        file.write("%-25s " % s2s)
        file.write("%-25s " % local_tm)
        file.write("%-25s " % te)
        file.write("%-25s " % tf)
        file.write("%-25s " % ts)
        file.write("%-25s " % rex)
        file.write("%-25s " % r)
        file.write("%-25s " % csa)

        # Minimisation results.
        file.write("%-25s %-8s %-8s %-8s %-8s %-45s " % (chi2, i, f, g, h, warn))

        # Diffusion parameters.
        file.write("%-10s " % diff_type)
        if diff_params:
            for i in xrange(len(diff_params)):
                file.write("%-25s " % diff_params[i])

        # PDB.
        file.write("%-40s " % pdb)
        file.write("%-10s " % pdb_model)
        file.write("%-15s " % pdb_heteronuc)
        file.write("%-15s " % pdb_proton)

        # XH unit vector.
        file.write("%-70s " % xh_vect)

        # Relaxation data setup.
        if ri_labels:
            file.write("%-40s " % ri_labels)
            file.write("%-25s " % remap_table)
            file.write("%-25s " % frq_labels)
            file.write("%-30s " % frq)

        # Relaxation data.
        if ri:
            for i in xrange(len(ri)):
                if ri[i] == None:
                    file.write("%-25s " % 'None')
                else:
                    file.write("%-25s " % ri[i])

        # Relaxation errors.
        if ri_error:
            for i in xrange(len(ri_error)):
                if ri_error[i] == None:
                    file.write("%-25s " % 'None')
                else:
                    file.write("%-25s " % ri_error[i])

        # End of the line.
        file.write("\n")


    def write_columnar_results(self, file, run):
        """Function for printing the results into a file."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()


        # Header.
        #########

        # Diffusion parameters.
        diff_params = None
        if self.param_set != 'local_tm' and hasattr(relax_data_store, 'diff') and relax_data_store.diff.has_key(self.run):
            # Sphere.
            if relax_data_store.diff[self.run].type == 'sphere':
                diff_params = ['tm_(s)']

            # Spheroid.
            elif relax_data_store.diff[self.run].type == 'spheroid':
                diff_params = ['tm_(s)', 'Da_(1/s)', 'theta_(deg)', 'phi_(deg)']

            # Ellipsoid.
            elif relax_data_store.diff[self.run].type == 'ellipsoid':
                diff_params = ['tm_(s)', 'Da_(1/s)', 'Dr_(1/s)', 'alpha_(deg)', 'beta_(deg)', 'gamma_(deg)']

        # Relaxation data and errors.
        ri = []
        ri_error = []
        if hasattr(relax_data_store, 'num_ri'):
            for i in xrange(relax_data_store.num_ri[self.run]):
                ri.append('Ri_(' + relax_data_store.ri_labels[self.run][i] + "_" + relax_data_store.frq_labels[self.run][relax_data_store.remap_table[self.run][i]] + ")")
                ri_error.append('Ri_error_(' + relax_data_store.ri_labels[self.run][i] + "_" + relax_data_store.frq_labels[self.run][relax_data_store.remap_table[self.run][i]] + ")")

        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', data_set='Data_set', nucleus='Nucleus', model='Model', equation='Equation', params='Params', param_set='Param_set', s2='S2', s2f='S2f', s2s='S2s', local_tm='Local_tm_(' + self.return_units('local_tm') + ')', te='te_(' + self.return_units('te') + ')', tf='tf_(' + self.return_units('tf') + ')', ts='ts_(' + self.return_units('ts') + ')', rex='Rex_(' + replace(self.return_units('rex'), ' ', '_') + ')', r='Bond_length_(' + self.return_units('r') + ')', csa='CSA_(' + self.return_units('csa') + ')', chi2='Chi-squared', i='Iter', f='f_count', g='g_count', h='h_count', warn='Warning', diff_type='Diff_type', diff_params=diff_params, pdb='PDB', pdb_model='PDB_model', pdb_heteronuc='PDB_heteronuc', pdb_proton='PDB_proton', xh_vect='XH_vector', ri_labels='Ri_labels', remap_table='Remap_table', frq_labels='Frq_labels', frq='Frequencies', ri=ri, ri_error=ri_error)


        # Values.
        #########

        # Nucleus.
        nucleus = self.relax.generic.nuclei.find_nucleus()

        # Diffusion parameters.
        diff_type = None
        diff_params = None
        if self.param_set != 'local_tm' and hasattr(relax_data_store, 'diff') and relax_data_store.diff.has_key(self.run):
            # Sphere.
            if relax_data_store.diff[self.run].type == 'sphere':
                diff_type = 'sphere'
                diff_params = [`relax_data_store.diff[self.run].tm`]

            # Spheroid.
            elif relax_data_store.diff[self.run].type == 'spheroid':
                diff_type = relax_data_store.diff[self.run].spheroid_type
                if diff_type == None:
                    diff_type = 'spheroid'
                diff_params = [`relax_data_store.diff[self.run].tm`, `relax_data_store.diff[self.run].Da`, `relax_data_store.diff[self.run].theta * 360 / (2.0 * pi)`, `relax_data_store.diff[self.run].phi * 360 / (2.0 * pi)`]

            # Ellipsoid.
            elif relax_data_store.diff[self.run].type == 'ellipsoid':
                diff_type = 'ellipsoid'
                diff_params = [`relax_data_store.diff[self.run].tm`, `relax_data_store.diff[self.run].Da`, `relax_data_store.diff[self.run].Dr`, `relax_data_store.diff[self.run].alpha * 360 / (2.0 * pi)`, `relax_data_store.diff[self.run].beta * 360 / (2.0 * pi)`, `relax_data_store.diff[self.run].gamma * 360 / (2.0 * pi)`]

        # PDB.
        pdb = None
        pdb_model = None
        if relax_data_store.pdb.has_key(self.run):
            pdb = relax_data_store.pdb[self.run].file_name
            pdb_model = relax_data_store.pdb[self.run].model

        # Relaxation data setup.
        try:
            ri_labels = replace(`relax_data_store.ri_labels[self.run]`, ' ', '')
            remap_table = replace(`relax_data_store.remap_table[self.run]`, ' ', '')
            frq_labels = replace(`relax_data_store.frq_labels[self.run]`, ' ', '')
            frq = replace(`relax_data_store.frq[self.run]`, ' ', '')
        except AttributeError:
            ri_labels = `None`
            remap_table = `None`
            frq_labels = `None`
            frq = `None`

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Reassign data structure.
            data = relax_data_store.res[self.run][i]

            # Model details.
            model = None
            if hasattr(data, 'model'):
                model = data.model

            equation = None
            if hasattr(data, 'equation'):
                equation = data.equation

            params = None
            if hasattr(data, 'params'):
                params = replace(`data.params`, ' ', '')

            # S2.
            s2 = None
            if hasattr(data, 's2') and data.s2 != None:
                s2 = data.s2 / self.return_conversion_factor('s2')
            s2 = `s2`

            # S2f.
            s2f = None
            if hasattr(data, 's2f') and data.s2f != None:
                s2f = data.s2f / self.return_conversion_factor('s2f')
            s2f = `s2f`

            # S2s.
            s2s = None
            if hasattr(data, 's2s') and data.s2s != None:
                s2s = data.s2s / self.return_conversion_factor('s2s')
            s2s = `s2s`

            # Local tm.
            local_tm = None
            if hasattr(data, 'local_tm') and data.local_tm != None:
                local_tm = data.local_tm / self.return_conversion_factor('local_tm')
            local_tm = `local_tm`

            # te.
            te = None
            if hasattr(data, 'te') and data.te != None:
                te = data.te / self.return_conversion_factor('te')
            te = `te`

            # tf.
            tf = None
            if hasattr(data, 'tf') and data.tf != None:
                tf = data.tf / self.return_conversion_factor('tf')
            tf = `tf`

            # ts.
            ts = None
            if hasattr(data, 'ts') and data.ts != None:
                ts = data.ts / self.return_conversion_factor('ts')
            ts = `ts`

            # Rex.
            rex = None
            if hasattr(data, 'rex') and data.rex != None:
                rex = data.rex / self.return_conversion_factor('rex')
            rex = `rex`

            # Bond length.
            r = None
            if hasattr(data, 'r') and data.r != None:
                r = data.r / self.return_conversion_factor('r')
            r = `r`

            # CSA.
            csa = None
            if hasattr(data, 'csa') and data.csa != None:
                csa = data.csa / self.return_conversion_factor('csa')
            csa = `csa`

            # Minimisation details.
            try:
                # Global minimisation results.
                if self.param_set == 'diff' or self.param_set == 'all':
                    chi2 = `relax_data_store.chi2[self.run]`
                    iter = relax_data_store.iter[self.run]
                    f = relax_data_store.f_count[self.run]
                    g = relax_data_store.g_count[self.run]
                    h = relax_data_store.h_count[self.run]
                    if type(relax_data_store.warning[self.run]) == str:
                        warn = replace(relax_data_store.warning[self.run], ' ', '_')
                    else:
                        warn = relax_data_store.warning[self.run]

                # Individual residue results.
                else:
                    chi2 = `data.chi2`
                    iter = data.iter
                    f = data.f_count
                    g = data.g_count
                    h = data.h_count
                    if type(data.warning) == str:
                        warn = replace(data.warning, ' ', '_')
                    else:
                        warn = data.warning

            # No minimisation details.
            except:
                chi2 = None
                iter = None
                f = None
                g = None
                h = None
                warn = None

            # XH vector.
            xh_vect = None
            if hasattr(data, 'xh_vect'):
                xh_vect = replace(`data.xh_vect.tolist()`, ' ', '')

            # Heteronucleus and proton names.
            heteronuc = None
            proton = None
            if hasattr(data, 'heteronuc'):
                heteronuc = data.heteronuc
                proton = data.proton

            # Relaxation data and errors.
            ri = []
            ri_error = []
            if hasattr(relax_data_store, 'num_ri'):
                for i in xrange(relax_data_store.num_ri[self.run]):
                    try:
                        # Find the residue specific data corresponding to i.
                        index = None
                        for j in xrange(data.num_ri):
                            if data.ri_labels[j] == relax_data_store.ri_labels[self.run][i] and data.frq_labels[data.remap_table[j]] == relax_data_store.frq_labels[self.run][relax_data_store.remap_table[self.run][i]]:
                                index = j

                        # Data exists for this data type.
                        ri.append(`data.relax_data[index]`)
                        ri_error.append(`data.relax_error[index]`)

                    # No data exists for this data type.
                    except:
                        ri.append(None)
                        ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='value', nucleus=nucleus, model=model, equation=equation, params=params, param_set=self.param_set, s2=s2, s2f=s2f, s2s=s2s, local_tm=local_tm, te=te, tf=tf, ts=ts, rex=rex, r=r, csa=csa, chi2=chi2, i=iter, f=f, g=g, h=h, warn=warn, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, pdb_heteronuc=heteronuc, pdb_proton=proton, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Errors.
        #########

        # Only invoke this section if errors exist.
        if self.has_errors():
            # Diffusion parameters.
            diff_params = None
            if self.param_set != 'local_tm' and hasattr(relax_data_store, 'diff') and relax_data_store.diff.has_key(self.run):
                # Sphere.
                if relax_data_store.diff[self.run].type == 'sphere':
                    diff_params = [None]

                # Spheroid.
                elif relax_data_store.diff[self.run].type == 'spheroid':
                    diff_params = [None, None, None, None]

                # Ellipsoid.
                elif relax_data_store.diff[self.run].type == 'ellipsoid':
                    diff_params = [None, None, None, None, None, None]

                # Diffusion parameter errors.
                if self.param_set == 'diff' or self.param_set == 'all':
                    # Sphere.
                    if relax_data_store.diff[self.run].type == 'sphere' and hasattr(relax_data_store.diff[self.run], 'tm_err'):
                        diff_params = [`relax_data_store.diff[self.run].tm_err`]

                    # Spheroid.
                    elif relax_data_store.diff[self.run].type == 'spheroid' and hasattr(relax_data_store.diff[self.run], 'tm_err'):
                        diff_params = [`relax_data_store.diff[self.run].tm_err`, `relax_data_store.diff[self.run].Da_err`, `relax_data_store.diff[self.run].theta_err * 360 / (2.0 * pi)`, `relax_data_store.diff[self.run].phi_err * 360 / (2.0 * pi)`]

                    # Ellipsoid.
                    elif relax_data_store.diff[self.run].type == 'ellipsoid' and hasattr(relax_data_store.diff[self.run], 'tm_err'):
                        diff_params = [`relax_data_store.diff[self.run].tm_err`, `relax_data_store.diff[self.run].Da_err`, `relax_data_store.diff[self.run].Dr_err`, `relax_data_store.diff[self.run].alpha_err * 360 / (2.0 * pi)`, `relax_data_store.diff[self.run].beta_err * 360 / (2.0 * pi)`, `relax_data_store.diff[self.run].gamma_err * 360 / (2.0 * pi)`]

            # Loop over the sequence.
            for i in xrange(len(relax_data_store.res[self.run])):
                # Reassign data structure.
                data = relax_data_store.res[self.run][i]

                # Model details.
                model = None
                if hasattr(data, 'model'):
                    model = data.model

                equation = None
                if hasattr(data, 'equation'):
                    equation = data.equation

                params = None
                if hasattr(data, 'params'):
                    params = replace(`data.params`, ' ', '')

                # S2.
                s2 = None
                if hasattr(data, 's2_err') and data.s2_err != None:
                    s2 = data.s2_err / self.return_conversion_factor('s2')
                s2 = `s2`

                # S2f.
                s2f = None
                if hasattr(data, 's2f_err') and data.s2f_err != None:
                    s2f = data.s2f_err / self.return_conversion_factor('s2f')
                s2f = `s2f`

                # S2s.
                s2s = None
                if hasattr(data, 's2s_err') and data.s2s_err != None:
                    s2s = data.s2s_err / self.return_conversion_factor('s2s')
                s2s = `s2s`

                # Local tm.
                local_tm = None
                if hasattr(data, 'local_tm_err') and data.local_tm_err != None:
                    local_tm = data.local_tm_err / self.return_conversion_factor('local_tm')
                local_tm = `local_tm`

                # te.
                te = None
                if hasattr(data, 'te_err') and data.te_err != None:
                    te = data.te_err / self.return_conversion_factor('te')
                te = `te`

                # tf.
                tf = None
                if hasattr(data, 'tf_err') and data.tf_err != None:
                    tf = data.tf_err / self.return_conversion_factor('tf')
                tf = `tf`

                # ts.
                ts = None
                if hasattr(data, 'ts_err') and data.ts_err != None:
                    ts = data.ts_err / self.return_conversion_factor('ts')
                ts = `ts`

                # Rex.
                rex = None
                if hasattr(data, 'rex_err') and data.rex_err != None:
                    rex = data.rex_err / self.return_conversion_factor('rex')
                rex = `rex`

                # Bond length.
                r = None
                if hasattr(data, 'r_err') and data.r_err != None:
                    r = data.r_err / self.return_conversion_factor('r')
                r = `r`

                # CSA.
                csa = None
                if hasattr(data, 'csa_err') and data.csa_err != None:
                    csa = data.csa_err / self.return_conversion_factor('csa')
                csa = `csa`

                # Relaxation data and errors.
                ri = []
                ri_error = []
                for i in xrange(relax_data_store.num_ri[self.run]):
                    ri.append(None)
                    ri_error.append(None)

                # XH vector.
                xh_vect = None
                if hasattr(data, 'xh_vect'):
                    xh_vect = replace(`data.xh_vect.tolist()`, ' ', '')

                # Write the line.
                self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='error', nucleus=nucleus, model=model, equation=equation, params=params, param_set=self.param_set, s2=s2, s2f=s2f, s2s=s2s, local_tm=local_tm, te=te, tf=tf, ts=ts, rex=rex, r=r, csa=csa, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, pdb_heteronuc=heteronuc, pdb_proton=proton, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Simulation values.
        ####################

        # Only invoke this section if simulations have been setup.
        if hasattr(relax_data_store, 'sim_state') and relax_data_store.sim_state[self.run]:
            # Loop over the simulations.
            for i in xrange(relax_data_store.sim_number[self.run]):
                # Diffusion parameters.
                diff_params = None
                if self.param_set != 'local_tm' and hasattr(relax_data_store, 'diff') and relax_data_store.diff.has_key(self.run):
                    # Diffusion parameter simulation values.
                    if self.param_set == 'diff' or self.param_set == 'all':
                        # Sphere.
                        if relax_data_store.diff[self.run].type == 'sphere':
                            diff_params = [`relax_data_store.diff[self.run].tm_sim[i]`]

                        # Spheroid.
                        elif relax_data_store.diff[self.run].type == 'spheroid':
                            diff_params = [`relax_data_store.diff[self.run].tm_sim[i]`, `relax_data_store.diff[self.run].Da_sim[i]`, `relax_data_store.diff[self.run].theta_sim[i] * 360 / (2.0 * pi)`, `relax_data_store.diff[self.run].phi_sim[i] * 360 / (2.0 * pi)`]

                        # Ellipsoid.
                        elif relax_data_store.diff[self.run].type == 'ellipsoid':
                            diff_params = [`relax_data_store.diff[self.run].tm_sim[i]`, `relax_data_store.diff[self.run].Da_sim[i]`, `relax_data_store.diff[self.run].Dr_sim[i]`, `relax_data_store.diff[self.run].alpha_sim[i] * 360 / (2.0 * pi)`, `relax_data_store.diff[self.run].beta_sim[i] * 360 / (2.0 * pi)`, `relax_data_store.diff[self.run].gamma_sim[i] * 360 / (2.0 * pi)`]

                    # No simulation values.
                    else:
                        # Sphere.
                        if relax_data_store.diff[self.run].type == 'sphere':
                            diff_params = [None]

                        # Spheroid.
                        elif relax_data_store.diff[self.run].type == 'spheroid':
                            diff_params = [None, None, None, None]

                        # Ellipsoid.
                        elif relax_data_store.diff[self.run].type == 'ellipsoid':
                            diff_params = [None, None, None, None, None, None]

                # Loop over the sequence.
                for j in xrange(len(relax_data_store.res[self.run])):
                    # Reassign data structure.
                    data = relax_data_store.res[self.run][j]

                    # Model details.
                    model = None
                    if hasattr(data, 'model'):
                        model = data.model

                    equation = None
                    if hasattr(data, 'equation'):
                        equation = data.equation

                    params = None
                    if hasattr(data, 'params'):
                        params = replace(`data.params`, ' ', '')

                    # Selected simulation.
                    if self.param_set == 'diff' or self.param_set == 'all':
                        select_sim = relax_data_store.select_sim[self.run][i]
                    else:
                        select_sim = data.select_sim[i]

                    # S2.
                    s2 = None
                    if hasattr(data, 's2_sim') and data.s2_sim[i] != None:
                        s2 = data.s2_sim[i] / self.return_conversion_factor('s2')
                    s2 = `s2`

                    # S2f.
                    s2f = None
                    if hasattr(data, 's2f_sim') and data.s2f_sim[i] != None:
                        s2f = data.s2f_sim[i] / self.return_conversion_factor('s2f')
                    s2f = `s2f`

                    # S2s.
                    s2s = None
                    if hasattr(data, 's2s_sim') and data.s2s_sim[i] != None:
                        s2s = data.s2s_sim[i] / self.return_conversion_factor('s2s')
                    s2s = `s2s`

                    # Local tm.
                    local_tm = None
                    if hasattr(data, 'local_tm_sim') and data.local_tm_sim[i] != None:
                        local_tm = data.local_tm_sim[i] / self.return_conversion_factor('local_tm')
                    local_tm = `local_tm`

                    # te.
                    te = None
                    if hasattr(data, 'te_sim') and data.te_sim[i] != None:
                        te = data.te_sim[i] / self.return_conversion_factor('te')
                    te = `te`

                    # tf.
                    tf = None
                    if hasattr(data, 'tf_sim') and data.tf_sim[i] != None:
                        tf = data.tf_sim[i] / self.return_conversion_factor('tf')
                    tf = `tf`

                    # ts.
                    ts = None
                    if hasattr(data, 'ts_sim') and data.ts_sim[i] != None:
                        ts = data.ts_sim[i] / self.return_conversion_factor('ts')
                    ts = `ts`

                    # Rex.
                    rex = None
                    if hasattr(data, 'rex_sim') and data.rex_sim[i] != None:
                        rex = data.rex_sim[i] / self.return_conversion_factor('rex')
                    rex = `rex`

                    # Bond length.
                    r = None
                    if hasattr(data, 'r_sim') and data.r_sim[i] != None:
                        r = data.r_sim[i] / self.return_conversion_factor('r')
                    r = `r`

                    # CSA.
                    csa = None
                    if hasattr(data, 'csa_sim') and data.csa_sim[i] != None:
                        csa = data.csa_sim[i] / self.return_conversion_factor('csa')
                    csa = `csa`

                    # Minimisation details.
                    try:
                        # Global minimisation results.
                        if self.param_set == 'diff' or self.param_set == 'all':
                            chi2 = `relax_data_store.chi2_sim[self.run][i]`
                            iter = relax_data_store.iter_sim[self.run][i]
                            f = relax_data_store.f_count_sim[self.run][i]
                            g = relax_data_store.g_count_sim[self.run][i]
                            h = relax_data_store.h_count_sim[self.run][i]
                            if type(relax_data_store.warning_sim[self.run][i]) == str:
                                warn = replace(relax_data_store.warning_sim[self.run][i], ' ', '_')
                            else:
                                warn = relax_data_store.warning_sim[self.run][i]

                        # Individual residue results.
                        else:
                            chi2 = `data.chi2_sim[i]`
                            iter = data.iter_sim[i]
                            f = data.f_count_sim[i]
                            g = data.g_count_sim[i]
                            h = data.h_count_sim[i]
                            if type(data.warning_sim[i]) == str:
                                warn = replace(data.warning_sim[i], ' ', '_')
                            else:
                                warn = data.warning_sim[i]

                    # No minimisation details.
                    except AttributeError:
                        chi2 = None
                        iter = None
                        f = None
                        g = None
                        h = None
                        warn = None

                    # Relaxation data and errors.
                    ri = []
                    ri_error = []
                    if hasattr(relax_data_store, 'num_ri'):
                        for k in xrange(relax_data_store.num_ri[self.run]):
                            try:
                                # Find the residue specific data corresponding to k.
                                index = None
                                for l in xrange(data.num_ri):
                                    if data.ri_labels[l] == relax_data_store.ri_labels[self.run][k] and data.frq_labels[data.remap_table[l]] == relax_data_store.frq_labels[self.run][relax_data_store.remap_table[self.run][k]]:
                                        index = l

                                # Data exists for this data type.
                                ri.append(`data.relax_sim_data[i][index]`)
                                ri_error.append(`data.relax_error[index]`)

                            # No data exists for this data type.
                            except:
                                ri.append(None)
                                ri_error.append(None)

                    # XH vector.
                    xh_vect = None
                    if hasattr(data, 'xh_vect'):
                        xh_vect = replace(`data.xh_vect.tolist()`, ' ', '')

                    # Write the line.
                    self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, select_sim=select_sim, data_set='sim_'+`i`, nucleus=nucleus, model=model, equation=equation, params=params, param_set=self.param_set, s2=s2, s2f=s2f, s2s=s2s, local_tm=local_tm, te=te, tf=tf, ts=ts, rex=rex, r=r, csa=csa, chi2=chi2, i=iter, f=f, g=g, h=h, warn=warn, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, pdb_heteronuc=heteronuc, pdb_proton=proton, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)
