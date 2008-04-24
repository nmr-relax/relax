###############################################################################
#                                                                             #
# Copyright (C) 2004-2007 Edward d'Auvergne                                   #
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
from LinearAlgebra import inverse
from math import sqrt
from numpy import array, average, dot, float64, identity, zeros
from re import match, search
import sys

# relax module imports.
from data import Data as relax_data_store
from base_class import Common_functions
from minimise.generic import generic_minimise
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxLenError, RelaxNoModelError, RelaxNoPipeError, RelaxNoSequenceError

# C modules.
try:
    from maths_fns.relax_fit import setup, func, dfunc, d2func, back_calc_I
except ImportError:
    sys.stderr.write("\nImportError: relaxation curve fitting is unavailible, try compiling the C modules.\n")
    C_module_exp_fn = 0
else:
    C_module_exp_fn = 1



class Relax_fit(Common_functions):
    def __init__(self):
        """Class containing functions for relaxation data."""


    def assemble_param_vector(self, index=None, sim_index=None):
        """Function for assembling various pieces of data into a numpy parameter array."""

        # Initialise.
        param_vector = []

        # Alias the residue specific data structure.
        data = relax_data_store.res[self.run][index]

        # Loop over the model parameters.
        for i in xrange(len(data.params)):
            # Relaxation rate.
            if data.params[i] == 'Rx':
                if sim_index != None:
                    param_vector.append(data.rx_sim[sim_index])
                elif data.rx == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(data.rx)

            # Initial intensity.
            elif data.params[i] == 'I0':
                if sim_index != None:
                    param_vector.append(data.i0_sim[sim_index])
                elif data.i0 == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(data.i0)

            # Intensity at infinity.
            elif data.params[i] == 'Iinf':
                if sim_index != None:
                    param_vector.append(data.iinf_sim[sim_index])
                elif data.iinf == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(data.iinf)

        # Return a numpy array.
        return array(param_vector, float64)


    def assemble_scaling_matrix(self, index=None, scaling=1):
        """Function for creating the scaling matrix."""

        # Initialise.
        self.scaling_matrix = identity(len(self.param_vector), float64)
        i = 0

        # No diagonal scaling.
        if not scaling:
            return

        # Alias the residue specific data structure.
        data = relax_data_store.res[self.run][index]

        # Loop over the parameters.
        for i in xrange(len(data.params)):
            # Relaxation rate.
            if data.params[i] == 'Rx':
                pass

            # Intensity scaling.
            elif search('^i', data.params[i]):
                # Find the position of the first time point.
                pos = relax_data_store.relax_times[self.run].index(min(relax_data_store.relax_times[self.run]))

                # Scaling.
                self.scaling_matrix[i, i] = 1.0 / average(data.intensities[pos])

            # Increment i.
            i = i + 1


    def assign_function(self, run=None, i=None, intensity=None):
        """Function for assigning peak intensity data to either the reference or saturated spectra."""

        # Alias the residue specific data structure.
        data = relax_data_store.res[run][i]

        # Initialise.
        index = None
        if not hasattr(data, 'intensities'):
            data.intensities = []

        # Determine if the relaxation time already exists for the residue (duplicated spectra).
        for i in xrange(len(relax_data_store.relax_times[self.run])):
            if self.relax_time == relax_data_store.relax_times[self.run][i]:
                index = i

        # A new relaxation time has been encountered.
        if index >= len(data.intensities):
            data.intensities.append([intensity])

        # Duplicated spectra.
        else:
            data.intensities[index].append(intensity)


    def back_calc(self, run=None, index=None, relax_time_index=None):
        """Back-calculation of peak intensity for the given relaxation time."""

        # Run argument.
        self.run = run

        # Alias the residue specific data structure.
        data = relax_data_store.res[self.run][index]

        # Create the initial parameter vector.
        self.param_vector = self.assemble_param_vector(index=index)

        # Initialise the relaxation fit functions.
        setup(num_params=len(data.params), num_times=len(relax_data_store.relax_times[self.run]), values=data.ave_intensities, sd=relax_data_store.sd[self.run], relax_times=relax_data_store.relax_times[self.run], scaling_matrix=self.scaling_matrix)

        # Make a single function call.  This will cause back calculation and the data will be stored in the C module.
        func(self.param_vector)

        # Get the data back.
        results = back_calc_I()

        # Return the correct peak height.
        return results[relax_time_index]


    def create_mc_data(self, run, i):
        """Function for creating the Monte Carlo peak intensity data."""

        # Arguments
        self.run = run

        # Initialise the MC data data structure.
        mc_data = []

        # Alias the residue specific data structure.
        data = relax_data_store.res[self.run][i]

        # Skip unselected residues.
        if not data.select:
            return

        # Skip residues which have no data.
        if not hasattr(data, 'intensities'):
            return

        # Test if the model is set.
        if not hasattr(data, 'model') or not data.model:
            raise RelaxNoModelError, self.run

        # Loop over the spectral time points.
        for j in xrange(len(relax_data_store.relax_times[run])):
            # Back calculate the value.
            value = self.back_calc(run=run, index=i, relax_time_index=j)

            # Append the value.
            mc_data.append(value)

        # Return the MC data.
        return mc_data


    def data_init(self, spin):
        """Function for initialising the data structures."""

        # Get the data names.
        data_names = self.data_names()

        # Loop over the data structure names.
        for name in data_names:
            # Data structures which are initially empty arrays.
            list_data = [ 'params' ]
            if name in list_data:
                init_data = []

            # Otherwise initialise the data structure to None.
            else:
                init_data = None

            # If the name is not in 'spin', add it.
            if not hasattr(spin, name):
                setattr(spin, name, init_data)


    def data_names(self, set='all'):
        """Function for returning a list of names of data structures.

        Description
        ~~~~~~~~~~~

        The names are as follows:

        params:  An array of the parameter names associated with the model.

        rx:  Either the R1 or R2 relaxation rate.

        i0:  The initial intensity.

        iinf:  The intensity at infinity.

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
            names.append('params')

        # Parameters.
        if set == 'all' or set == 'params':
            names.append('rx')
            names.append('i0')
            names.append('iinf')

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
        Relaxation curve fitting default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        These values are completely arbitrary as peak heights (or volumes) are extremely variable
        and the Rx value is a compensation for both the R1 and R2 values.
        ___________________________________________________________________
        |                        |               |                        |
        | Data type              | Object name   | Value                  |
        |________________________|_______________|________________________|
        |                        |               |                        |
        | Relaxation rate        | 'rx'          | 8.0                    |
        |                        |               |                        |
        | Initial intensity      | 'i0'          | 10000.0                |
        |                        |               |                        |
        | Intensity at infinity  | 'iinf'        | 0.0                    |
        |                        |               |                        |
        |________________________|_______________|________________________|

        """

        # Relaxation rate.
        if param == 'rx':
            return 8.0

        # Initial intensity.
        if param == 'i0':
            return 10000.0

        # Intensity at infinity.
        if param == 'iinf':
            return 0.0


    def disassemble_param_vector(self, index=None, sim_index=None):
        """Function for disassembling the parameter vector."""

        # Alias the residue specific data structure.
        data = relax_data_store.res[self.run][index]

        # Monte Carlo simulations.
        if sim_index != None:
            # The relaxation rate.
            data.rx_sim[sim_index] = self.param_vector[0]

            # Initial intensity.
            data.i0_sim[sim_index] = self.param_vector[1]

            # Intensity at infinity.
            if relax_data_store.curve_type[self.run] == 'inv':
                data.iinf_sim[sim_index] = self.param_vector[2]

        # Parameter values.
        else:
            # The relaxation rate.
            data.rx = self.param_vector[0]

            # Initial intensity.
            data.i0 = self.param_vector[1]

            # Intensity at infinity.
            if relax_data_store.curve_type[self.run] == 'inv':
                data.iinf = self.param_vector[2]


    def grid_search(self, run, lower, upper, inc, constraints, verbosity, sim_index=None):
        """The grid search function."""

        # Arguments.
        self.lower = lower
        self.upper = upper
        self.inc = inc

        # Minimisation.
        self.minimise(run=run, min_algor='grid', constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def grid_search_setup(self, index=None):
        """The grid search setup function."""

        # The length of the parameter array.
        n = len(self.param_vector)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            raise RelaxError, "Cannot run a grid search on a model with zero parameters."

        # Lower bounds.
        if self.lower != None:
            if len(self.lower) != n:
                raise RelaxLenError, ('lower bounds', n)

        # Upper bounds.
        if self.upper != None:
            if len(self.upper) != n:
                raise RelaxLenError, ('upper bounds', n)

        # Increment.
        if type(self.inc) == list:
            if len(self.inc) != n:
                raise RelaxLenError, ('increment', n)
            inc = self.inc
        elif type(self.inc) == int:
            temp = []
            for j in xrange(n):
                temp.append(self.inc)
            inc = temp

        # Minimisation options initialisation.
        min_options = []
        j = 0

        # Alias the residue specific data structure.
        data = relax_data_store.res[self.run][index]

        # Loop over the parameters.
        for i in xrange(len(data.params)):
            # Relaxation rate (from 0 to 20 s^-1).
            if data.params[i] == 'Rx':
                min_options.append([inc[j], 0.0, 20.0])

            # Intensity
            elif search('^I', data.params[i]):
                # Find the position of the first time point.
                pos = relax_data_store.relax_times[self.run].index(min(relax_data_store.relax_times[self.run]))

                # Scaling.
                min_options.append([inc[j], 0.0, average(data.intensities[pos])])

            # Increment j.
            j = j + 1

        # Set the lower and upper bounds if these are supplied.
        if self.lower != None:
            for j in xrange(n):
                if self.lower[j] != None:
                    min_options[j][1] = self.lower[j]
        if self.upper != None:
            for j in xrange(n):
                if self.upper[j] != None:
                    min_options[j][2] = self.upper[j]

        # Test if the grid is too large.
        self.grid_size = 1
        for i in xrange(len(min_options)):
            self.grid_size = self.grid_size * min_options[i][0]
        if type(self.grid_size) == long:
            raise RelaxError, "A grid search of size " + `self.grid_size` + " is too large."

        # Diagonal scaling of minimisation options.
        for j in xrange(len(min_options)):
            min_options[j][1] = min_options[j][1] / self.scaling_matrix[j, j]
            min_options[j][2] = min_options[j][2] / self.scaling_matrix[j, j]

        return min_options


    def linear_constraints(self, index=None):
        """Function for setting up the linear constraint matrices A and b.

        Standard notation
        ~~~~~~~~~~~~~~~~~

        The relaxation rate constraints are:

            Rx >= 0

        The intensity constraints are:

            I0 >= 0
            Iinf >= 0


        Matrix notation
        ~~~~~~~~~~~~~~~

        In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
        values, and b is a vector of scalars, these inequality constraints are:

            | 1  0  0 |     |  Rx  |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |  .  |  I0  |  >=  |    0    |
            |         |     |      |      |         |
            | 1  0  0 |     | Iinf |      |    0    |

        """

        # Initialisation (0..j..m).
        A = []
        b = []
        n = len(self.param_vector)
        zero_array = zeros(n, float64)
        i = 0
        j = 0

        # Alias the residue specific data structure.
        data = relax_data_store.res[self.run][index]

        # Loop over the parameters.
        for k in xrange(len(data.params)):
            # Relaxation rate.
            if data.params[k] == 'Rx':
                # Rx >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Intensity parameter.
            elif search('^I', data.params[k]):
                # I0, Iinf >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Increment i.
            i = i + 1

        # Convert to numpy data structures.
        A = array(A, float64)
        b = array(b, float64)

        return A, b


    def mean_and_error(self, run=None, verbosity=0):
        """Function for calculating the average intensity and standard deviation of all spectra."""

        # Arguments.
        self.run = run

        # Test if the standard deviation is already calculated.
        if hasattr(relax_data_store, 'sd'):
            raise RelaxError, "The average intensity and standard deviation of all spectra has already been calculated."

        # Print out.
        print "\nCalculating the average intensity and standard deviation of all spectra."

        # Initialise.
        relax_data_store.sd = {}
        relax_data_store.sd[self.run] = []

        # Loop over the time points.
        for time_index in xrange(len(relax_data_store.relax_times[self.run])):
            # Print out.
            print "\nTime point:  " + `relax_data_store.relax_times[self.run][time_index]` + " s"
            print "Number of spectra:  " + `relax_data_store.num_spectra[self.run][time_index]`
            if verbosity:
                print "%-5s%-6s%-20s%-20s" % ("Num", "Name", "Average", "SD")

            # Append zero to the global standard deviation structure.
            relax_data_store.sd[self.run].append(0.0)

            # Initialise the time point and residue specific sd.
            total_res = 0

            # Test for multiple spectra.
            if relax_data_store.num_spectra[self.run][time_index] == 1:
                multiple_spectra = 0
            else:
                multiple_spectra = 1

            # Calculate the mean value.
            for i in xrange(len(relax_data_store.res[self.run])):
                # Alias the residue specific data structure.
                data = relax_data_store.res[self.run][i]

                # Skip unselected residues.
                if not data.select:
                    continue

                # Skip and unselect residues which have no data.
                if not hasattr(data, 'intensities'):
                    data.select = 0
                    continue

                # Initialise the average intensity and standard deviation data structures.
                if not hasattr(data, 'ave_intensities'):
                    data.ave_intensities = []
                if not hasattr(data, 'sd'):
                    data.sd = []

                # Average intensity.
                data.ave_intensities.append(average(data.intensities[time_index]))

                # Sum of squared errors.
                SSE = 0.0
                for j in xrange(relax_data_store.num_spectra[self.run][time_index]):
                    SSE = SSE + (data.intensities[time_index][j] - data.ave_intensities[time_index]) ** 2

                # Standard deviation.
                #                 ____________________________
                #                /   1
                #       sd =    /  ----- * sum({Xi - Xav}^2)]
                #             \/   n - 1
                #
                if relax_data_store.num_spectra[self.run][time_index] == 1:
                    sd = 0.0
                else:
                    sd = sqrt(1.0 / (relax_data_store.num_spectra[self.run][time_index] - 1.0) * SSE)
                data.sd.append(sd)

                # Print out.
                if verbosity:
                    print "%-5i%-6s%-20s%-20s" % (data.num, data.name, `data.ave_intensities[time_index]`, `data.sd[time_index]`)

                # Sum of standard deviations (for average).
                relax_data_store.sd[self.run][time_index] = relax_data_store.sd[self.run][time_index] + data.sd[time_index]

                # Increment the number of residues counter.
                total_res = total_res + 1

            # Average sd.
            relax_data_store.sd[self.run][time_index] = relax_data_store.sd[self.run][time_index] / float(total_res)

            # Print out.
            print "Standard deviation for time point %s:  %s" % (`time_index`, `relax_data_store.sd[self.run][time_index]`)


        # Average across all spectra if there are time points with a single spectrum.
        if 0.0 in relax_data_store.sd[self.run]:
            # Initialise.
            sd = 0.0
            num_dups = 0

            # Loop over all time points.
            for i in xrange(len(relax_data_store.relax_times[self.run])):
                # Single spectrum (or extrodinarily accurate NMR spectra!).
                if relax_data_store.sd[self.run][i] == 0.0:
                    continue

                # Sum and count.
                sd = sd + relax_data_store.sd[self.run][i]
                num_dups = num_dups + 1

            # Average value.
            sd = sd / float(num_dups)

            # Assign the average value to all time points.
            for i in xrange(len(relax_data_store.relax_times[self.run])):
                relax_data_store.sd[self.run][i] = sd

            # Print out.
            print "\nStandard deviation (averaged over all spectra):  " + `sd`


    def minimise(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=0, scaling=1, verbosity=0, sim_index=None):
        """Relaxation curve fitting function."""

        # Arguments.
        self.run = run
        self.verbosity = verbosity

        # Test if the sequence data for self.run is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Alias the residue specific data structure.
            data = relax_data_store.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # Skip residues which have no data.
            if not hasattr(data, 'intensities'):
                continue

            # Create the initial parameter vector.
            self.param_vector = self.assemble_param_vector(index=i, sim_index=sim_index)

            # Diagonal scaling.
            self.assemble_scaling_matrix(index=i, scaling=scaling)
            self.param_vector = dot(inverse(self.scaling_matrix), self.param_vector)

            # Get the grid search minimisation options.
            if match('^[Gg]rid', min_algor):
                min_options = self.grid_search_setup(index=i)

            # Linear constraints.
            if constraints:
                A, b = self.linear_constraints(index=i)

            # Print out.
            if self.verbosity >= 1:
                # Individual residue print out.
                if self.verbosity >= 2:
                    print "\n\n"
                string = "Fitting to residue: " + `data.num` + " " + data.name
                print "\n\n" + string
                print len(string) * '~'

                # Grid search print out.
                if match('^[Gg]rid', min_algor):
                    print "Unconstrained grid search size: " + `self.grid_size` + " (constraints may decrease this size).\n"


            # Initialise the function to minimise.
            ######################################

            if sim_index == None:
                values = data.ave_intensities
            else:
                values = data.sim_intensities[sim_index]

            setup(num_params=len(data.params), num_times=len(relax_data_store.relax_times[self.run]), values=values, sd=relax_data_store.sd[self.run], relax_times=relax_data_store.relax_times[self.run], scaling_matrix=self.scaling_matrix)


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
                lm_error = zeros(len(data.relax_times), float64)
                index = 0
                for k in xrange(len(data.relax_times)):
                    lm_error[index:index+len(relax_error[k])] = relax_error[k]
                    index = index + len(relax_error[k])

                min_options = min_options + (self.relax_fit.lm_dri, lm_error)


            # Minimisation.
            ###############

            if constraints:
                results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=verbosity)
            else:
                results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=verbosity)
            if results == None:
                return
            self.param_vector, self.func, self.iter_count, self.f_count, self.g_count, self.h_count, self.warning = results

            # Scaling.
            if scaling:
                self.param_vector = dot(self.scaling_matrix, self.param_vector)

            # Disassemble the parameter vector.
            self.disassemble_param_vector(index=i, sim_index=sim_index)

            # Monte Carlo minimisation statistics.
            if sim_index != None:
                # Chi-squared statistic.
                data.chi2_sim[sim_index] = self.func

                # Iterations.
                data.iter_sim[sim_index] = self.iter_count

                # Function evaluations.
                data.f_count_sim[sim_index] = self.f_count

                # Gradient evaluations.
                data.g_count_sim[sim_index] = self.g_count

                # Hessian evaluations.
                data.h_count_sim[sim_index] = self.h_count

                # Warning.
                data.warning_sim[sim_index] = self.warning


            # Normal statistics.
            else:
                # Chi-squared statistic.
                data.chi2 = self.func

                # Iterations.
                data.iter = self.iter_count

                # Function evaluations.
                data.f_count = self.f_count

                # Gradient evaluations.
                data.g_count = self.g_count

                # Hessian evaluations.
                data.h_count = self.h_count

                # Warning.
                data.warning = self.warning


    def model_setup(self, model, params):
        """Function for updating various data structures dependant on the model selected."""

        # Set the model.
        relax_data_store.curve_type[self.run] = model

        # Initialise the data structures (if needed).
        self.data_init()

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Skip unselected residues.
            if not relax_data_store.res[self.run][i].select:
                continue

            # The model and parameter names.
            relax_data_store.res[self.run][i].model = model
            relax_data_store.res[self.run][i].params = params


    def overfit_deselect(self, run):
        """Function for deselecting residues without sufficient data to support minimisation"""

        # Test the sequence data exists:
        if not relax_data_store.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Loop over residue data:
        for residue in relax_data_store.res[run]:

            # Check for sufficient data
            if not hasattr(residue, 'intensities'):
                residue.select = 0
                continue

            # Require 3 or more data points
            if len(residue.intensities) < 3:
                residue.select = 0
                continue


    def read(self, file=None, dir=None, relax_time=0.0, format=None, heteronuc=None, proton=None, int_col=None):
        """Read in the peak intensity data.

        This method sets up the global data structures in the current data pipe and then calls
        intensity.read().


        @keyword file:          The name of the file containing the peak intensities.
        @type file:             str
        @keyword dir:           The directory where the file is located.
        @type dir:              str
        @keyword relax_time:    The time, in seconds, of the relaxation period.
        @type relax_time:       float
        @keyword format:        The type of file containing peak intensities.  This can currently be
                                one of 'sparky' or 'xeasy'.
        @type format:           str
        @keyword heteronuc:     The name of the heteronucleus as specified in the peak intensity
                                file.
        @type heteronuc:        str
        @keyword proton:        The name of the proton as specified in the peak intensity file.
        @type proton:           str
        @keyword int_col:       The column containing the peak intensity data (for a non-standard
                                formatted file).
        @type int_col:          int
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Initialise the global data if necessary.
        self.data_init()

        # Global relaxation time data structure.
        if not hasattr(cdp, 'relax_times'):
            cdp.relax_times = []

        # Number of spectra.
        if not hasattr(cdp, 'num_spectra'):
            relax_data_store.num_spectra = []

        # Determine if the relaxation time already exists for the residue (duplicated spectra).
        index = None
        for i in xrange(len(cdp.relax_times)):
            if relax_time == cdp.relax_times[i]:
                index = i

        # A new relaxation time.
        if index == None:
            # Add the time.
            cdp.relax_times.append(relax_time)

            # First spectrum.
            cdp.num_spectra.append(1)

        # Duplicated spectra.
        else:
            cdp.num_spectra[index] = cdp.num_spectra[index] + 1

        # Generic intensity function.
        intensity.read(file=file, dir=dir, format=format, heteronuc=heteronuc, proton=proton, int_col=int_col, assign_func=self.assign_function)


    def return_data(self, run, i):
        """Function for returning the peak intensity data structure."""

        return relax_data_store.res[run][i].intensities


    def return_error(self, run, i):
        """Function for returning the standard deviation data structure."""

        return relax_data_store.sd[run]


    def return_data_name(self, name):
        """
        Relaxation curve fitting data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        __________________________________________________________________________________________
        |                                   |                      |                             |
        | Data type                         | Object name          | Patterns                    |
        |___________________________________|______________________|_____________________________|
        |                                   |                      |                             |
        | Relaxation rate                   | 'rx'                 | '^[Rr]x$'                   |
        |                                   |                      |                             |
        | Average peak intensities (series) | 'ave_intensities'    | '^[Aa]ve[ -_][Ii]nt$'       |
        |                                   |                      |                             |
        | Initial intensity                 | 'i0'                 | '^[Ii]0$'                   |
        |                                   |                      |                             |
        | Intensity at infinity             | 'iinf'               | '^[Ii]inf$'                 |
        |                                   |                      |                             |
        | Relaxation period times (series)  | 'relax_times'        | '^[Rr]elax[ -_][Tt]imes$'   |
        |___________________________________|______________________|_____________________________|

        """

        # Relaxation rate.
        if match('^[Rr]x$', name):
            return 'rx'

        # Average peak intensities (series)
        if match('^[Aa]ve[ -_][Ii]nt$', name):
            return 'ave_intensities'

        # Initial intensity.
        if match('^[Ii]0$', name):
            return 'i0'

        # Intensity at infinity.
        if match('^[Ii]inf$', name):
            return 'iinf'

        # Relaxation period times (series).
        if match('^[Rr]elax[ -_][Tt]imes$', name):
            return 'relax_times'


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # Relaxation rate.
        if object_name == 'rx':
            grace_string = '\\qR\\sx\\Q'

        # Average peak intensities.
        elif object_name == 'ave_intensities':
            grace_string = '\\qAverage peak intensities\\Q'

        # Initial intensity.
        elif object_name == 'i0':
            grace_string = '\\qI\\s0\\Q'

        # Intensity at infinity.
        elif object_name == 'iinf':
            grace_string = '\\qI\\sinf\\Q'

        # Intensity at infinity.
        elif object_name == 'relax_times':
            grace_string = '\\qRelaxation time period (s)\\Q'

        # Return the Grace string.
        return grace_string


    def return_units(self, stat_type):
        """Dummy function which returns None as the stats have no units."""

        return None


    def select_model(self, run=None, model='exp'):
        """Function for selecting the model of the exponential curve."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if the run type is set to 'relax_fit'.
        function_type = relax_data_store.run_types[relax_data_store.run_names.index(self.run)]
        if function_type != 'relax_fit':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Two parameter exponential fit.
        if model == 'exp':
            print "Two parameter exponential fit."
            params = ['Rx', 'I0']

        # Three parameter inversion recovery fit.
        elif model == 'inv':
            print "Three parameter inversion recovery fit."
            params = ['Rx', 'I0', 'Iinf']

        # Invalid model.
        else:
            raise RelaxError, "The model '" + model + "' is invalid."

        # Set up the model.
        self.model_setup(model, params)


    def set_doc(self):
        """
        Relaxation curve fitting set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        Only three parameters can be set, the relaxation rate (Rx), the initial intensity (I0), and
        the intensity at infinity (Iinf).  Setting the parameter Iinf has no effect if the chosen
        model is that of the exponential curve which decays to zero.
        """


    def set_selected_sim(self, select_sim, spin):
        """Function for returning the array of selected simulation flags."""

        # Multiple spins.
        spin.select_sim = select_sim


    def sim_pack_data(self, run, i, sim_data):
        """Function for packing Monte Carlo simulation data."""

        # Test if the simulation data already exists.
        if hasattr(relax_data_store.res[run][i], 'sim_intensities'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        relax_data_store.res[run][i].sim_intensities = sim_data
