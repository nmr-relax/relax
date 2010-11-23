###############################################################################
#                                                                             #
# Copyright (C) 2004-2010 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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

# Module docstring.
"""The relaxation dispersion curve fitting specific code."""

# Python module imports.
from numpy import array, average, dot, float64, identity, log, zeros
from numpy.linalg import inv
from re import match, search

# relax module imports.
from api_base import API_base
from api_common import API_common
from dep_check import C_module_disp
from generic_fns import pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, generate_spin_id, return_spin, spin_loop
from minfx.generic import generic_minimise
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxLenError, RelaxNoModelError, RelaxNoSequenceError

# C modules.
if C_module_disp:
    from maths_fns.relax_disp import setup, func, dfunc, d2func, back_calc_I


class Relax_disp(API_base, API_common):
    """Class containing functions for relaxation dispersion curve fitting."""

    def assemble_param_vector(self, spin=None, sim_index=None):
        """Assemble the dispersion relaxation dispersion curve fitting parameter vector (as a numpy array).

        @keyword spin:          The spin data container.
        @type spin:             SpinContainer instance
        @keyword sim_index:     The optional MC simulation index.
        @type sim_index:        int
        @return:                An array of the parameter values of the dispersion relaxation model.
        @rtype:                 numpy array
        """

        # Initialise.
        param_vector = []

        # Loop over the model parameters.
        for i in xrange(len(spin.params)):
            # Transversal relaxation rate.
            if spin.params[i] == 'R2':
                if sim_index != None:
                    param_vector.append(spin.r2_sim[sim_index])
                elif spin.r2 == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.r2)

            # Chemical exchange contribution to 'R2'.
            elif spin.params[i] == 'Rex':
                if sim_index != None:
                    param_vector.append(spin.rex_sim[sim_index])
                elif spin.rex == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.rex)

            # Exchange rate.
            elif spin.params[i] == 'kex':
                if sim_index != None:
                    param_vector.append(spin.kex_sim[sim_index])
                elif spin.kex == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.kex)

            # Transversal relaxation rate for state A.
            if spin.params[i] == 'R2A':
                if sim_index != None:
                    param_vector.append(spin.r2a_sim[sim_index])
                elif spin.r2a == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.r2a)

            # Exchange rate from state A to state B.
            if spin.params[i] == 'kA':
                if sim_index != None:
                    param_vector.append(spin.ka_sim[sim_index])
                elif spin.ka == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.ka)

            # Chemical shift difference between states A and B.
            if spin.params[i] == 'dw':
                if sim_index != None:
                    param_vector.append(spin.dw_sim[sim_index])
                elif spin.dw == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.dw)

        # Return a numpy array.
        return array(param_vector, float64)


    def assemble_scaling_matrix(self, spin=None, scaling=True):
        """Create and return the scaling matrix.

        @keyword spin:          The spin data container.
        @type spin:             SpinContainer instance
        @keyword scaling:       A flag which if false will cause the identity matrix to be returned.
        @type scaling:          bool
        @return:                The diagonal and square scaling matrix.
        @rtype:                 numpy diagonal matrix
        """

        # Initialise.
        scaling_matrix = identity(len(spin.params), float64)
        i = 0

        # No diagonal scaling.
        if not scaling:
            return scaling_matrix

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Loop over the parameters.
        for i in xrange(len(spin.params)):
            # Effective transversal relaxation rate scaling.
            if spin.params[i] == 'R2eff':
                # Find the position of the first CPMG pulse train frequency point.
                pos = cdp.cpmg_frqs.index(min(cdp.cpmg_frqs))

                # Scaling.
                scaling_matrix[i, i] = 1.0 / average(spin.r2eff[pos])

            # Transversal relaxation rate scaling.
            elif spin.params[i] == 'R2':
                # Find the position of the first CPMG pulse train frequency point.
                pos = cdp.cpmg_frqs.index(min(cdp.cpmg_frqs))

                # Scaling.
                scaling_matrix[i, i] = 1e-1

            # Chemical exchange contribution to 'R2' scaling.
            elif spin.params[i] == 'Rex':
                # Find the position of the first CPMG pulse train frequency point.
                pos = cdp.cpmg_frqs.index(min(cdp.cpmg_frqs))

                # Scaling.
                scaling_matrix[i, i] = 1e-1

            # Exchange rate scaling.
            elif spin.params[i] == 'kex':
                # Find the position of the first CPMG pulse train frequency point.
                pos = cdp.cpmg_frqs.index(min(cdp.cpmg_frqs))

                # Scaling.
                scaling_matrix[i, i] = 1e-4

            # Transversal relaxation rate for state A scaling
            elif spin.params[i] == 'R2A':
                # Find the position of the first CPMG pulse train frequency point.
                pos = cdp.cpmg_frqs.index(min(cdp.cpmg_frqs))

                # Scaling.
                scaling_matrix[i, i] = 1e-1

            # Exchange rate from state A to state B scaling.
            elif spin.params[i] == 'kA':
                # Find the position of the first CPMG pulse train frequency point.
                pos = cdp.cpmg_frqs.index(min(cdp.cpmg_frqs))

                # Scaling.
                scaling_matrix[i, i] = 1e-4

            # Chemical shift difference between states A and B scaling.
            elif spin.params[i] == 'dw':
                # Find the position of the first CPMG pulse train frequency point.
                pos = cdp.cpmg_frqs.index(min(cdp.cpmg_frqs))

                # Scaling.
                scaling_matrix[i, i] = 1e-3

            # Increment i.
            i = i + 1

        # Return the scaling matrix.
        return scaling_matrix


    def back_calc(self, spin=None, result_index=None):
        """Back-calculation of peak intensity for the given CPMG pulse train frequency.

        @keyword spin:            The spin container.
        @type spin:               SpinContainer instance
        @keyword result_index:    The index for the back-calculated data associated to every CPMG or
                                  R1rho frequency, as well as every magnetic field frequency.
        @type result_index:       int
        @return:                  The R2eff value associated to every CPMG or R1rho frequency, as
                                  well as every magnetic field frequency.
        @rtype:                   float
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Create the initial parameter vector.
        param_vector = self.assemble_param_vector(spin=spin)

        # Create a scaling matrix.
        scaling_matrix = self.assemble_scaling_matrix(spin=spin, scaling=False)

        # Initialise the relaxation dispersion fit functions.
        setup(num_params=len(spin.params), num_times=len(cdp.cpmg_frqs), values=spin.intensities, sd=spin.intensity_err, cpmg_frqs=cdp.cpmg_frqs, scaling_matrix=scaling_matrix)

        # Make a single function call.  This will cause back calculation and the data will be stored in the C module.
        func(param_vector)

        # Get the data back.
        results = back_calc_I()

        # Return the correct peak height.
        return results[result_index]


    def calc_r2eff(self, exp_type='cpmg', id=None, delayT=None, int_cpmg=1.0, int_ref=1.0):
        """Calculate the effective transversal relaxation rate from the peak intensities. The
        equation depends on the experiment type chosen, either 'cpmg' or 'r1rho'.

        @keyword exp_type:   The experiment type, either 'cpmg' or 'r1rho'.
        @type exp_type:      str
        @keyword id:         The experimental identification string (allowing for multiple experiments
                             per data pipe).
        @type id:            str
        @keyword delayT:     The CPMG constant time delay (T) in s.
        @type delayT:        float
        @keyword int_cpmg:   The intensity of the peak in the CPMG spectrum.
        @type int_cpmg:      float
        @keyword int_ref:    The intensity of the peak in the reference spectrum.
        @type int_ref:       float
        """

        # Avoid division by zero.
        if int_ref == 0:
            raise RelaxError, "The reference peak intensity should not have a value of 0 (zero)"

        # Avoid other inmpossible mathematical situation.
        if int_cpmg == 0:
            raise RelaxError, "The CPMG peak intensity should not have a value of 0 (zero)"

        if delayT == 0:
            raise RelaxError, "The CPMG constant time delay (T) should not have a value of 0 (zero)"

        if exp_type == 'cpmg' and delayT != None:
            r2eff = - ( 1 / delayT ) * log ( int_cpmg / int_ref )
            return r2eff


    def cpmg_delayT(self, id=None, delayT=None):
        """Set the CPMG constant time delay (T) of the experiment.

        @keyword id:       The experimental identification string (allowing for multiple experiments
                           per data pipe).
        @type id:          str
        @keyword delayT:   The CPMG constant time delay (T) in s.
        @type delayT:      float
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Set up the dictionnary data structure if it doesn't exist yet.
        if not hasattr(cdp, 'delayT'):
            cdp.delayT = {}

        # Test if the pipe type is set to 'relax_disp'.
        function_type = cdp.pipe_type
        if function_type != 'relax_disp':
            raise RelaxFuncSetupError, specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Make sure the experiment type is set to 'cpmg'.
        if not cdp.exp_type == 'cpmg':
            raise RelaxError, "To use this user function, the experiment type must be set to 'cpmg'."

        # Test the CPMG constant time delay (T) has not already been set.
        if cdp.delayT.has_key(id):
           raise RelaxError, "The CPMG constant time delay (T) for the experiment " + `id` + " has already been set."

        # Set the CPMG constant time delay (T).
        cdp.delayT[id] = delayT
        print "The CPMG delay T for experiment " + `id` + " has been set to " + `cdp.delayT[id]`  + " s."


    def cpmg_frq(self, cpmg_frq=None, spectrum_id=None):
        """Set the CPMG frequency associated with a given spectrum.

        @keyword cpmg_frq:      The frequency, in Hz, of the CPMG pulse train.
        @type cpmg_frq:         float
        @keyword spectrum_id:   The spectrum identification string.
        @type spectrum_id:      str
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the spectrum id exists.
        if spectrum_id not in cdp.spectrum_ids:
            raise RelaxError, "The peak heights corresponding to spectrum id '%s' have not been loaded." % spectrum_id

        # Store the CPMG frequency in the class instance.
        if cpmg_frq != None:
            self.__cpmg_frq = float(cpmg_frq)

        # The index.
        index = cdp.spectrum_ids.index(spectrum_id)

        # Initialise the global CPMG frequency data structure if needed.
        if not hasattr(cdp, 'cpmg_frqs'):
            cdp.cpmg_frqs = [None] * len(cdp.spectrum_ids)

        # Index not present in the global CPMG frequency data structure.
        while 1:
            if index > len(cdp.cpmg_frqs) - 1:
                cdp.cpmg_frqs.append(None)
            else:
                break

        # Add the frequency at the correct position.
        cdp.cpmg_frqs[index] = cpmg_frq


    def create_mc_data(self, spin_id):
        """Create the Monte Carlo peak intensity data.

        @param spin_id: The spin identification string, as yielded by the base_data_loop() generator
                        method.
        @type spin_id:  str
        @return:        The Monte Carlo simulation data.
        @rtype:         list of floats
        """

        # Initialise the MC data data structure.
        mc_data = []

        # Get the spin container.
        spin = return_spin(spin_id)

        # Skip deselected spins.
        if not spin.select:
            return

        # Skip spins which have no data.
        if not hasattr(spin, 'intensities'):
            return

        # Test if the model is set.
        if not hasattr(spin, 'model') or not spin.model:
            raise RelaxNoModelError

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Loop over the spectral time points.
        for j in xrange(len(cdp.cpmg_frqs)):
            # Back calculate the value.
            value = self.back_calc(spin=spin, result_index=j)

            # Append the value.
            mc_data.append(value)

        # Return the MC data.
        return mc_data


    def data_init(self, spin):
        """Initialise the spin specific data structures.

        @param spin:    The spin container.
        @type spin:     SpinContainer instance
        """

        # Loop over the data structure names.
        for name in self.data_names():
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


    def data_names(self, set='all', error_names=False, sim_names=False):
        """Function for returning a list of names of data structures.

        Description
        ===========

        The names are as follows:

            - 'params', an array of the parameter names associated with the model.
            - 'r2', the transversal relaxation rate.
            - 'rex', the chemical exchange contribution to 'R2'.
            - 'kex', the exchange rate.
            - 'r2a', the transversal relaxation rate for state A.
            - 'ka', the exchange rate from state A to state B.
            - 'dw', the chemical shift difference between states A and B.
            - 'chi2', chi-squared value.
            - 'iter', iterations.
            - 'f_count', function count.
            - 'g_count', gradient count.
            - 'h_count', hessian count.
            - 'warning', minimisation warning.


        @keyword set:           The set of object names to return.  This can be set to 'all' for all
                                names, to 'generic' for generic object names, 'params' for parameter
                                names,or to 'min' for minimisation specific object names.
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
            names.append('params')

        # Parameters.
        if set == 'all' or set == 'params':
            names.append('r2')
            names.append('rex')
            names.append('kex')
            names.append('r2a')
            names.append('ka')
            names.append('dw')

        # Minimisation statistics.
        if set == 'all' or set == 'min':
            names.append('chi2')
            names.append('iter')
            names.append('f_count')
            names.append('g_count')
            names.append('h_count')
            names.append('warning')

        # Parameter errors.
        if error_names and (set == 'all' or set == 'params'):
            names.append('r2_err')
            names.append('rex_err')
            names.append('kex_err')
            names.append('r2a_err')
            names.append('ka_err')
            names.append('dw_err')

        # Parameter simulation values.
        if sim_names and (set == 'all' or set == 'params'):
            names.append('r2_sim')
            names.append('rex_sim')
            names.append('kex_sim')
            names.append('r2a_sim')
            names.append('ka_sim')
            names.append('dw_sim')

        # Return the names.
        return names


    def default_value(self, param):
        """
        Relaxation dispersion curve fitting default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        These values are arbitrary and will depend on the system studied.
        ________________________________________________________________________________
        |                                                   |               |          |
        | Data type                                         | Object name   | Value    |
        |___________________________________________________|_______________|__________|
        |                                                   |               |          |
        | Transversal relaxation rate                       | 'R2'          | 15.0     |
        |                                                   |               |          |
        | Chemical exchange contribution to 'R2'            | 'Rex'         | 5.0      |
        |                                                   |               |          |
        | Exchange rate                                     | 'kex'         | 10000.0  |
        |                                                   |               |          |
        | Transversal relaxation rate for state A           | 'R2A'         | 15.0     |
        |                                                   |               |          |
        | Exchange rate from state A to state B             | 'kA'          | 10000.0  |
        |                                                   |               |          |
        | Chemical shift difference between states A and B  | 'dw'          | 1000.0   |
        |                                                   |               |          |
        |___________________________________________________|_______________|__________|

        """

        # Transversal relaxation rate.
        if param == 'R2':
            return 15.0

        # Chemical exchange contribution to 'R2'.
        if param == 'Rex':
            return 5.0

        # Exchange rate.
        if param == 'kex':
            return 10000.0

        # Transversal relaxation rate for state A.
        if param == 'R2A' :
            return 15.0

        # Exchange rate from state A to state B.
        if param == 'kA' :
            return 10000

        # Chemical shift difference between states A and B.
        if param == 'dw' :
            return 1000.0


    def disassemble_param_vector(self, param_vector=None, spin=None, sim_index=None):
        """Disassemble the parameter vector.

        @keyword param_vector:  The parameter vector.
        @type param_vector:     numpy array
        @keyword spin:          The spin data container.
        @type spin:             SpinContainer instance
        @keyword sim_index:     The optional MC simulation index.
        @type sim_index:        int
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Monte Carlo simulations.
        if sim_index != None:
            # Transversal relaxation rate.
            spin.r2_sim[sim_index] = param_vector[0]

            # Chemical exchange contribution to 'R2'.
            spin.rex_sim[sim_index] = param_vector[1]

            # Exchange rate.
            spin.kex_sim[sim_index] = param_vector[2]

            # Transversal relaxation rate for state A.
            spin.r2a_sim[sim_index] = param_vector[3]

            # Exchange rate from state A to state B.
            spin.ka_sim[sim_index] = param_vector[4]

            # Chemical shift difference between states A and B.
            spin.dw_sim[sim_index] = param_vector[5]

        # Parameter values.
        else:
            # Transversal relaxation rate.
            spin.r2 = param_vector[0]

            # Chemical exchange contribution to 'R2'.
            spin.rex = param_vector[1]

            # Exchange rate.
            spin.kex = param_vector[2]

            # Transversal relaxation rate for state A.
            spin.r2a = param_vector[3]

            # Exchange rate from state A to state B.
            spin.ka = param_vector[4]

            # Chemical shift difference between states A and B.
            spin.dw = param_vector[5]


    def exp_type(self, exp_type='cpmg'):
        """Function for selecting the relaxation dispersion experiment type performed.
        @keyword exp: The relaxation dispersion experiment type.  Can be one of 'cpmg' or 'r1rho'.
        @type exp:    str
        """

        # Test if the current pipe exists.
        pipes.test()

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the pipe type is set to 'relax_disp'.
        function_type = cdp.pipe_type
        if function_type != 'relax_disp':
            raise RelaxFuncSetupError, specific_setup.get_string(function_type)

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # CPMG relaxation dispersion experiments.
        if exp_type == 'cpmg':
            print "CPMG relaxation dispersion experiments."
            cdp.exp_type = 'cpmg'

        # R1rho relaxation dispersion experiments.
        elif exp_type == 'r1rho':
            print "R1rho relaxation dispersion experiments."
            cdp.exp_type = 'r1rho'

        # Invalid relaxation dispersion experiment.
        else:
            raise RelaxError, "The relaxation dispersion experiment '" + exp_type + "' is invalid."


    def grid_search(self, lower=None, upper=None, inc=None, constraints=True, verbosity=1, sim_index=None):
        """The relaxation dispersion curve fitting grid search function.

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


    def grid_search_setup(self, spin=None, param_vector=None, lower=None, upper=None, inc=None, scaling_matrix=None):
        """The grid search setup function.

        @keyword spin:              The spin data container.
        @type spin:                 SpinContainer instance
        @keyword param_vector:      The parameter vector.
        @type param_vector:         numpy array
        @keyword lower:             The lower bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is
                                    only used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is
                                    only used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid
                                    search.  The number of elements in the array must equal to the
                                    number of parameters in the model.  This argument is only used
                                    when doing a grid search.
        @type inc:                  array of int
        @keyword scaling_matrix:    The scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        @return:                    A tuple of the grid size and the minimisation options.  For the
                                    minimisation options, the first dimension corresponds to the
                                    model parameter.  The second dimension is a list of the number
                                    of increments, the lower bound, and upper bound.
        @rtype:                     (int, list of lists [int, float, float])
        """

        # The length of the parameter array.
        n = len(param_vector)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            raise RelaxError, "Cannot run a grid search on a model with zero parameters."

        # Lower bounds.
        if lower != None:
            if len(lower) != n:
                raise RelaxLenError, ('lower bounds', n)

        # Upper bounds.
        if upper != None:
            if len(upper) != n:
                raise RelaxLenError, ('upper bounds', n)

        # Increment.
        if type(inc) == list:
            if len(inc) != n:
                raise RelaxLenError, ('increment', n)
            inc = inc
        elif type(inc) == int:
            temp = []
            for j in xrange(n):
                temp.append(inc)
            inc = temp

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Minimisation options initialisation.
        min_options = []
        j = 0

        # Loop over the parameters.
        for i in xrange(len(spin.params)):
            # Relaxation rate (from 0 to 20 s^-1).
            if spin.params[i] == 'Rx':
                min_options.append([inc[j], 0.0, 20.0])

            # Intensity
            elif search('^I', spin.params[i]):
                # Find the position of the first time point.
                pos = cdp.cpmg_frqs.index(min(cdp.cpmg_frqs))

                # Scaling.
                min_options.append([inc[j], 0.0, average(spin.intensities[pos])])

            # Increment j.
            j = j + 1

        # Set the lower and upper bounds if these are supplied.
        if lower != None:
            for j in xrange(n):
                if lower[j] != None:
                    min_options[j][1] = lower[j]
        if upper != None:
            for j in xrange(n):
                if upper[j] != None:
                    min_options[j][2] = upper[j]

        # Test if the grid is too large.
        grid_size = 1
        for i in xrange(len(min_options)):
            grid_size = grid_size * min_options[i][0]
        if type(grid_size) == long:
            raise RelaxError, "A grid search of size " + `grid_size` + " is too large."

        # Diagonal scaling of minimisation options.
        for j in xrange(len(min_options)):
            min_options[j][1] = min_options[j][1] / scaling_matrix[j, j]
            min_options[j][2] = min_options[j][2] / scaling_matrix[j, j]

        return grid_size, min_options


    def linear_constraints(self, spin=None, scaling_matrix=None):
        """Set up the relaxation dispersion curve fitting linear constraint matrices A and b.

        Standard notation
        =================

        The different constraints are::

            R2 >= 0
            Rex >= 0
            kex >= 0

            R2A >= 0
            kA >= 0
            dw >= 0


        Matrix notation
        ===============

        In the notation A.x >= b, where A is a matrix of coefficients, x is an array of parameter
        values, and b is a vector of scalars, these inequality constraints are::

            | 1  0  0 |     |  R2  |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |  .  |  Rex |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |     |  kex |      |    0    |
            |         |     |      |  >=  |         |
            | 1  0  0 |     |  R2A |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |     |  kA  |      |    0    |
            |         |     |      |      |         |
            | 1  0  0 |     |  dw  |      |    0    |


        @keyword spin:              The spin data container.
        @type spin:                 SpinContainer instance
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        """

        # Initialisation (0..j..m).
        A = []
        b = []
        n = len(spin.params)
        zero_array = zeros(n, float64)
        i = 0
        j = 0

        # Loop over the parameters.
        for k in xrange(len(spin.params)):
            # Relaxation rates and Rex.
            if search('^R', spin.params[k]):
                # R2, Rex, R2A >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Exchange rates.
            elif search('^k', spin.params[k]):
                # kex, kA >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Chemical exchange difference.
            elif spin.params[k] == 'dw':
                # dw >= 0.
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


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Relaxation dispersion curve fitting function.

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

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over the sequence.
        for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Skip spins which have no data.
            if not hasattr(spin, 'intensities'):
                continue

            # Create the initial parameter vector.
            param_vector = self.assemble_param_vector(spin=spin)

            # Diagonal scaling.
            scaling_matrix = self.assemble_scaling_matrix(spin=spin, scaling=scaling)
            if len(scaling_matrix):
                param_vector = dot(inv(scaling_matrix), param_vector)

            # Get the grid search minimisation options.
            if match('^[Gg]rid', min_algor):
                grid_size, min_options = self.grid_search_setup(spin=spin, param_vector=param_vector, lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix)

            # Linear constraints.
            if constraints:
                A, b = self.linear_constraints(spin=spin, scaling_matrix=scaling_matrix)

            # Print out.
            if verbosity >= 1:
                # Get the spin id string.
                spin_id = generate_spin_id(mol_name, res_num, res_name, spin.num, spin.name)

                # Individual spin print out.
                if verbosity >= 2:
                    print "\n\n"

                string = "Fitting to spin " + `spin_id`
                print "\n\n" + string
                print len(string) * '~'

                # Grid search print out.
                if match('^[Gg]rid', min_algor):
                    print "Unconstrained grid search size: " + `grid_size` + " (constraints may decrease this size).\n"


            # Initialise the function to minimise.
            ######################################

            if sim_index == None:
                values = spin.intensities
            else:
                values = spin.sim_intensities[sim_index]

            setup(num_params=len(spin.params), num_times=len(cdp.cpmg_frqs), values=values, sd=spin.intensity_err, cpmg_frqs=cdp.cpmg_frqs, scaling_matrix=scaling_matrix)


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
                lm_error = zeros(len(spin.cpmg_frqs), float64)
                index = 0
                for k in xrange(len(spin.cpmg_frqs)):
                    lm_error[index:index+len(relax_error[k])] = relax_error[k]
                    index = index + len(relax_error[k])

                min_options = min_options + (self.relax_disp.lm_dri, lm_error)


            # Minimisation.
            ###############

            if constraints:
                results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=True, print_flag=verbosity)
            else:
                results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=True, print_flag=verbosity)
            if results == None:
                return
            param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

            # Scaling.
            if scaling:
                param_vector = dot(scaling_matrix, param_vector)

            # Disassemble the parameter vector.
            self.disassemble_param_vector(param_vector=param_vector, spin=spin, sim_index=sim_index)

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


    def model_setup(self, model, params):
        """Update various model specific data structures.

        @param model:   The relaxation dispersion curve type.
        @type model:    str
        @param params:  A list consisting of the model parameters.
        @type params:   list of str
        """

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Set the model.
        cdp.curve_type = model

        # Loop over the sequence.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Initialise the data structures (if needed).
            self.data_init(spin)

            # The model and parameter names.
            spin.model = model
            spin.params = params


    def overfit_deselect(self):
        """Deselect spins which have insufficient data to support minimisation."""

        # Test the sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over spin data.
        for spin in spin_loop():
            # Check if data exists.
            if not hasattr(spin, 'intensities'):
                spin.select = False
                continue

            # Require 3 or more data points.
            if len(spin.intensities) < 3:
                spin.select = False
                continue


    def return_data(self, spin):
        """Function for returning the peak intensity data structure.

        @param spin:    The spin container.
        @type spin:     SpinContainer instance
        @return:        The peak intensity data structure.
        @rtype:         list of float
        """

        return spin.intensities


    return_data_name_doc =  """
        Relaxation dispersion curve fitting data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        _________________________________________________________________________________________________
        |                                                   |                |                          |
        | Data type                                         | Object name    | Patterns                 |
        |___________________________________________________|________________|__________________________|
        |                                                   |                |                          |
        | Transversal relaxation rate                       | 'r2'           | '^[Rr]2$'                |
        |                                                   |                |                          |
        | Chemical exchange contribution to 'R2'            | 'rex'          | '^[Rr]ex$'               |
        |                                                   |                |                          |
        | Exchange rate                                     | 'kex'          | '^[Kk]ex$'               |
        |                                                   |                |                          |
        | Transversal relaxation rate for state A           | 'r2a'          | '^[Rr]2A$'               |
        |                                                   |                |                          |
        | Exchange rate from state A to state B             | 'ka'           | '^[Kk]A$'                |
        |                                                   |                |                          |
        | Chemical shift difference between states A and B  | 'dw'           | '^[Dd]w$'                |
        |                                                   |                |                          |
        | Peak intensities (series)                         | 'intensities'  | '^[Ii]nt$'               |
        |                                                   |                |                          |
        | CPMG pulse train frequency (series)               | 'cpmg_frqs'    | '^[Cc]pmg[ -_][Ff]rqs$'  |
        |___________________________________________________|________________|__________________________|

        """

    def return_data_name(self, name):
        """Return a unique identifying string for the relaxation dispersion curve-fitting parameter.

        @param name:    The relaxation dispersion curve-fitting parameter.
        @type name:     str
        @return:        The unique parameter identifying string.
        @rtype:         str
        """

        # Transversal relaxation rate.
        if match('^[Rr]2$', name):
            return 'r2'

        # Chemical exchange contribution to 'R2'.
        if match('^[Rr]ex$', name):
            return 'rex'

        # Exchange rate.
        if match('^[Kk]ex$', name):
            return 'kex'

        # Transversal relaxation rate for state A.
        if match('^[Rr]2A$', name):
            return 'r2a'

        # Exchange rate from state A to state B.
        if match('^[Kk]A$', name):
            return 'ka'

        # Chemical shift difference between states A and B.
        if match ('^[Dd]w$', name):
            return 'dw'

        # Peak intensities (series)
        if match('^[Ii]nt$', name):
            return 'intensities'

        # CPMG pulse train frequency (series).
        if match('^[Cc]pmg[ -_][Ff]rqs$', name):
            return 'cpmg_frqs'


    def return_error(self, spin_id):
        """Return the standard deviation data structure.

        @param spin_id: The spin identification string, as yielded by the base_data_loop() generator
                        method.
        @type spin_id:  str
        @return:        The standard deviation data structure.
        @rtype:         list of float
        """

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Get the spin container.
        spin = return_spin(spin_id)

        # Return the error list.
        return spin.intensity_err


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # Peak intensities.
        if object_name == 'intensities':
            grace_string = '\\qPeak intensities\\Q'

        # Transversal relaxation rate.
        elif object_name == 'r2':
            grace_string = '\\qR\\s2\\N (s\\S-1\\N)\\Q'

        # Chemical exchange contribution to 'R2'.
        elif object_name == 'rex':
            grace_string = '\\qR\\sex\\N (s\\S-1\\N)\\Q'

        # Exchange rate.
        elif object_name == 'kex':
            grace_string = '\\qk\\sex\\N (s\\S-1\\N)\\Q'

        # Transversal relaxation rate for state A.
        elif object_name == 'r2a':
            grace_string = '\\qR\\s2,A\\N (s\\S-1\\N)\\Q'

        # Exchange rate from state A to state B.
        elif object_name == 'ka':
            grace_string = '\\qk\\sA\\N (s\\S-1\\N)\\Q'

        # Chemical shift difference between states A and B.
        elif object_name == 'dw':
            grace_string = '\\q\\xDw\\f{} (Hz)\\Q'

        # CPMG pulse train frequency
        elif object_name == 'cpmg_frqs':
            grace_string = '\\qCPMG pulse train frequency (Hz)\\Q'

        # Return the Grace string.
        return grace_string


    def return_units(self, stat_type):
        """Dummy function which returns None as the stats have no units."""

        return None


    def select_model(self, model='fast'):
        """Function for selecting the model of the relaxation dispersion curve.

        @keyword model: The relaxation dispersion time scale for curve fitting.  Can be one of
                        'fast' or 'slow'.
        @type model:    str
        """

        # Test if the current pipe exists.
        pipes.test()

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the pipe type is set to 'relax_disp'.
        function_type = cdp.pipe_type
        if function_type != 'relax_disp':
            raise RelaxFuncSetupError, specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the experiment type is set.
        if not hasattr(cdp, 'exp_type'):
            raise RelaxError, "The relaxation dispersion experiment type has not been set."

        # Fast-exchange regime.
        if model == 'fast':
            print "Fast-exchange regime."
            params = ['R2', 'Rex', 'kex']

        # Slow-exchange regime.
        elif model == 'slow':
            print "Slow-exchange regime."
            params = ['R2A', 'kA', 'dw']

        # Invalid model.
        else:
            raise RelaxError, "The model '" + model + "' is invalid."

        # Set up the model.
        self.model_setup(model, params)


    def set_doc(self):
        """
        Relaxation dispersion curve fitting set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        Only three parameters can be set for either the slow- or the fast-exchange regime. For the
        slow-exchange regime, these parameters include the transversal relaxation rate for state A
        (R2A), the exchange rate from state A to state (kA) and the chemical shift difference
        between states A and B (dw). For the fast-exchange regime, these include the transversal
        relaxation rate (R2), the chemical exchange contribution to R2 (Rex) and the exchange rate
        (kex). Setting parameters for a non selected model has no effect.
        """


    def sim_pack_data(self, spin_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param spin_id:     The spin identification string, as yielded by the base_data_loop()
                            generator method.
        @type spin_id:      str
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Get the spin container.
        spin = return_spin(spin_id)

        # Test if the simulation data already exists.
        if hasattr(spin, 'sim_intensities'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        spin.sim_intensities = sim_data
