###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Module for the optimisation of the relaxation dispersion models."""

# Python module imports.
from minfx.generic import generic_minimise
from minfx.grid import grid
from numpy import dot
from numpy.linalg import inv
from re import search
import sys

# relax module imports.
from lib.check_types import is_float
from lib.errors import RelaxError
from lib.text.sectioning import subsection
from multi import Memo, Result_command, Slave_command
from specific_analyses.relax_disp.disp_data import loop_exp_frq_point, return_cpmg_frqs, return_index_from_disp_point, return_index_from_exp_type, return_index_from_frq, return_offset_data, return_param_key_from_data, return_r1_data, return_r2eff_arrays, return_spin_lock_nu1, return_value_from_frq_index
from specific_analyses.relax_disp.parameters import assemble_param_vector, disassemble_param_vector, linear_constraints, loop_parameters, param_conversion, param_num
from specific_analyses.relax_disp.variables import MODEL_CR72, MODEL_CR72_FULL, MODEL_DPL94, MODEL_LM63, MODEL_M61, MODEL_M61B, MODEL_NS_R1RHO_2SITE, MODEL_TP02
from target_functions.relax_disp import Dispersion


def grid_search_setup(spins=None, spin_ids=None, param_vector=None, lower=None, upper=None, inc=None, scaling_matrix=None):
    """The grid search setup function.

    @keyword spins:             The list of spin data containers for the block.
    @type spins:                list of SpinContainer instances
    @keyword spin_ids:          The corresponding spin ID strings.
    @type spin_ids:             list of str
    @keyword param_vector:      The parameter vector.
    @type param_vector:         numpy array
    @keyword lower:             The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
    @type lower:                array of numbers
    @keyword upper:             The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
    @type upper:                array of numbers
    @keyword inc:               The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
    @type inc:                  array of int
    @keyword scaling_matrix:    The scaling matrix.
    @type scaling_matrix:       numpy diagonal matrix
    @return:                    A tuple of the grid size and the minimisation options.  For the minimisation options, the first dimension corresponds to the model parameter.  The second dimension is a list of the number of increments, the lower bound, and upper bound.
    @rtype:                     (int, list of lists [int, float, float])
    """

    # The length of the parameter array.
    n = len(param_vector)

    # Make sure that the length of the parameter array is > 0.
    if n == 0:
        raise RelaxError("Cannot run a grid search on a model with zero parameters.")

    # Lower bounds.
    if lower != None and len(lower) != n:
        raise RelaxLenError('lower bounds', n)

    # Upper bounds.
    if upper != None and len(upper) != n:
        raise RelaxLenError('upper bounds', n)

    # Increment.
    if isinstance(inc, list) and len(inc) != n:
        raise RelaxLenError('increment', n)
    elif isinstance(inc, int):
        inc = [inc]*n

    # Set up the default bounds.
    if not lower:
        # Init.
        lower = []
        upper = []

        # The R2eff model.
        if cdp.model_type == 'R2eff':
            # Loop over each spectrometer frequency and dispersion point.
            for exp_type, frq, point in loop_exp_frq_point():
                # Loop over the parameters.
                for param_name, param_index, spin_index, frq_index in loop_parameters(spins=spins):
                    # R2eff relaxation rate (from 1 to 40 s^-1).
                    if param_name == 'r2eff':
                        lower.append(1.0)
                        upper.append(40.0)

                    # Intensity.
                    elif param_name == 'i0':
                        lower.append(0.0001)
                        upper.append(max(spins[spin_index].intensities.values()))

        # All other models.
        else:
            # Loop over the parameters.
            for param_name, param_index, spin_index, frq_index in loop_parameters(spins=spins):
                # Cluster specific parameter.
                if spin_index == None:
                    spin_index = 0

                # R2 relaxation rates (from 1 to 40 s^-1).
                if param_name in ['r2', 'r2a', 'r2b']:
                    lower.append(1.0)
                    upper.append(40.0)

                # The pA.pB.dw**2 and pA.dw**2 parameters.
                elif param_name in ['phi_ex', 'phi_ex_B', 'phi_ex_C', 'padw2']:
                    lower.append(0.0)
                    upper.append(10.0)

                # Chemical shift difference between states A and B.
                elif param_name in ['dw', 'dwH']:
                    lower.append(0.0)
                    upper.append(10.0)

                # The population of state A.
                elif param_name == 'pA':
                    if spins[spin_index].model == MODEL_M61B:
                        lower.append(0.85)
                    else:
                        lower.append(0.5)
                    upper.append(1.0)

                # Exchange rates.
                elif param_name in ['kex', 'k_AB', 'kB', 'kC']:
                    lower.append(1.0)
                    upper.append(100000.0)

                # Time of exchange.
                elif param_name in ['tex']:
                    lower.append(1/200000.0)
                    upper.append(0.5)

    # Pre-set parameters.
    for param_name, param_index, spin_index, frq_index in loop_parameters(spins=spins):
        # Cluster specific parameter.
        if spin_index == None:
            spin_index = 0

        # Get the parameter.
        if hasattr(spins[spin_index], param_name):
            val = getattr(spins[spin_index], param_name)

            # Value already set.
            if is_float(val) and val != 0.0:
                # Printout.
                print("The spin '%s' parameter '%s' is pre-set to %s, skipping it in the grid search." % (spin_ids[spin_index], param_name, val))

                # Turn of the grid search for this parameter.
                inc[param_index] = 1
                lower[param_index] = val
                upper[param_index] = val

    # The full grid size.
    grid_size = 1
    for i in range(n):
        grid_size *= inc[i]

    # Diagonal scaling of minimisation options.
    lower_new = []
    upper_new = []
    for i in range(n):
        lower_new.append(lower[i] / scaling_matrix[i, i])
        upper_new.append(upper[i] / scaling_matrix[i, i])

    # Return the data structures.
    return grid_size, inc, lower_new, upper_new



class Disp_memo(Memo):
    """The relaxation dispersion memo class."""

    def __init__(self, spins=None, cluster_name=None, sim_index=None, scaling_matrix=None, verbosity=None):
        """Initialise the relaxation dispersion memo class.

        This is used for handling the optimisation results returned from a slave processor.  It runs on the master processor and is used to store data which is passed to the slave processor and then passed back to the master via the results command.


        @keyword spins:             The list of spin data container for the cluster.  If this argument is supplied, then the spin_id argument will be ignored.
        @type spins:                list of SpinContainer instances
        @keyword cluster_name:      The name of the cluster to optimise.  This is used for printouts.
        @type cluster_name:         list of str
        @keyword sim_index:         The optional MC simulation index.
        @type sim_index:            int
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        @keyword verbosity:         The verbosity level.  This is used by the result command returned to the master for printouts.
        @type verbosity:            int
        """

        # Execute the base class __init__() method.
        super(Disp_memo, self).__init__()

        # Store the arguments.
        self.spins = spins
        self.cluster_name = cluster_name
        self.sim_index = sim_index
        self.scaling_matrix = scaling_matrix
        self.verbosity = verbosity



class Disp_minimise_command(Slave_command):
    """Command class for relaxation dispersion optimisation on the slave processor."""

    def __init__(self, spins=None, spin_ids=None, sim_index=None, scaling_matrix=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, verbosity=0, lower=None, upper=None, inc=None, fields=None):
        """Initialise the base class, storing all the master data to be sent to the slave processor.

        This method is run on the master processor whereas the run() method is run on the slave processor.


        @keyword spins:             The list of spin data container for the cluster.  If this argument is supplied, then the spin_id argument will be ignored.
        @type spins:                list of SpinContainer instances
        @keyword spin_ids:          The list of spin ID strings corresponding to the spins argument.
        @type spin_ids:             list of str
        @keyword sim_index:         The optional MC simulation index.
        @type sim_index:            int
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
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
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  array of int
        @keyword fields:            The list of unique of spectrometer field strengths.
        @type fields:               int
        """

        # Execute the base class __init__() method.
        super(Disp_minimise_command, self).__init__()

        # Store the arguments needed by the run() method.
        self.spins = spins
        self.spin_ids = spin_ids
        self.sim_index = sim_index
        self.scaling_matrix = scaling_matrix
        self.verbosity = verbosity
        self.min_algor = min_algor
        self.min_options = min_options
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.max_iterations = max_iterations
        self.fields = fields

        # Create the initial parameter vector.
        self.param_vector = assemble_param_vector(spins=self.spins)
        if len(scaling_matrix):
            self.param_vector = dot(inv(scaling_matrix), self.param_vector)

        # Get the grid search minimisation options.
        self.lower_new, self.upper_new = None, None
        if search('^[Gg]rid', min_algor):
            self.grid_size, self.inc_new, self.lower_new, self.upper_new = grid_search_setup(spins=spins, spin_ids=spin_ids, param_vector=self.param_vector, lower=lower, upper=upper, inc=inc, scaling_matrix=self.scaling_matrix)

        # Linear constraints.
        self.A, self.b = None, None
        if constraints:
            self.A, self.b = linear_constraints(spins=spins, scaling_matrix=scaling_matrix)

        # Test if the spectrometer frequencies have been set.
        if spins[0].model in [MODEL_LM63, MODEL_CR72, MODEL_CR72_FULL, MODEL_M61, MODEL_TP02] and not hasattr(cdp, 'spectrometer_frq'):
            raise RelaxError("The spectrometer frequency information has not been specified.")

        # The R2eff/R1rho data.
        self.values, self.errors, self.missing, self.frqs, self.exp_types = return_r2eff_arrays(spins=spins, spin_ids=spin_ids, fields=fields, field_count=len(fields), sim_index=sim_index)

        # The offset and R1 data for R1rho off-resonance models.
        self.chemical_shifts, self.offsets, self.tilt_angles, self.r1 = None, None, None, None
        if spins[0].model in [MODEL_DPL94, MODEL_TP02, MODEL_NS_R1RHO_2SITE]:
            self.chemical_shifts, self.offsets, self.tilt_angles = return_offset_data(spins=spins, spin_ids=spin_ids, fields=fields, field_count=len(fields))
            self.r1 = return_r1_data(spins=spins, spin_ids=spin_ids, fields=fields, field_count=len(fields), sim_index=sim_index)

        # Parameter number.
        self.param_num = param_num(spins=spins)

        # The dispersion data.
        self.dispersion_points = cdp.dispersion_points
        self.cpmg_frqs = return_cpmg_frqs(ref_flag=False)
        self.spin_lock_nu1 = return_spin_lock_nu1(ref_flag=False)

        # The relaxation times.
        self.relax_times = cdp.relax_time_list[0]


    def run(self, processor, completed):
        """Set up and perform the optimisation."""

        # Print out.
        if self.verbosity >= 1:
            # Individual spin block section.
            top = 2
            if self.verbosity >= 2:
                top += 2
            subsection(file=sys.stdout, text="Fitting to the spin block %s"%self.spin_ids, prespace=top)

            # Grid search printout.
            if search('^[Gg]rid', self.min_algor):
                print("Unconstrained grid search size: %s (constraints may decrease this size).\n" % self.grid_size)

        # Initialise the function to minimise.
        model = Dispersion(model=self.spins[0].model, num_params=self.param_num, num_spins=len(self.spins), num_frq=len(self.fields), num_disp_points=self.dispersion_points, exp_types=self.exp_types, values=self.values, errors=self.errors, missing=self.missing, frqs=self.frqs, cpmg_frqs=self.cpmg_frqs, spin_lock_nu1=self.spin_lock_nu1, chemical_shifts=self.chemical_shifts, spin_lock_offsets=self.offsets, tilt_angles=self.tilt_angles, r1=self.r1, relax_time=self.relax_times, scaling_matrix=self.scaling_matrix)

        # Grid search.
        if search('^[Gg]rid', self.min_algor):
            results = grid(func=model.func, args=(), num_incs=self.inc_new, lower=self.lower_new, upper=self.upper_new, A=self.A, b=self.b, verbosity=self.verbosity)

            # Unpack the results.
            param_vector, chi2, iter_count, warning = results
            f_count = iter_count
            g_count = 0.0
            h_count = 0.0

        # Minimisation.
        else:
            results = generic_minimise(func=model.func, args=(), x0=self.param_vector, min_algor=self.min_algor, min_options=self.min_options, func_tol=self.func_tol, grad_tol=self.grad_tol, maxiter=self.max_iterations, A=self.A, b=self.b, full_output=True, print_flag=self.verbosity)

            # Unpack the results.
            if results == None:
                return
            param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

        # Create the result command object to send back to the master.
        processor.return_object(Disp_result_command(processor=processor, memo_id=self.memo_id, param_vector=param_vector, chi2=chi2, iter_count=iter_count, f_count=f_count, g_count=g_count, h_count=h_count, warning=warning, missing=self.missing, back_calc=model.back_calc, completed=False))



class Disp_result_command(Result_command):
    """Class for processing the dispersion optimisation results.

    This object will be sent from the slave back to the master to have its run() method executed.
    """

    def __init__(self, processor=None, memo_id=None, param_vector=None, chi2=None, iter_count=None, f_count=None, g_count=None, h_count=None, warning=None, missing=None, back_calc=None, completed=True):
        """Set up this class object on the slave, placing the minimisation results here.

        @keyword processor:     The processor object.
        @type processor:        multi.processor.Processor instance
        @keyword memo_id:       The memo identification string.
        @type memo_id:          str
        @keyword param_vector:  The optimised parameter vector.
        @type param_vector:     numpy rank-1 array
        @keyword chi2:          The final target function value.
        @type chi2:             float
        @keyword iter_count:    The number of optimisation iterations.
        @type iter_count:       int
        @keyword f_count:       The total function call count.
        @type f_count:          int
        @keyword g_count:       The total gradient call count.
        @type g_count:          int
        @keyword h_count:       The total Hessian call count.
        @type h_count:          int
        @keyword warning:       Any optimisation warnings.
        @type warning:          str or None
        @keyword missing:       The data structure indicating which R2eff/R1rho' base data is missing.
        @type missing:          numpy rank-3 array
        @keyword back_calc:     The back-calculated R2eff/R1rho' data structure from the target function class.  This is will be transfered to the master to be stored in the r2eff_bc data structure.
        @type back_calc:        numpy rank-3 array
        @keyword completed:     A flag which if True signals that the optimisation successfully completed.
        @type completed:        bool
        """

        # Execute the base class __init__() method.
        super(Disp_result_command, self).__init__(processor=processor, completed=completed)

        # Store the arguments (to be sent back to the master).
        self.memo_id = memo_id
        self.param_vector = param_vector
        self.chi2 = chi2
        self.iter_count = iter_count
        self.f_count = f_count
        self.g_count = g_count
        self.h_count = h_count
        self.warning = warning
        self.missing = missing
        self.back_calc = back_calc
        self.completed = completed


    def run(self, processor=None, memo=None):
        """Disassemble the model-free optimisation results (on the master).

        @param processor:   Unused!
        @type processor:    None
        @param memo:        The dispersion memo.  This holds a lot of the data and objects needed for processing the results from the slave.
        @type memo:         memo
        """

        # Scaling.
        if memo.scaling_matrix != None:
            param_vector = dot(memo.scaling_matrix, self.param_vector)

        # Disassemble the parameter vector.
        disassemble_param_vector(param_vector=param_vector, spins=memo.spins, sim_index=memo.sim_index)
        param_conversion(spins=memo.spins, sim_index=memo.sim_index)

        # Monte Carlo minimisation statistics.
        if memo.sim_index != None:
            for spin in memo.spins:
                # Chi-squared statistic.
                spin.chi2_sim[memo.sim_index] = self.chi2

                # Iterations.
                spin.iter_sim[memo.sim_index] = self.iter_count

                # Function evaluations.
                spin.f_count_sim[memo.sim_index] = self.f_count

                # Gradient evaluations.
                spin.g_count_sim[memo.sim_index] = self.g_count

                # Hessian evaluations.
                spin.h_count_sim[memo.sim_index] = self.h_count

                # Warning.
                spin.warning_sim[memo.sim_index] = self.warning

        # Normal statistics.
        else:
            for spin in memo.spins:
                # Chi-squared statistic.
                spin.chi2 = self.chi2

                # Iterations.
                spin.iter = self.iter_count

                # Function evaluations.
                spin.f_count = self.f_count

                # Gradient evaluations.
                spin.g_count = self.g_count

                # Hessian evaluations.
                spin.h_count = self.h_count

                # Warning.
                spin.warning = self.warning

        # Store the back-calculated values.
        if memo.sim_index == None:
            for spin_index in range(len(memo.spins)):
                # Alias the spin.
                spin = memo.spins[spin_index]

                # No data.
                if not hasattr(spin, 'r2eff'):
                    continue

                # Initialise.
                if not hasattr(spin, 'r2eff_bc'):
                    spin.r2eff_bc = {}

                # Loop over the R2eff data.
                for exp_type, frq, point in loop_exp_frq_point():
                    # The indices.
                    exp_type_index = return_index_from_exp_type(exp_type=exp_type)
                    disp_pt_index = return_index_from_disp_point(point, exp_type=exp_type)
                    frq_index = return_index_from_frq(frq)

                    # Missing data.
                    if self.missing[exp_type_index, spin_index, frq_index, disp_pt_index]:
                        continue

                    # The R2eff key.
                    key = return_param_key_from_data(frq=frq, point=point)

                    # Store the back-calculated data.
                    spin.r2eff_bc[key] = self.back_calc[spin_index, frq_index, disp_pt_index]

        # Optimisation printout.
        if memo.verbosity:
            print("\nOptimised parameter values:")
            for param_name, param_index, spin_index, frq_index in loop_parameters(spins=memo.spins):
                # The parameter with additional details.
                param_text = param_name
                if param_name in ['r2', 'r2a', 'r2b']:
                    frq = return_value_from_frq_index(frq_index)
                    if frq:
                        param_text += " (%.3f MHz)" % (frq / 1e6) 
                param_text += ":"

                # The printout.
                print("%-20s %25.15f" % (param_text, param_vector[param_index]))

        # Printout.
        if memo.sim_index != None:
            print("Simulation %s, cluster %s" % (memo.sim_index+1, memo.cluster_name))
