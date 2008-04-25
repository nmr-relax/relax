###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006-2008 Edward d'Auvergne                             #
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

# relax module imports.
from data import Data as relax_data_store
from generic_fns.selection import count_spins, exists_mol_res_spin_data, spin_loop
from relax_errors import RelaxError



class Common_functions:
    """Base class containing simple methods used by some a number of the specific analysis types."""

    def has_errors(self):
        """Function for testing if errors exist for the run.

        @return:    The answer to the question of whether errors exist.
        @rtype:     bool
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Diffusion tensor errors.
        if hasattr(cdp, 'diff'):
            for object_name in dir(cdp.diff):
                # The object error name.
                object_error = object_name + '_err'

                # Error exists.
                if hasattr(cdp.diff, object_error):
                    return True

        # Loop over the sequence.
        for spin in spin_loop():
            # Parameter errors.
            for object_name in dir(spin):
                # The object error name.
                object_error = object_name + '_err'

                # Error exists.
                if hasattr(spin, object_error):
                    return True

        # No errors found.
        return False


    def is_spin_param(self, name):
        """Determine whether the given parameter is spin specific.

        This base class method always returns true, hence all parameters will be considered
        residents of a SpinContainer object unless this method is overwritten.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        True
        @rtype:         bool
        """

        # Return the default of True.
        return True


    def num_instances(self):
        """Function for returning the number of instances.

        The default in this base class is to return the number of spins.

        @return:    The number of instances (equal to the number of spins).
        @rtype:     int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Return the number of spins.
        return count_spins()


    def overfit_deselect(self):
        """Dummy function, nornally for deselecting spins with insufficient data for minimisation."""


    def return_conversion_factor(self, stat_type):
        """Dummy function for returning 1.0."""

        return 1.0


    def return_data(self, spin):
        """Function for returning the Ri data structure for the given spin.

        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer instance
        @return:        The array of relaxation data values.
        @rtype:         list of float
        """

        return spin.relax_data


    def return_error(self, spin):
        """Function for returning the Ri error structure for the given spin.

        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer instance
        @return:        The array of relaxation data error values.
        @rtype:         list of float
        """

        return spin.relax_error


    def return_value(self, spin, param, sim=None):
        """Return the value and error corresponding to the parameter 'param'.

        If sim is set to an integer, return the value of the simulation and None.  The values are
        taken from the given SpinContainer object.


        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        @param param:   The name of the parameter to return values for.
        @type param:    str
        @param sim:     The Monte Carlo simulation index.
        @type sim:      None or int
        @return:        The value and error corresponding to 
        @rtype:         tuple of length 2 of floats or None
        """

        # Get the object name.
        object_name = self.return_data_name(param)

        # The data type does not exist.
        if not object_name:
            raise RelaxError, "The parameter " + `param` + " does not exist."

        # The error and simulation names.
        object_error = object_name + '_err'
        object_sim = object_name + '_sim'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Initial values.
        value = None
        error = None

        # Value and error.
        if sim == None:
            # Get the value.
            if hasattr(spin, object_name):
                value = getattr(spin, object_name)
            elif hasattr(cdp, object_name):
                value = getattr(cdp, object_name)

            # Get the error.
            if hasattr(spin, object_error):
                error = getattr(spin, object_error)
            elif hasattr(cdp, object_error):
                error = getattr(cdp, object_error)

        # Simulation value.
        else:
            # Get the value.
            if hasattr(spin, object_sim):
                object = getattr(spin, object_sim)
                value = object[sim]
            elif hasattr(cdp, object_sim):
                object = getattr(cdp, object_sim)
                value = object[sim]

        # Return the data.
        return value, error


    def set_error(self, run, instance, index, error):
        """Function for setting parameter errors."""

        # Arguments.
        self.run = run

        # Skip deselected residues.
        if not relax_data_store.res[self.run][instance].select:
            return

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                setattr(relax_data_store.res[self.run][instance], param + "_err", error)

            # Increment.
            inc = inc + 1


    def set_non_spin_params(self, value=None, param=None):
        """Base class method which complains loudly if anything is supplied to it.

        @param value:   The parameter values.
        @type value:    None, number, or list of numbers
        @param param:   The parameter names.
        @type param:    None, str, or list of str
        """

        # Throw a RelaxError.
        if value or param:
            raise RelaxError, "Do not know how to handle the non-spin specific parameters " + `param` + " with the values " + `value`


    def set_update(self, param, spin):
        """Dummy function to do nothing!

        @param param:   The name of the parameter which has been changed.
        @type param:    str
        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        """

        return


    def sim_init_values(self, run):
        """Function for initialising Monte Carlo parameter values."""

        # Arguments.
        self.run = run

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Loop over the residues.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Skip deselected residues.
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

        # Loop over the residues.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Skip deselected residues.
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


    def sim_return_param(self, run, instance, index):
        """Function for returning the array of simulation parameter values."""

        # Arguments.
        self.run = run

        # Skip deselected residues.
        if not relax_data_store.res[self.run][instance].select:
            return

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                return getattr(relax_data_store.res[self.run][instance], param + "_sim")

            # Increment.
            inc = inc + 1


    def sim_return_selected(self, spin):
        """Function for returning the array of selected simulation flags for the given spin.

        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer instance
        @return:        The array of selected simulation flags.
        @rtype:         list of int
        """

        # Return the array.
        return spin.select_sim


    def test_grid_ops(self, lower=None, upper=None, inc=None, n=None):
        """Function for testing that the grid search options are reasonable.

        @param lower:       The lower bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type lower:        array of numbers
        @param upper:       The upper bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type upper:        array of numbers
        @param inc:         The increments for each dimension of the space for the grid search.  The
                            number of elements in the array must equal to the number of parameters
                            in the model.
        @type inc:          array of int
        @param n:           The number of parameters in the model.
        @type n:            int
        """

        # Lower bounds test.
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
