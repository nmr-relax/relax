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
from generic_fns.selection import spin_loop
from relax_errors import RelaxError, RelaxParamSetError



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
        @return type:   tuple of length 2 of floats or None
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


    def set(self, value=None, error=None, param=None, scaling=1.0, spin=None):
        """Common function for setting parameter values.

        @param value:   The value to change the parameter to.
        @type value:    float or str
        @param error:   The error value associated with the parameter, also to be set.
        @type error:    float or str
        @param param:   The name of the parameter to change.
        @type param:    str
        @param scaling: The scaling factor for the value or error parameters.
        @type scaling:  float
        @param spin:    The SpinContainer object.
        @type spin:     SpinContainer
        """

        # Setting the model parameters prior to minimisation.
        #####################################################

        if param == None:
            # The values are supplied by the user:
            if value:
                # Test if the length of the value array is equal to the length of the parameter array.
                if len(value) != len(spin.params):
                    raise RelaxError, "The length of " + `len(value)` + " of the value array must be equal to the length of the parameter array, " + `spin.params` + ", for residue " + `spin.num` + " " + spin.name + "."

            # Default values.
            else:
                # Set 'value' to an empty array.
                value = []

                # Loop over the parameters.
                for i in xrange(len(spin.params)):
                    value.append(self.default_value(spin.params[i]))

            # Loop over the parameters.
            for i in xrange(len(spin.params)):
                # Get the object.
                object_name = self.return_data_name(spin.params[i])
                if not object_name:
                    raise RelaxError, "The data type " + `spin.params[i]` + " does not exist."

                # Initialise all data if it doesn't exist.
                if not hasattr(spin, object_name):
                    self.data_init(spin)

                # Set the value.
                if value[i] == None:
                    setattr(spin, object_name, None)
                else:
                    # Catch parameters with string values.
                    try:
                        value[i] = float(value[i]) * scaling
                    except ValueError:
                        pass

                    # Set the attribute.
                    setattr(spin, object_name, value[i])


        # Individual data type.
        #######################

        else:
            # Get the object.
            object_name = self.return_data_name(param)
            if not object_name:
                raise RelaxError, "The data type " + `param` + " does not exist."

            # Initialise all data if it doesn't exist.
            if not hasattr(spin, object_name):
                self.data_init(spin)

            # Default value.
            if value == None:
                value = self.default_value(object_name)

            # No default value, hence the parameter cannot be set.
            if value == None:
                raise RelaxParamSetError, param

            # Set the value.
            if value == None:
                setattr(spin, object_name, None)
            else:
                # Catch parameters with string values.
                try:
                    value = float(value) * scaling
                except ValueError:
                    pass

                # Set the attribute.
                setattr(spin, object_name, value)

            # Set the error.
            if error != None:
                # Catch parameters with string values.
                try:
                    error = float(error) * scaling
                except ValueError:
                    pass

                # Set the attribute.
                setattr(spin, object_name+'_err', error)

            # Update the other parameters if necessary.
            self.set_update(param=param, spin=spin)


    def set_error(self, run, instance, index, error):
        """Function for setting parameter errors."""

        # Arguments.
        self.run = run

        # Skip unselected residues.
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

        # Loop over the residues.
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


    def sim_return_param(self, run, instance, index):
        """Function for returning the array of simulation parameter values."""

        # Arguments.
        self.run = run

        # Skip unselected residues.
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
