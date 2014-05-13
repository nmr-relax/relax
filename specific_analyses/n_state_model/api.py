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
"""The N-state model or structural ensemble analysis."""

# Python module imports.
from copy import deepcopy
from math import pi
from minfx.generic import generic_minimise
from minfx.grid import grid
from numpy import dot, float64, zeros
from re import search
from warnings import warn

# relax module imports.
import lib.arg_check
from lib.errors import RelaxError, RelaxInfError, RelaxNaNError, RelaxNoModelError
from lib.float import isNaN, isInf
from lib.optimisation import test_grid_ops
from lib.warnings import RelaxWarning
from pipe_control import align_tensor, pcs, rdc
from pipe_control.align_tensor import opt_uses_tensor
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import spin_loop
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.n_state_model.data import base_data_types, calc_ave_dist, num_data_points
from specific_analyses.n_state_model.optimisation import minimise_bc_data, target_fn_setup
from specific_analyses.n_state_model.parameter_object import N_state_params
from specific_analyses.n_state_model.parameters import disassemble_param_vector, linear_constraints, param_num
from target_functions.potential import quad_pot


class N_state_model(API_base, API_common):
    """Class containing functions for the N-state model."""

    # Class variable for storing the class instance (for the singleton design pattern).
    instance = None

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Place methods into the API.
        self.model_loop = self._model_loop_single_global
        self.overfit_deselect = self._overfit_deselect_dummy
        self.set_selected_sim = self._set_selected_sim_global
        self.sim_return_selected = self._sim_return_selected_global

        # Place a copy of the parameter list object in the instance namespace.
        self._PARAMS = N_state_params()


    def base_data_loop(self):
        """Loop over the base data of the spins - RDCs, PCSs, and NOESY data.

        This loop iterates for each data point (RDC, PCS, NOESY) for each spin or interatomic data container, returning the identification information.

        @return:            A list of the spin or interatomic data container, the data type ('rdc', 'pcs', 'noesy'), and the alignment ID if required.
        @rtype:             list of [SpinContainer instance, str, str] or [InteratomContainer instance, str, str]
        """

        # Loop over the interatomic data containers.
        for interatom in interatomic_loop():
            # Skip deselected data.
            if not interatom.select:
                continue

            # Re-initialise the data structure.
            data = [interatom, None, None]

            # RDC data.
            if hasattr(interatom, 'rdc'):
                data[1] = 'rdc'

                # Loop over the alignment IDs.
                for id in cdp.rdc_ids:
                    # Add the ID.
                    data[2] = id

                    # Yield the set.
                    yield data

            # NOESY data.
            if hasattr(interatom, 'noesy'):
                data[1] = 'noesy'

                # Loop over the alignment IDs.
                for id in cdp.noesy_ids:
                    # Add the ID.
                    data[2] = id

                    # Yield the set.
                    yield data

        # Loop over the spins.
        for spin in spin_loop():
            # Skip deselected data.
            if not spin.select:
                continue

            # Re-initialise the data structure.
            data = [spin, None, None]

            # PCS data.
            if hasattr(spin, 'pcs'):
                data[1] = 'pcs'

                # Loop over the alignment IDs.
                for id in cdp.pcs_ids:
                    # Add the ID.
                    data[2] = id

                    # Yield the set.
                    yield data


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Calculation function.

        Currently this function simply calculates the NOESY flat-bottom quadratic energy potential,
        if NOE restraints are available.

        @keyword spin_id:   The spin identification string (unused).
        @type spin_id:      None or str
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The MC simulation index (unused).
        @type sim_index:    None
        """

        # Set up the target function for direct calculation.
        model, param_vector, data_types, scaling_matrix = target_fn_setup()

        # Calculate the chi-squared value.
        if model:
            # Make a function call.
            chi2 = model.func(param_vector)

            # Store the global chi-squared value.
            cdp.chi2 = chi2

            # Store the back-calculated data.
            minimise_bc_data(model)

            # Calculate the RDC Q factors.
            if 'rdc' in data_types:
                rdc.q_factors()

            # Calculate the PCS Q factors.
            if 'pcs' in data_types:
                pcs.q_factors()

        # NOE potential.
        if hasattr(cdp, 'noe_restraints'):
            # Init some numpy arrays.
            num_restraints = len(cdp.noe_restraints)
            dist = zeros(num_restraints, float64)
            pot = zeros(num_restraints, float64)
            lower = zeros(num_restraints, float64)
            upper = zeros(num_restraints, float64)

            # Loop over the NOEs.
            for i in range(num_restraints):
                # Create arrays of the NOEs.
                lower[i] = cdp.noe_restraints[i][2]
                upper[i] = cdp.noe_restraints[i][3]

                # Calculate the average distances, using -6 power averaging.
                dist[i] = calc_ave_dist(cdp.noe_restraints[i][0], cdp.noe_restraints[i][1], exp=-6)

            # Calculate the quadratic potential.
            quad_pot(dist, pot, lower, upper)

            # Store the distance and potential information.
            cdp.ave_dist = []
            cdp.quad_pot = []
            for i in range(num_restraints):
                cdp.ave_dist.append([cdp.noe_restraints[i][0], cdp.noe_restraints[i][1], dist[i]])
                cdp.quad_pot.append([cdp.noe_restraints[i][0], cdp.noe_restraints[i][1], pot[i]])


    def create_mc_data(self, data_id=None):
        """Create the Monte Carlo data by back-calculation.

        @keyword data_id:   The list of spin ID, data type, and alignment ID, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        @return:            The Monte Carlo Ri data.
        @rtype:             list of floats
        """

        # Initialise the MC data structure.
        mc_data = []

        # Alias the spin or interatomic data container.
        container = data_id[0]

        # RDC data.
        if data_id[1] == 'rdc' and hasattr(container, 'rdc'):
            # Does back-calculated data exist?
            if not hasattr(container, 'rdc_bc'):
                self.calculate()

            # The data.
            if not hasattr(container, 'rdc_bc') or not data_id[2] in container.rdc_bc:
                data = None
            else:
                data = container.rdc_bc[data_id[2]]

            # Append the data.
            mc_data.append(data)

        # NOESY data.
        elif data_id[1] == 'noesy' and hasattr(container, 'noesy'):
            # Does back-calculated data exist?
            if not hasattr(container, 'noesy_bc'):
                self.calculate()

            # Append the data.
            mc_data.append(container.noesy_bc)

        # PCS data.
        elif data_id[1] == 'pcs' and hasattr(container, 'pcs'):
            # Does back-calculated data exist?
            if not hasattr(container, 'pcs_bc'):
                self.calculate()

            # The data.
            if not hasattr(container, 'pcs_bc') or not data_id[2] in container.pcs_bc:
                data = None
            else:
                data = container.pcs_bc[data_id[2]]

            # Append the data.
            mc_data.append(data)

        # Return the data.
        return mc_data


    def grid_search(self, lower=None, upper=None, inc=None, constraints=False, verbosity=0, sim_index=None):
        """The grid search function.

        @param lower:       The lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:        array of numbers
        @param upper:       The upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:        array of numbers
        @param inc:         The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.
        @type inc:          array of int
        @param constraints: If True, constraints are applied during the grid search (elinating parts of the grid).  If False, no constraints are used.
        @type constraints:  bool
        @param verbosity:   A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        """

        # Test if the N-state model has been set up.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('N-state')

        # The number of parameters.
        n = param_num()

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            print("Cannot run a grid search on a model with zero parameters, skipping the grid search.")
            return

        # Test the grid search options.
        test_grid_ops(lower=lower, upper=upper, inc=inc, n=n)

        # If inc is a single int, convert it into an array of that value.
        if isinstance(inc, int):
            inc = [inc]*n

        # Setup the default bounds.
        if not lower:
            # Init.
            lower = []
            upper = []

            # Loop over the parameters.
            for i in range(n):
                # i is in the parameter array.
                if i < len(cdp.params):
                    # Probabilities (default values).
                    if search('^p', cdp.params[i]):
                        lower.append(0.0)
                        upper.append(1.0)

                    # Angles (default values).
                    if search('^alpha', cdp.params[i]) or search('^gamma', cdp.params[i]):
                        lower.append(0.0)
                        upper.append(2*pi)
                    elif search('^beta', cdp.params[i]):
                        lower.append(0.0)
                        upper.append(pi)

                # The paramagnetic centre.
                elif hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed and (n - i) <= 3:
                    lower.append(-100)
                    upper.append(100)

                # Otherwise this must be an alignment tensor component.
                else:
                    lower.append(-1e-3)
                    upper.append(1e-3)

        # Determine the data type.
        data_types = base_data_types()

        # The number of tensors to optimise.
        tensor_num = align_tensor.num_tensors(skip_fixed=True)

        # Custom sub-grid search for when only tensors are optimised (as each tensor is independent, the number of points collapses from inc**(5*N) to N*inc**5).
        if cdp.model == 'fixed' and tensor_num > 1 and ('rdc' in data_types or 'pcs' in data_types) and not align_tensor.all_tensors_fixed() and hasattr(cdp, 'paramag_centre_fixed') and cdp.paramag_centre_fixed:
            # Print out.
            print("Optimising each alignment tensor separately.")

            # Store the alignment tensor fixed flags.
            fixed_flags = []
            for i in range(len(cdp.align_ids)):
                # Get the tensor object.
                tensor = align_tensor.return_tensor(index=i, skip_fixed=False)

                # Store the flag.
                fixed_flags.append(tensor.fixed)

                # Fix the tensor.
                tensor.set('fixed', True)

            # Loop over each sub-grid.
            for i in range(len(cdp.align_ids)):
                # Skip the tensor if originally fixed.
                if fixed_flags[i]:
                    continue

                # Get the tensor object.
                tensor = align_tensor.return_tensor(index=i, skip_fixed=False)

                # Unfix the current tensor.
                tensor.set('fixed', False)

                # Grid search parameter subsets.
                lower_sub = lower[i*5:i*5+5]
                upper_sub = upper[i*5:i*5+5]
                inc_sub = inc[i*5:i*5+5]

                # Minimisation of the sub-grid.
                self.minimise(min_algor='grid', lower=lower_sub, upper=upper_sub, inc=inc_sub, constraints=constraints, verbosity=verbosity, sim_index=sim_index)

                # Fix the tensor again.
                tensor.set('fixed', True)

            # Reset the state of the tensors.
            for i in range(len(cdp.align_ids)):
                # Get the tensor object.
                tensor = align_tensor.return_tensor(index=i, skip_fixed=False)

                # Fix the tensor.
                tensor.set('fixed', fixed_flags[i])

        # All other minimisation.
        else:
            self.minimise(min_algor='grid', lower=lower, upper=upper, inc=inc, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def is_spin_param(self, name):
        """Determine whether the given parameter is spin specific.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        False
        @rtype:         bool
        """

        # Spin specific parameters.
        if name in ['r', 'heteronuc_type', 'proton_type']:
            return True

        # All other parameters are global.
        return False


    def map_bounds(self, param, spin_id=None):
        """Create bounds for the OpenDX mapping function.

        @param param:       The name of the parameter to return the lower and upper bounds of.
        @type param:        str
        @param spin_id:     The spin identification string (unused).
        @type spin_id:      None
        @return:            The upper and lower bounds of the parameter.
        @rtype:             list of float
        """

        # Paramagnetic centre.
        if search('^paramag_[xyz]$', param):
            return [-100.0, 100.0]


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Minimisation function.

        @param min_algor:       The minimisation algorithm to use.
        @type min_algor:        str
        @param min_options:     An array of options to be used by the minimisation algorithm.
        @type min_options:      array of str
        @param func_tol:        The function tolerance which, when reached, terminates optimisation. Setting this to None turns of the check.
        @type func_tol:         None or float
        @param grad_tol:        The gradient tolerance which, when reached, terminates optimisation. Setting this to None turns of the check.
        @type grad_tol:         None or float
        @param max_iterations:  The maximum number of iterations for the algorithm.
        @type max_iterations:   int
        @param constraints:     If True, constraints are used during optimisation.
        @type constraints:      bool
        @param scaling:         If True, diagonal scaling is enabled during optimisation to allow the problem to be better conditioned.
        @type scaling:          bool
        @param verbosity:       A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:        int
        @param sim_index:       The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:        None or int
        @keyword lower:         The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:            array of numbers
        @keyword upper:         The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:            array of numbers
        @keyword inc:           The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:              array of int
        """

        # Set up the target function for direct calculation.
        model, param_vector, data_types, scaling_matrix = target_fn_setup(sim_index=sim_index, scaling=scaling)

        # Nothing to do!
        if not len(param_vector):
            warn(RelaxWarning("The model has no parameters, minimisation cannot be performed."))
            return

        # Right, constraints cannot be used for the 'fixed' model.
        if constraints and cdp.model == 'fixed':
            warn(RelaxWarning("Turning constraints off.  These cannot be used for the 'fixed' model."))
            constraints = False

            # Pop out the Method of Multipliers algorithm.
            if min_algor == 'Method of Multipliers':
                min_algor = min_options[0]
                min_options = min_options[1:]

        # And constraints absolutely must be used for the 'population' model.
        if not constraints and cdp.model == 'population':
            warn(RelaxWarning("Turning constraints on.  These absolutely must be used for the 'population' model."))
            constraints = True

            # Add the Method of Multipliers algorithm.
            min_options = (min_algor,) + min_options
            min_algor = 'Method of Multipliers'

        # Disallow Newton optimisation and other Hessian optimisers for the paramagnetic centre position optimisation (the PCS Hessian is not yet implemented).
        if hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed:
            if min_algor in ['newton']:
                raise RelaxError("For the paramagnetic centre position, as the Hessians are not yet implemented Newton optimisation cannot be performed.")

        # Linear constraints.
        if constraints:
            A, b = linear_constraints(data_types=data_types, scaling_matrix=scaling_matrix)
        else:
            A, b = None, None

        # Grid search.
        if search('^[Gg]rid', min_algor):
            # Scaling.
            if scaling:
                for i in range(len(param_vector)):
                    lower[i] = lower[i] / scaling_matrix[i, i]
                    upper[i] = upper[i] / scaling_matrix[i, i]

            # The search.
            results = grid(func=model.func, args=(), num_incs=inc, lower=lower, upper=upper, A=A, b=b, verbosity=verbosity)

            # Unpack the results.
            param_vector, func, iter_count, warning = results
            f_count = iter_count
            g_count = 0.0
            h_count = 0.0

        # Minimisation.
        else:
            results = generic_minimise(func=model.func, dfunc=model.dfunc, d2func=model.d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=verbosity)

            # Unpack the results.
            if results == None:
                return
            param_vector, func, iter_count, f_count, g_count, h_count, warning = results

        # Catch infinite chi-squared values.
        if isInf(func):
            raise RelaxInfError('chi-squared')

        # Catch chi-squared values of NaN.
        if isNaN(func):
            raise RelaxNaNError('chi-squared')

        # Make a last function call to update the back-calculated RDC and PCS structures to the optimal values.
        chi2 = model.func(param_vector)

        # Scaling.
        if scaling:
            param_vector = dot(scaling_matrix, param_vector)

        # Disassemble the parameter vector.
        disassemble_param_vector(param_vector=param_vector, data_types=data_types, sim_index=sim_index)

        # Monte Carlo minimisation statistics.
        if sim_index != None:
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

        # Statistical analysis.
        if sim_index == None and ('rdc' in data_types or 'pcs' in data_types):
            # Get the final back calculated data (for the Q factor and
            minimise_bc_data(model)

            # Calculate the RDC Q factors.
            if 'rdc' in data_types:
                rdc.q_factors()

            # Calculate the PCS Q factors.
            if 'pcs' in data_types:
                pcs.q_factors()


    def model_statistics(self, model_info=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword model_info:    The data returned from model_loop() (unused).
        @type model_info:       None
        @keyword spin_id:       The spin identification string.  This is ignored in the N-state model.
        @type spin_id:          None or str
        @keyword global_stats:  A parameter which determines if global or local statistics are returned.  For the N-state model, this argument is ignored.
        @type global_stats:     None or bool
        @return:                The optimisation statistics, in tuple format, of the number of parameters (k), the number of data points (n), and the chi-squared value (chi2).
        @rtype:                 tuple of (int, int, float)
        """

        # Return the values.
        return param_num(), num_data_points(), cdp.chi2


    def return_data(self, data_id):
        """Return the base data for the given data ID.

        @keyword data_id:   The list of spin ID, data type, and alignment ID, as yielded by the base_data_loop() generator method.
        @type data_id:      list of str
        @return:            The base data.
        @rtype:             list of (float or None)
        """

        # Alias the spin or interatomic data container, data type and alignment ID.
        container = data_id[0]
        data_type = data_id[1]
        align_id = data_id[2]

        # The data structure to return.
        data = []

        # Skip deselected spins.
        if data_id[1] == 'pcs' and not container.select:
            return

        # Return the RDC data.
        if data_type == 'rdc' and hasattr(container, 'rdc'):
            if align_id not in container.rdc:
                data.append(None)
            else:
                data.append(container.rdc[align_id])

        # Return the NOESY data.
        elif data_type == 'noesy' and hasattr(container, 'noesy'):
            data.append(container.noesy)

        # Return the PCS data.
        elif data_id[1] == 'pcs' and hasattr(container, 'pcs'):
            if align_id not in container.pcs:
                data.append(None)
            else:
                data.append(container.pcs[align_id])

        # Return the data.
        return data


    def return_error(self, data_id=None):
        """Create and return the spin specific Monte Carlo Ri error structure.

        @keyword data_id:   The list of spin ID, data type, and alignment ID, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        @return:            The Monte Carlo simulation data errors.
        @rtype:             list of float
        """

        # Initialise the MC data structure.
        mc_errors = []

        # Alias the spin or interatomic data container.
        container = data_id[0]

        # Skip deselected spins.
        if data_id[1] == 'pcs' and not container.select:
            return

        # RDC data.
        if data_id[1] == 'rdc' and hasattr(container, 'rdc'):
            # Do errors exist?
            if not hasattr(container, 'rdc_err'):
                raise RelaxError("The RDC errors are missing for the spin pair '%s' and '%s'." % (container.spin_id1, container.spin_id2))

            # The error.
            if data_id[2] not in container.rdc_err:
                err = None
            else:
                err = container.rdc_err[data_id[2]]

            # Append the data.
            mc_errors.append(err)

        # NOESY data.
        elif data_id[1] == 'noesy' and hasattr(container, 'noesy'):
            # Do errors exist?
            if not hasattr(container, 'noesy_err'):
                raise RelaxError("The NOESY errors are missing for the spin pair '%s' and '%s'." % (container.spin_id1, container.spin_id2))

            # Append the data.
            mc_errors.append(container.noesy_err)

        # PCS data.
        elif data_id[1] == 'pcs' and hasattr(container, 'pcs'):
            # Do errors exist?
            if not hasattr(container, 'pcs_err'):
                raise RelaxError("The PCS errors are missing for spin '%s'." % data_id[0])

            # The error.
            if data_id[2] not in container.pcs_err:
                err = None
            else:
                err = container.pcs_err[data_id[2]]

            # Append the data.
            mc_errors.append(err)

        # Return the errors.
        return mc_errors


    def set_error(self, model_info, index, error):
        """Set the parameter errors.

        @param model_info:  The global model index originating from model_loop().
        @type model_info:   int
        @param index:       The index of the parameter to set the errors for.
        @type index:        int
        @param error:       The error value.
        @type error:        float
        """

        # Align parameters.
        names = ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz']

        # Alignment tensor parameters.
        if index < len(cdp.align_ids)*5:
            # The tensor and parameter index.
            param_index = index % 5
            tensor_index = (index - index % 5) / 5

            # Set the error.
            tensor = align_tensor.return_tensor(index=tensor_index, skip_fixed=True)
            tensor.set(param=names[param_index], value=error, category='err')

            # Return the object.
            return getattr(tensor, names[param_index]+'_err')


    def set_param_values(self, param=None, value=None, index=None, spin_id=None, error=False, force=True):
        """Set the N-state model parameter values.

        @keyword param:     The parameter name list.
        @type param:        list of str
        @keyword value:     The parameter value list.
        @type value:        list
        @keyword index:     The index for parameters which are of the list-type (probs, alpha, beta, and gamma).  This is ignored for all other types.
        @type index:        None or int
        @keyword spin_id:   The spin identification string (unused).
        @type spin_id:      None
        @keyword error:     A flag which if True will allow the parameter errors to be set instead of the values.
        @type error:        bool
        @keyword force:     A flag which if True will cause current values to be overwritten.  If False, a RelaxError will raised if the parameter value is already set.
        @type force:        bool
        """

        # Checks.
        lib.arg_check.is_str_list(param, 'parameter name')
        lib.arg_check.is_list(value, 'parameter value')

        # Loop over the parameters.
        for i in range(len(param)):
            # Is the parameter is valid?
            if not param[i]:
                raise RelaxError("The parameter '%s' is not valid for this data pipe type." % param[i])

            # Error object.
            if error:
                param[i] += '_err'

            # Set the indexed parameter.
            if param[i] in ['probs', 'alpha', 'beta', 'gamma']:
                obj = getattr(cdp, param[i])
                obj[index] = value[i]

            # Set the spin parameters.
            else:
                for spin in spin_loop(spin_id):
                    setattr(spin, param[i], value[i])


    def sim_init_values(self):
        """Initialise the Monte Carlo parameter values."""

        # Get the minimisation statistic object names.
        sim_names = self.data_names(set='min')

        # Add the paramagnetic centre, if optimised.
        if hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed:
            sim_names += ['paramagnetic_centre']

        # Alignments.
        if hasattr(cdp, 'align_tensors'):
            # The parameter names.
            names = ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz']

            # Loop over the alignments, adding the alignment tensor parameters to the tensor data container.
            for i in range(len(cdp.align_tensors)):
                # Skip non-optimised tensors.
                if not opt_uses_tensor(cdp.align_tensors[i]):
                    continue

                # Set up the number of simulations.
                cdp.align_tensors[i].set_sim_num(cdp.sim_number)

                # Loop over all the parameter names, setting the initial simulation values to those of the parameter value.
                for object_name in names:
                    for j in range(cdp.sim_number):
                        cdp.align_tensors[i].set(param=object_name, value=deepcopy(getattr(cdp.align_tensors[i], object_name)), category='sim', sim_index=j)

            # Create all other simulation objects.
            for object_name in sim_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(cdp, sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(cdp, sim_object_name)

                # Loop over the simulations.
                for j in range(cdp.sim_number):
                    # Append None to fill the structure.
                    sim_object.append(None)

            # Set the simulation paramagnetic centre positions to the optimised values.
            if hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed:
                for j in range(cdp.sim_number):
                    cdp.paramagnetic_centre_sim[j] = deepcopy(cdp.paramagnetic_centre)


    def sim_pack_data(self, data_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @keyword data_id:   The list of spin ID, data type, and alignment ID, as yielded by the base_data_loop() generator method.
        @type data_id:      list of str
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Alias the spin or interatomic data container.
        container = data_id[0]

        # RDC data.
        if data_id[1] == 'rdc' and hasattr(container, 'rdc'):
            # Initialise.
            if not hasattr(container, 'rdc_sim'):
                container.rdc_sim = {}
                
            # Store the data structure.
            container.rdc_sim[data_id[2]] = []
            for i in range(cdp.sim_number):
                container.rdc_sim[data_id[2]].append(sim_data[i][0])

        # NOESY data.
        elif data_id[1] == 'noesy' and hasattr(container, 'noesy'):
            # Store the data structure.
            container.noesy_sim = []
            for i in range(cdp.sim_number):
                container.noesy_sim[data_id[2]].append(sim_data[i][0])

        # PCS data.
        elif data_id[1] == 'pcs' and hasattr(container, 'pcs'):
            # Initialise.
            if not hasattr(container, 'pcs_sim'):
                container.pcs_sim = {}
                
            # Store the data structure.
            container.pcs_sim[data_id[2]] = []
            for i in range(cdp.sim_number):
                container.pcs_sim[data_id[2]].append(sim_data[i][0])


    def sim_return_param(self, model_info, index):
        """Return the array of simulation parameter values.

        @param model_info:  The global model index originating from model_loop().
        @type model_info:   int
        @param index:       The index of the parameter to return the array of values for.
        @type index:        int
        @return:            The array of simulation parameter values.
        @rtype:             list of float
        """

        # Align parameters.
        names = ['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz']

        # Alignment tensor parameters.
        if index < align_tensor.num_tensors(skip_fixed=True)*5:
            # The tensor and parameter index.
            param_index = index % 5
            tensor_index = (index - index % 5) / 5

            # Return the simulation parameter array.
            tensor = align_tensor.return_tensor(index=tensor_index, skip_fixed=True)
            return getattr(tensor, names[param_index]+'_sim')
