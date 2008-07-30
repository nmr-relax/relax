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
from data import Relax_data_store; ds = Relax_data_store()
from float import isNaN,isInf
from generic_fns import diffusion_tensor, pipes, relax_data, sequence
from generic_fns.mol_res_spin import convert_from_global_index, count_spins, exists_mol_res_spin_data, return_spin, return_spin_from_index, spin_loop
from maths_fns.mf import Mf
from minfx.generic import generic_minimise
from physical_constants import N15_CSA, NH_BOND_LENGTH
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxInfError, RelaxInvalidDataError, RelaxLenError, RelaxNaNError, RelaxNoModelError, RelaxNoPdbError, RelaxNoResError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoSpinSpecError, RelaxNoTensorError, RelaxNoValueError, RelaxNoVectorsError, RelaxNucleusError, RelaxTensorError
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

        # Deselected residue.
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
        cdp = ds[ds.current_pipe]

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
                # Skip deselected residues.
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
        @keyword model_type:    The optional model type, one of 'all', 'diff', 'mf', or 'local_tm'.
        @type model_type:       str or None
        @return:                An array of the parameter values of the model-free model.
        @rtype:                 numpy array
        """

        # Initialise.
        param_vector = []

        # Determine the model type.
        if not model_type:
            model_type = self.determine_model_type()

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

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
                # Skip deselected residues.
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


    def assemble_scaling_matrix(self, num_params, model_type=None, spin=None, spin_id=None, scaling=True):
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

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

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
        if not hasattr(ds.res[self.run][i], 'model') or not ds.res[self.run][i].model:
            raise RelaxNoModelError, self.run

        # Loop over the relaxation data.
        for j in xrange(len(ds.res[run][i].relax_data)):
            # Back calculate the value.
            value = self.back_calc(run=run, index=i, ri_label=ds.res[run][i].ri_labels[j], frq_label=ds.res[run][i].frq_labels[ds.res[run][i].remap_table[j]], frq=ds.res[run][i].frq[ds.res[run][i].remap_table[j]])

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
        if not ds.current_pipe:
            raise RelaxNoPipeError

        # Test if the pipe type is 'mf'.
        function_type = ds[ds.current_pipe].pipe_type
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
        relax_data_names = relax_data.get_data_names()

        # Loop over the data structure names.
        relax_data_init = False
        for name in data_names:
            # Relaxation data structures.
            if name in relax_data_names and not relax_data_init:
                relax_data.data_init(spin)
                relax_data_init = True

            # Data structures which are initially empty arrays.
            list_data = [ 'params' ]
            if name in list_data:
                init_data = []

            # Set everything else initially to None.
            init_data = None

            # If the name is not in 'spin', add it.
            if not hasattr(spin, name):
                setattr(spin, name, init_data)


    def data_names(self, set='all', error_names=False, sim_names=False):
        """Return a list of all spin container specific model-free object names.

        Description
        ===========

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


        @keyword set:           The set of object names to return.  This can be set to 'all' for all
                                names, to 'generic' for generic object names, 'params' for
                                model-free parameter names, or to 'min' for minimisation specific
                                object names.
        @type set:              str
        @keyword error_names:   A flag which if True will add the error object names as well.
        @type error_names:      bool
        @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object
                                names as well.
        @type sim_names:        bool
        @return:                The list of object names.
        @rtype:                 list of str
        """

        # Initialise.
        names = []

        # Generic.
        if set == 'all' or set == 'generic':
            names.append('select')
            names.append('fixed')
            names.append('proton_type')
            names.append('heteronuc_type')
            names.append('attached_proton')
            names.append('nucleus')
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

        # Minimisation statistics.
        if set == 'all' or set == 'min':
            names.append('chi2')
            names.append('iter')
            names.append('f_count')
            names.append('g_count')
            names.append('h_count')
            names.append('warning')

        # Structural data.
        names.append('xh_vect')

        # Relaxation data.
        if set == 'all':
            names = names + relax_data.get_data_names()

        # Parameter errors.
        if error_names and (set == 'all' or set == 'params'):
            names.append('s2_err')
            names.append('s2f_err')
            names.append('s2s_err')
            names.append('local_tm_err')
            names.append('te_err')
            names.append('tf_err')
            names.append('ts_err')
            names.append('rex_err')
            names.append('r_err')
            names.append('csa_err')

        # Parameter simulation values.
        if sim_names and (set == 'all' or set == 'params'):
            names.append('s2_sim')
            names.append('s2f_sim')
            names.append('s2s_sim')
            names.append('local_tm_sim')
            names.append('te_sim')
            names.append('tf_sim')
            names.append('ts_sim')
            names.append('rex_sim')
            names.append('r_sim')
            names.append('csa_sim')

        # Relaxation data simulation values.
        if sim_names and set == 'all':
            names = names + relax_data.get_data_names(sim_names=True)

        # Return the names.
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

        # Test if the current pipe exists.
        if not ds.current_pipe:
            raise RelaxNoPipeError

        # Test if the pipe type is set to 'mf'.
        function_type = ds[ds.current_pipe].pipe_type
        if function_type != 'mf':
            raise RelaxFuncSetupError, specific_fns.setup.get_string(function_type)

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Get all data structure names.
        names = self.data_names()

        # Loop over the sequence.
        for i in xrange(len(ds.res[self.run])):
            # Remap the data structure 'ds.res[self.run][i]'.
            data = ds.res[self.run][i]

            # Loop through the data structure names.
            for name in names:
                # Skip the data structure if it does not exist.
                if not hasattr(data, name):
                    continue

                # Delete the data.
                delattr(data, name)

        # Clean up the runs.
        self.relax.generic.runs.eliminate_unused_runs()


    def determine_model_type(self):
        """Determine the global model type.

        @return:    The name of the model type, which will be one of 'all', 'diff', 'mf', or
                    'local_tm'.
        @rtype:     str
        """

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # If there is a local tm, fail if not all residues have a local tm parameter.
        local_tm = 0
        for spin in spin_loop():
            # Skip deselected residues.
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
            # Skip deselected residues.
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

        # 'diff' model type.
        if mf_all_fixed:
            # All parameters fixed!
            if cdp.diff_tensor.fixed:
                raise RelaxError, "All parameters are fixed."

            return 'diff'

        # 'mf' model type.
        if cdp.diff_tensor.fixed:
            return 'mf'

        # 'all' model type.
        else:
            return 'all'


    def duplicate_data(self, pipe_from=None, pipe_to=None, model_index=None, global_stats=False):
        """Duplicate the data specific to a single model-free model.

        @keyword pipe_from:     The data pipe to copy the data from.
        @type pipe_from:        str
        @keyword pipe_to:       The data pipe to copy the data to.
        @type pipe_to:          str
        @keyword model_index:   The index of the model to determine which spin system to duplicate
                                data from.
        @type model_index:      int
        @keyword global_stats:  The global statistics flag
        @type global_stats:     bool
        """

        # First create the pipe_to data pipe, if it doesn't exist (restoring the current pipe at the end).
        current_pipe = ds.current_pipe
        if not ds.has_key(pipe_to):
            pipes.create(pipe_to, pipe_type='mf')
        ds.current_pipe = current_pipe

        # Duplicate all non-sequence specific data.
        for data_name in dir(ds[pipe_from]):
            # Skip the container objects.
            if data_name in ['mol', 'diff_tensor']:
                continue

            # Skip special objects.
            if search('^_', data_name) or data_name in ds[pipe_from].__class__.__dict__.keys():
                continue

            # Get the original object.
            data_from = getattr(ds[pipe_from], data_name)

            # The data already exists.
            if hasattr(ds[pipe_to], data_name):
                # Get the object in the target pipe.
                data_to = getattr(ds[pipe_to], data_name)

                # The data must match!
                if data_from != data_to:
                    raise RelaxError, "The object " + `data_name` + " is not consistent between the pipes " + `pipe_from` + " and " + `pipe_to` + "."

                # Skip the data.
                continue

            # Duplicate the data.
            setattr(ds[pipe_to], data_name, deepcopy(data_from))

        # Diffusion tensor comparison.
        if hasattr(ds[pipe_from], 'diff_tensor'):
            # Duplicate the tensor if it doesn't exist.
            if not hasattr(ds[pipe_to], 'diff_tensor'):
                setattr(ds[pipe_to], 'diff_tensor', deepcopy(ds[pipe_from].diff_tensor))

            # Otherwise compare the objects inside the container.
            else:
                # Loop over the modifiable objects.
                for data_name in ds[pipe_from].diff_tensor.__mod_attr__:
                    # Get the original object.
                    data_from = None
                    if hasattr(ds[pipe_from].diff_tensor, data_name):
                        data_from = getattr(ds[pipe_from].diff_tensor, data_name)

                    # Get the target object.
                    if data_from and not hasattr(ds[pipe_to].diff_tensor, data_name):
                        raise RelaxError, "The diffusion tensor object " + `data_name` + " of the " + `pipe_from` + " data pipe is not located in the " + `pipe_to` + " data pipe."
                    elif data_from:
                        data_to = getattr(ds[pipe_to].diff_tensor, data_name)
                    else:
                        continue

                    # The data must match!
                    if data_from != data_to:
                        raise RelaxError, "The object " + `data_name` + "." + `data_name` + " is not consistent between the pipes " + `pipe_from` + " and " + `pipe_to` + "."

        # Determine the model type.
        model_type = self.determine_model_type()

        # Sequence specific data.
        if model_type == 'mf' or (model_type == 'local_tm' and not global_stats):
            # Duplicate the sequence data if it doesn't exist.
            if ds[pipe_to].mol.is_empty():
                sequence.copy(pipe_from=pipe_from, pipe_to=pipe_to)

            # Get the spin container indices.
            mol_index, res_index, spin_index = convert_from_global_index(global_index=model_index, pipe=pipe_from)

            # Duplicate the spin specific data.
            ds[pipe_to].mol[mol_index].res[res_index].spin[spin_index] = deepcopy(ds[pipe_from].mol[mol_index].res[res_index].spin[spin_index])

        # Other data types.
        else:
            # Duplicate all the spin specific data.
            ds[pipe_to].mol = deepcopy(ds[pipe_from].mol)


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
        if model_type == 'local_tm':
            tm = ds.res[run][i].local_tm
        else:
            tm = ds.diff[run].tm

        # Local tm.
        if name == 'local_tm' and value >= c1:
            print "The local tm parameter of " + `value` + " is greater than " + `c1` + ", eliminating spin system " + `ds.res[run][i].num` + " " + ds.res[run][i].name + " of the run " + `run`
            return 1

        # Internal correlation times.
        if match('t[efs]', name) and value >= c2 * tm:
            print "The " + name + " value of " + `value` + " is greater than " + `c2 * tm` + ", eliminating spin system " + `ds.res[run][i].num` + " " + ds.res[run][i].name + " of the run " + `run`
            return 1

        # Accept model.
        return 0


    def get_param_names(self, model_index=None):
        """Return a vector of parameter names.

        @keyword model_index:   The model index.  This is zero for the global models or equal to the
                                global spin index (which covers the molecule, residue, and spin
                                indices).
        @type model_index:      int
        @return:                The vector of parameter names.
        @rtype:                 list of str
        """

        # Determine the model type.
        model_type = self.determine_model_type()

        # Get the spin ids.
        if model_type == 'mf' or model_type == 'local_tm':
            # Get the spin and it's id string.
            spin, spin_id = return_spin_from_index(model_index, return_spin_id=True)
        else:
            spin_id = None

        # Assemble and return the parameter names.
        return self.assemble_param_names(model_type, spin_id=spin_id)


    def get_param_values(self, model_index=None, sim_index=None):
        """Return a vector of parameter values.

        @keyword model_index:   The model index.  This is zero for the global models or equal to the
                                global spin index (which covers the molecule, residue, and spin
                                indices).
        @type model_index:      int
        @keyword sim_index:     The Monte Carlo simulation index.
        @type sim_index:        int
        @return:                The vector of parameter values.
        @rtype:                 list of str
        """

        # Test if the model-free models have been set up.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Not setup.
            if not spin.model:
                raise RelaxNoModelError

        # Determine the model type.
        model_type = self.determine_model_type()

        # Set the spin container (to None if the model is global).
        if model_type == 'mf' or model_type == 'local_tm':
            spin = return_spin_from_index(model_index)
        else:
            spin = None

        # Assemble the parameter values and return them.
        return self.assemble_param_vector(spin=spin, sim_index=sim_index, model_type=model_type)


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


    def linear_constraints(self, num_params, model_type=None, spin=None, spin_id=None, scaling_matrix=None):
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

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

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
        for param in params:
            if param == 'local_tm' and hasattr(ds, 'diff_tensor'):
                raise RelaxTensorError, 'diffusion'

        # Loop over the sequence.
        for spin in spin_loop(spin_id):
            # Initialise the data structures (if needed).
            self.data_init(spin)

            # Model-free model, equation, and parameter types.
            spin.model = model
            spin.equation = equation
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

        # Determine the model type.
        model_type = self.determine_model_type()

        # Statistics for a single residue.
        if not global_stats:
            # Get the SpinContainer.
            if spin_id:
                spin = return_spin(spin_id)
            else:
                spin = return_spin_from_index(instance)

            # Skip deselected residues.
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
                # Skip deselected residues.
                if not spin.select:
                    continue

                # Skip residues with no relaxation data.
                if not hasattr(spin, 'relax_data') or not len(spin.relax_data):
                    continue

                n = n + len(spin.relax_data)

                # Local tm models.
                if model_type == 'local_tm':
                    chi2 = chi2 + spin.chi2

            # The chi2 value.
            if model_type != 'local_tm':
                chi2 = ds[ds.current_pipe].chi2

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

        # Determine the model type.
        model_type = self.determine_model_type()

        # Sequence specific data.
        if model_type == 'mf' or model_type == 'local_tm':
            return count_spins()

        # Other data.
        elif model_type == 'diff' or model_type == 'all':
            return 1

        # Should not be here.
        else:
            raise RelaxFault


    def overfit_deselect(self):
        """Deselect spins which have insufficient data to support minimisation."""

        # Test if sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Alias the current data pipe.
        cdp = ds[ds.current_pipe]

        # Is structural data required?
        need_vect = False
        if hasattr(cdp, 'diff_tensor') and (cdp.diff_tensor.type == 'spheroid' or cdp.diff_tensor.type == 'ellipsoid'):
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
            elif hasattr(spin, 'params') and spin.params and len(spin.params) > len(spin.relax_data):
                spin.select = False

            # Test for structural data if required.
            elif need_vect and not hasattr(spin, 'xh_vect'):
                spin.select = False


    def remove_tm(self, spin_id=None):
        """Remove local tm from the set of model-free parameters for the given spins.

        @param spin_id: The spin identification string.
        @type spin_id:  str or None
        """

        # Test if the current data pipe exists.
        if not ds.current_pipe:
            raise RelaxNoPipeError

        # Test if the pipe type is 'mf'.
        function_type = ds[ds.current_pipe].pipe_type
        if function_type != 'mf':
            raise RelaxFuncSetupError, specific_fns.get_string(function_type)

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over the spins.
        for spin in spin_loop(spin_id):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Test if a local tm parameter exists.
            if not hasattr(spin, 'params') or not 'local_tm' in spin.params:
                continue

            # Remove tm.
            spin.params.remove('local_tm')

            # Model name.
            if match('^tm', spin.model):
                spin.model = spin.model[1:]

            # Delete the local tm variable.
            del spin.local_tm

            # Set all the minimisation stats to None.
            spin.chi2 = None
            spin.iter = None
            spin.f_count = None
            spin.g_count = None
            spin.h_count = None
            spin.warning = None

        # Set the global minimisation stats to None.
        ds[ds.current_pipe].chi2 = None
        ds[ds.current_pipe].iter = None
        ds[ds.current_pipe].f_count = None
        ds[ds.current_pipe].g_count = None
        ds[ds.current_pipe].h_count = None
        ds[ds.current_pipe].warning = None


    def return_conversion_factor(self, param, spin=None, spin_id=None):
        """Return the factor of conversion between different parameter units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return 1e-12 for te.


        @param param:   The name of the parameter to return the conversion factor for.
        @type param:    str
        @param spin:    The spin container.
        @type spin:     SpinContainer instance
        @param spin_id: The spin identification string (ignored if the spin container is supplied).
        @type spin_id:  str
        @return:        The conversion factor.
        @rtype:         float
        """

        # Get the object name.
        object_name = self.return_data_name(param)

        # Test for objects needing the spin container.
        if object_name in ['rex']:
            # The spin must be specified to get frequency to scale the Rex value by.
            if spin == None and spin_id == None:
                raise RelaxNoSpinSpecError

            # Get the spin.
            if not spin:
                spin = return_spin(spin_id)

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


    def return_data_desc(self, name, spin=None):
        """Return a description of the spin specific object.

        @param name:    The name of the spin specific object.
        @type name:     str
        @param spin:    The spin container.
        @type spin:     SpinContainer instance
        @return:        The object description, or None.
        @rtype:         str or None
        """

        # Model-free specific objects.
        if name == 'select':
            return 'The spin selection flag'
        if name == 'fixed':
            return 'The fixed flag'
        if name == 'proton_type':
            return 'The proton spin type'
        if name == 'heteronuc_type':
            return 'The heteronucleus spin type'
        if name == 'attached_proton':
            return None
        if name == 'nucleus':
            return None
        if name == 'model':
            return 'The model'
        if name == 'equation':
            return 'The model equation'
        if name == 'params':
            return 'The model parameters'
        if name == 's2':
            return 'S2, the model-free generalised order parameter (S2 = S2f.S2s)'
        if name == 's2f':
            return 'S2f, the faster motion model-free generalised order parameter'
        if name == 's2s':
            return 'S2s, the slower motion model-free generalised order parameter'
        if name == 'local_tm':
            return 'The spin specific global correlation time (' + self.return_units('local_tm') + ')'
        if name == 'te':
            return 'Single motion effective internal correlation time (' + self.return_units('te') + ')'
        if name == 'tf':
            return 'Faster motion effective internal correlation time (' + self.return_units('tf') + ')'
        if name == 'ts':
            return 'Slower motion effective internal correlation time (' + self.return_units('ts') + ')'
        if name == 'rex':
            rex_units = self.return_units('rex', spin=spin)
            if rex_units:
                return 'Chemical exchange relaxation (' + rex_units + ')'
            else:
                return 'Chemical exchange relaxation'
        if name == 'r':
            return 'Bond length (' + self.return_units('r') + ')'
        if name == 'csa':
            return 'Chemical shift anisotropy (' + self.return_units('csa') + ')'
        if name == 'chi2':
            return 'Chi-squared value'
        if name == 'iter':
            return 'Optimisation iterations'
        if name == 'f_count':
            return 'Number of function calls'
        if name == 'g_count':
            return 'Number of gradient calls'
        if name == 'h_count':
            return 'Number of Hessian calls'
        if name == 'warning':
            return 'Optimisation warning'
        if name == 'xh_vect':
            return 'XH bond vector'

        # Ok, try the relaxation data specific objects.
        return relax_data.return_data_desc(name)


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


    def return_units(self, param, spin=None, spin_id=None):
        """Function for returning a string representing the parameters units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return the string
        'picoseconds' for te.


        @param param:   The name of the parameter to return the units string for.
        @type param:    str
        @param spin:    The spin container.
        @type spin:     SpinContainer instance
        @param spin_id: The spin identification string (ignored if the spin container is supplied).
        @type spin_id:  str
        @return:        The parameter units string.
        @rtype:         str
        """

        # Get the object name.
        object_name = self.return_data_name(param)

        # Test for objects needing the spin container.
        if object_name in ['rex']:
            # The spin must be specified to get frequency units.
            if spin == None and spin_id == None:
                raise RelaxNoSpinSpecError

            # Get the spin.
            if not spin:
                spin = return_spin(spin_id)

        # tm (nanoseconds).
        if object_name == 'tm' or object_name == 'local_tm':
            return 'ns'

        # te, tf, and ts (picoseconds).
        elif object_name in ['te', 'tf', 'ts']:
            return 'ps'

        # Rex (value at 1st field strength).
        elif object_name == 'rex' and hasattr(spin, 'frq_labels'):
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
        if not ds.current_pipe:
            raise RelaxNoPipeError

        # Test if the pipe type is 'mf'.
        function_type = ds[ds.current_pipe].pipe_type
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

        if model_type == 'diff' or model_type == 'all':
            # Spherical diffusion.
            if ds.diff[self.run].type == 'sphere':
                # Return the parameter array.
                if index == 0:
                    ds.diff[self.run].tm_err = error

                # Increment.
                inc = inc + 1

            # Spheroidal diffusion.
            elif ds.diff[self.run].type == 'spheroid':
                # Return the parameter array.
                if index == 0:
                    ds.diff[self.run].tm_err = error
                elif index == 1:
                    ds.diff[self.run].Da_err = error
                elif index == 2:
                    ds.diff[self.run].theta_err = error
                elif index == 3:
                    ds.diff[self.run].phi_err = error

                # Increment.
                inc = inc + 4

            # Ellipsoidal diffusion.
            elif ds.diff[self.run].type == 'ellipsoid':
                # Return the parameter array.
                if index == 0:
                    ds.diff[self.run].tm_err = error
                elif index == 1:
                    ds.diff[self.run].Da_err = error
                elif index == 2:
                    ds.diff[self.run].Dr_err = error
                elif index == 3:
                    ds.diff[self.run].alpha_err = error
                elif index == 4:
                    ds.diff[self.run].beta_err = error
                elif index == 5:
                    ds.diff[self.run].gamma_err = error

                # Increment.
                inc = inc + 6


        # Model-free parameter errors for the model type 'all'.
        #######################################################

        if model_type == 'all':
            # Loop over the sequence.
            for i in xrange(len(ds.res[self.run])):
                # Skip deselected residues.
                if not ds.res[self.run][i].select:
                    continue

                # Loop over the residue specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        setattr(ds.res[self.run][i], param + "_err", error)

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the model types 'mf' and 'local_tm'.
        ################################################################

        if model_type == 'mf' or model_type == 'local_tm':
            # Skip deselected residues.
            if not ds.res[self.run][instance].select:
                return

            # Loop over the residue specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    setattr(ds.res[self.run][instance], param + "_err", error)

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


    def set_selected_sim(self, instance, select_sim):
        """Set all simulation selection flags.

        @param instance:    Either the spin container or data pipe container object.
        @type instance:     SpinContainer or PipeContainer instance
        @param select_sim:  The selection flags.
        @type select_sim:   bool
        """

        # Determine the model type.
        model_type = self.determine_model_type()

        # Single instance.
        if model_type == 'all' or model_type == 'diff':
            ds[ds.current_pipe].select_sim = select_sim

        # Multiple instances.
        else:
            # Get the spin container.
            spin = return_spin_from_index(instance)

            # Set the simulation flags.
            spin.select_sim = select_sim


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

        # Determine the model type.
        model_type = self.determine_model_type()

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')

        # List of diffusion tensor parameters.
        if model_type == 'diff' or model_type == 'all':
            # Spherical diffusion.
            if ds.diff[self.run].type == 'sphere':
                diff_params = ['tm']

            # Spheroidal diffusion.
            elif ds.diff[self.run].type == 'spheroid':
                diff_params = ['tm', 'Da', 'theta', 'phi']

            # Ellipsoidal diffusion.
            elif ds.diff[self.run].type == 'ellipsoid':
                diff_params = ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma']


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Diffusion tensor parameters and non residue specific minimisation statistics.
        if model_type == 'diff' or model_type == 'all':
            # Loop over the parameters.
            for object_name in diff_params:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(ds.diff[self.run], sim_object_name):
                    raise RelaxError, "Monte Carlo parameter values have already been set."

            # Loop over the minimisation stats objects.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(ds, sim_object_name):
                    raise RelaxError, "Monte Carlo parameter values have already been set."

        # Residue specific parameters.
        if model_type != 'diff':
            for i in xrange(len(ds.res[self.run])):
                # Skip deselected residues.
                if not ds.res[self.run][i].select:
                    continue

                # Loop over all the parameter names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Test if the simulation object already exists.
                    if hasattr(ds.res[self.run][i], sim_object_name):
                        raise RelaxError, "Monte Carlo parameter values have already been set."


        # Set the Monte Carlo parameter values.
        #######################################

        # Loop over the global minimisation stats objects.
        for object_name in min_names:
            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Create the simulation object.
            setattr(ds, sim_object_name, {})

            # Get the simulation object.
            sim_object = getattr(ds, sim_object_name)

            # Add the run.
            sim_object[self.run] = []

            # Loop over the simulations.
            for j in xrange(ds.sim_number[self.run]):
                # Get the object.
                object = getattr(ds, object_name)

                # Test if the object has the key self.run.
                if not object.has_key(self.run):
                    continue

                # Copy and append the data.
                sim_object[self.run].append(deepcopy(object[self.run]))

        # Diffusion tensor parameters and non residue specific minimisation statistics.
        if model_type == 'diff' or model_type == 'all':
            # Loop over the parameters.
            for object_name in diff_params:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(ds.diff[self.run], sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(ds.diff[self.run], sim_object_name)

                # Loop over the simulations.
                for j in xrange(ds.sim_number[self.run]):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(ds.diff[self.run], object_name)))

        # Residue specific parameters.
        if model_type != 'diff':
            for i in xrange(len(ds.res[self.run])):
                # Skip deselected residues.
                if not ds.res[self.run][i].select:
                    continue

                # Loop over all the data names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    setattr(ds.res[self.run][i], sim_object_name, [])

                    # Get the simulation object.
                    sim_object = getattr(ds.res[self.run][i], sim_object_name)

                    # Loop over the simulations.
                    for j in xrange(ds.sim_number[self.run]):
                        # Copy and append the data.
                        sim_object.append(deepcopy(getattr(ds.res[self.run][i], object_name)))

                # Loop over all the minimisation object names.
                for object_name in min_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    setattr(ds.res[self.run][i], sim_object_name, [])

                    # Get the simulation object.
                    sim_object = getattr(ds.res[self.run][i], sim_object_name)

                    # Loop over the simulations.
                    for j in xrange(ds.sim_number[self.run]):
                        # Copy and append the data.
                        sim_object.append(deepcopy(getattr(ds.res[self.run][i], object_name)))


    def sim_pack_data(self, run, i, sim_data):
        """Function for packing Monte Carlo simulation data."""

        # Test if the simulation data already exists.
        if hasattr(ds.res[run][i], 'relax_sim_data'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        ds.res[run][i].relax_sim_data = sim_data


    def sim_return_chi2(self, run, instance):
        """Function for returning the array of simulation chi-squared values."""

        # Arguments.
        self.run = run

        # Determine the model type.
        model_type = self.determine_model_type()

        # Single instance.
        if model_type == 'all' or model_type == 'diff':
            return ds.chi2_sim[self.run]

        # Multiple instances.
        else:
            return ds.res[self.run][instance].chi2_sim


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

        if model_type == 'diff' or model_type == 'all':
            # Spherical diffusion.
            if ds.diff[self.run].type == 'sphere':
                # Return the parameter array.
                if index == 0:
                    return ds.diff[self.run].tm_sim

                # Increment.
                inc = inc + 1

            # Spheroidal diffusion.
            elif ds.diff[self.run].type == 'spheroid':
                # Return the parameter array.
                if index == 0:
                    return ds.diff[self.run].tm_sim
                elif index == 1:
                    return ds.diff[self.run].Da_sim
                elif index == 2:
                    return ds.diff[self.run].theta_sim
                elif index == 3:
                    return ds.diff[self.run].phi_sim

                # Increment.
                inc = inc + 4

            # Ellipsoidal diffusion.
            elif ds.diff[self.run].type == 'ellipsoid':
                # Return the parameter array.
                if index == 0:
                    return ds.diff[self.run].tm_sim
                elif index == 1:
                    return ds.diff[self.run].Da_sim
                elif index == 2:
                    return ds.diff[self.run].Dr_sim
                elif index == 3:
                    return ds.diff[self.run].alpha_sim
                elif index == 4:
                    return ds.diff[self.run].beta_sim
                elif index == 5:
                    return ds.diff[self.run].gamma_sim

                # Increment.
                inc = inc + 6


        # Model-free parameters for the model type 'all'.
        #################################################

        if model_type == 'all':
            # Loop over the sequence.
            for i in xrange(len(ds.res[self.run])):
                # Skip deselected residues.
                if not ds.res[self.run][i].select:
                    continue

                # Loop over the residue specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        return getattr(ds.res[self.run][i], param + "_sim")

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the model types 'mf' and 'local_tm'.
        ################################################################

        if model_type == 'mf' or model_type == 'local_tm':
            # Skip deselected residues.
            if not ds.res[self.run][instance].select:
                return

            # Loop over the residue specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    return getattr(ds.res[self.run][instance], param + "_sim")

                # Increment.
                inc = inc + 1


    def sim_return_selected(self, run, instance):
        """Function for returning the array of selected simulation flags."""

        # Arguments.
        self.run = run

        # Determine the model type.
        model_type = self.determine_model_type()

        # Single instance.
        if model_type == 'all' or model_type == 'diff':
            return ds.select_sim[self.run]

        # Multiple instances.
        else:
            return ds.res[self.run][instance].select_sim


    def skip_function(self, instance=None, min_instances=None, num_instances=None):
        """Skip certain data.

        @keyword instance:      The index of the minimisation instance.
        @type instance:         int
        @keyword min_instances: The total number of minimisation instances.
        @type min_instances:    int
        @keyword num_instances: The total number of instances.
        @type num_instances:    int
        """

        # Determine the model type.
        model_type = self.determine_model_type()

        # All spins.
        combine = False
        if min_instances == 1 and min_instances != num_instances:
            combine = True

        # Sequence specific data.
        if (model_type == 'mf' or model_type == 'local_tm') and not combine and not return_spin_from_index(instance).select:
            return True

        # Don't skip.
        return False


    def deselect(self, run, i, sim_index=None):
        """Function for deselecting models or simulations."""

        # Arguments.
        self.run = run

        # Determine the model type.
        model_type = self.determine_model_type()

        # Simulation deselect.
        if sim_index != None:
            # Single instance.
            if model_type == 'mf' or model_type == 'local_tm':
                ds.res[self.run][i].select_sim[sim_index] = 0

            # Multiple instances.
            else:
                ds.select_sim[self.run][sim_index] = 0

        # Residue deselect.
        else:
            # Single residue.
            if model_type == 'mf' or model_type == 'local_tm':
                ds.res[self.run][i].select = 0
