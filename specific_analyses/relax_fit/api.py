###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""The R1 and R2 exponential relaxation curve fitting API object."""

# Python module imports.
from minfx.generic import generic_minimise
from minfx.grid import grid
from numpy import dot, float64, zeros
from numpy.linalg import inv
from re import match, search
from warnings import warn

# relax module imports.
from dep_check import C_module_exp_fn
from lib.errors import RelaxError, RelaxNoModelError, RelaxNoSequenceError
from lib.warnings import RelaxDeselectWarning
from pipe_control.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.relax_fit.optimisation import back_calc, d2func_wrapper, dfunc_wrapper, func_wrapper
from specific_analyses.relax_fit.parameter_object import Relax_fit_params
from specific_analyses.relax_fit.parameters import assemble_param_vector, disassemble_param_vector, linear_constraints

# C modules.
if C_module_exp_fn:
    from target_functions.relax_fit import setup


class Relax_fit(API_base, API_common):
    """Class containing functions for relaxation curve fitting."""

    # Class variable for storing the class instance (for the singleton design pattern).
    instance = None

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Place methods into the API.
        self.base_data_loop = self._base_data_loop_spin
        self.model_loop = self._model_loop_spin
        self.print_model_title = self._print_model_title_spin
        self.return_conversion_factor = self._return_no_conversion_factor
        self.return_value = self._return_value_general
        self.set_error = self._set_error_spin
        self.set_param_values = self._set_param_values_spin
        self.set_selected_sim = self._set_selected_sim_spin
        self.sim_init_values = self._sim_init_values_spin
        self.sim_return_param = self._sim_return_param_spin
        self.sim_return_selected = self._sim_return_selected_spin

        # Place a copy of the parameter list object in the instance namespace.
        self._PARAMS = Relax_fit_params()


    def create_mc_data(self, data_id=None):
        """Create the Monte Carlo peak intensity data.

        @keyword data_id:   The spin identification string, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        @return:            The Monte Carlo simulation data.
        @rtype:             list of floats
        """

        # Initialise the MC data data structure.
        mc_data = {}

        # Get the spin container.
        spin = return_spin(data_id)

        # Skip deselected spins.
        if not spin.select:
            return

        # Skip spins which have no data.
        if not hasattr(spin, 'peak_intensity'):
            return

        # Test if the model is set.
        if not hasattr(spin, 'model') or not spin.model:
            raise RelaxNoModelError

        # Loop over the spectral time points.
        for id in list(cdp.relax_times.keys()):
            # Back calculate the value.
            value = back_calc(spin=spin, relax_time_id=id)

            # Append the value.
            mc_data[id] = value

        # Return the MC data.
        return mc_data


    def data_init(self, data, sim=False):
        """Initialise the spin specific data structures.

        @param data:    The spin ID string from the _base_data_loop_spin() method.
        @type data:     str
        @keyword sim:   The Monte Carlo simulation flag, which if true will initialise the simulation data structure.
        @type sim:      bool
        """

        # Get the spin container.
        spin = return_spin(data)

        # Loop over the data structure names.
        for name in self.data_names(set='params'):
            # Data structures which are initially empty arrays.
            list_data = [ 'params' ]
            if name in list_data:
                init_data = []

            # Otherwise initialise the data structure to None.
            else:
                init_data = None

            # If the name is not in the spin container, add it.
            if not hasattr(spin, name):
                setattr(spin, name, init_data)


    def get_param_names(self, model_info=None):
        """Return a vector of parameter names.

        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        @return:                The vector of parameter names.
        @rtype:                 list of str
        """

        # Simply return the two parameter names.
        return ['rx', 'i0']


    def get_param_values(self, model_info=None, sim_index=None):
        """Return a vector of parameter values.

        @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() method.
        @type model_info:       SpinContainer instance, str
        @keyword sim_index:     The optional Monte Carlo simulation index.
        @type sim_index:        int
        @return:                The vector of parameter values.
        @rtype:                 list of str
        """

        # Unpack the data.
        spin, spin_id = model_info

        # Return the vector.
        return assemble_param_vector(spin=spin, sim_index=sim_index)


    def grid_search(self, lower=None, upper=None, inc=None, scaling_matrix=None, constraints=True, verbosity=1, sim_index=None):
        """The exponential curve fitting grid search method.

        @keyword lower:             The per-model lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:                list of lists of numbers
        @keyword upper:             The per-model upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:                list of lists of numbers
        @keyword inc:               The per-model increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.
        @type inc:                  list of lists of int
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword constraints:       If True, constraints are applied during the grid search (eliminating parts of the grid).  If False, no constraints are used.
        @type constraints:          bool
        @keyword verbosity:         A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to apply the grid search to.  If None, the normal model is optimised.
        @type sim_index:            int
        """

        # Minimisation.
        self.minimise(min_algor='grid', lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling_matrix=None, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Relaxation curve fitting minimisation method.

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
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The per-model lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                list of lists of numbers
        @keyword upper:             The per-model upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                list of lists of numbers
        @keyword inc:               The per-model increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  list of lists of int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over the sequence.
        model_index = 0
        for spin, spin_id in self.model_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins which have no data.
            if not hasattr(spin, 'peak_intensity'):
                continue

            # Create the initial parameter vector.
            param_vector = assemble_param_vector(spin=spin)

            # Diagonal scaling.
            if scaling_matrix[model_index] != None:
                param_vector = dot(inv(scaling_matrix[model_index]), param_vector)

            # Linear constraints.
            if constraints:
                A, b = linear_constraints(spin=spin, scaling_matrix=scaling_matrix[model_index])
            else:
                A, b = None, None

            # Print out.
            if verbosity >= 1:
                # Individual spin printout.
                if verbosity >= 2:
                    print("\n\n")

                string = "Fitting to spin " + repr(spin_id)
                print("\n\n" + string)
                print(len(string) * '~')


            # Initialise the function to minimise.
            ######################################

            # The keys.
            keys = list(spin.peak_intensity.keys())

            # The peak intensities and times.
            values = []
            errors = []
            times = []
            for key in keys:
                # The values.
                if sim_index == None:
                    values.append(spin.peak_intensity[key])
                else:
                    values.append(spin.peak_intensity_sim[sim_index][key])

                # The errors.
                errors.append(spin.peak_intensity_err[key])

                # The relaxation times.
                times.append(cdp.relax_times[key])

            # The scaling matrix in a diagonalised list form.
            scaling_list = []
            if scaling_matrix[model_index] == None:
                for i in range(len(param_vector)):
                    scaling_list.append(1.0)
            else:
                for i in range(len(scaling_matrix[model_index])):
                    scaling_list.append(scaling_matrix[model_index][i, i])

            setup(num_params=len(spin.params), num_times=len(values), values=values, sd=errors, relax_times=times, scaling_matrix=scaling_list)


            # Setup the minimisation algorithm when constraints are present.
            ################################################################

            if constraints and not match('^[Gg]rid', min_algor):
                algor = min_options[0]
            else:
                algor = min_algor


            # Levenberg-Marquardt minimisation.
            ###################################

            if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                # Reconstruct the error data structure.
                lm_error = zeros(len(spin.relax_times), float64)
                index = 0
                for k in range(len(spin.relax_times)):
                    lm_error[index:index+len(relax_error[k])] = relax_error[k]
                    index = index + len(relax_error[k])

                min_options = min_options + (self.relax_fit.lm_dri, lm_error)


            # Minimisation.
            ###############

            # Grid search.
            if search('^[Gg]rid', min_algor):
                results = grid(func=func_wrapper, args=(), num_incs=inc[model_index], lower=lower[model_index], upper=upper[model_index], A=A, b=b, verbosity=verbosity)

                # Unpack the results.
                param_vector, chi2, iter_count, warning = results
                f_count = iter_count
                g_count = 0.0
                h_count = 0.0

            # Minimisation.
            else:
                results = generic_minimise(func=func_wrapper, dfunc=dfunc_wrapper, d2func=d2func_wrapper, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=True, print_flag=verbosity)

                # Unpack the results.
                if results == None:
                    return
                param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

            # Scaling.
            if scaling_matrix[model_index] != None:
                param_vector = dot(scaling_matrix[model_index], param_vector)

            # Disassemble the parameter vector.
            disassemble_param_vector(param_vector=param_vector, spin=spin, sim_index=sim_index)

            # Monte Carlo minimisation statistics.
            if sim_index != None:
                # Chi-squared statistic.
                spin.chi2_sim[sim_index] = chi2

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


            # Normal statistics.
            else:
                # Chi-squared statistic.
                spin.chi2 = chi2

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

            # Increment the model index.
            model_index += 1


    def overfit_deselect(self, data_check=True, verbose=True):
        """Deselect spins which have insufficient data to support minimisation.

        @keyword data_check:    A flag to signal if the presence of base data is to be checked for.
        @type data_check:       bool
        @keyword verbose:       A flag which if True will allow printouts.
        @type verbose:          bool
        """

        # Print out.
        if verbose:
            print("\nOver-fit spin deselection:")

        # Test the sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over spin data.
        deselect_flag = False
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Check if data exists.
            if not hasattr(spin, 'peak_intensity'):
                warn(RelaxDeselectWarning(spin_id, 'missing intensity data'))
                spin.select = False
                deselect_flag = True
                continue

            # Require 3 or more data points.
            elif len(spin.peak_intensity) < 3:
                warn(RelaxDeselectWarning(spin_id, 'insufficient data, 3 or more data points are required'))
                spin.select = False
                deselect_flag = True
                continue

            # Check that the number of relaxation times is complete.
            if len(spin.peak_intensity) != len(cdp.relax_times):
                raise RelaxError("The %s peak intensity points of the spin '%s' does not match the expected number of %s (the IDs %s do not match %s)." % (len(spin.peak_intensity), spin_id, len(cdp.relax_times), list(spin.peak_intensity.keys()), list(cdp.relax_times.keys())))

        # Final printout.
        if verbose and not deselect_flag:
            print("No spins have been deselected.")


    def return_data(self, data_id=None):
        """Function for returning the peak intensity data structure.

        @keyword data_id:   The spin identification string, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        @return:            The peak intensity data structure.
        @rtype:             list of float
        """

        # Get the spin container.
        spin = return_spin(data_id)

        # Return the peak intensities.
        return spin.peak_intensity


    def return_error(self, data_id):
        """Return the standard deviation data structure.

        @param data_id: The spin identification string, as yielded by the base_data_loop() generator
                        method.
        @type data_id:  str
        @return:        The standard deviation data structure.
        @rtype:         list of float
        """

        # Get the spin container.
        spin = return_spin(data_id)

        # Return the error list.
        return spin.peak_intensity_err


    def sim_pack_data(self, data_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param data_id:     The spin identification string, as yielded by the base_data_loop() generator method.
        @type data_id:      str
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Get the spin container.
        spin = return_spin(data_id)

        # Create the data structure.
        spin.peak_intensity_sim = sim_data
