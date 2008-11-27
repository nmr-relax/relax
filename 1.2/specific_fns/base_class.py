###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006 Edward d'Auvergne                                  #
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

from copy import deepcopy


class Common_functions:
    def __init__(self):
        """Base class containing functions common to the specific functions."""


    def has_errors(self):
        """Function for testing if errors exist for the run."""

        # Diffusion tensor errors.
        if self.relax.data.diff.has_key(self.run):
            for object_name in dir(self.relax.data.diff[self.run]):
                # The object error name.
                object_error = object_name + '_err'

                # Error exists.
                if hasattr(self.relax.data.diff[self.run], object_error):
                    return 1

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            data = self.relax.data.res[self.run][i]

            # Parameter errors.
            for object_name in dir(data):
                # The object error name.
                object_error = object_name + '_err'

                # Error exists.
                if hasattr(data, object_error):
                    return 1

        # No errors found.
        return 0


    def return_data(self, run, i):
        """Function for returning the Ri data structure."""

        return self.relax.data.res[run][i].relax_data


    def return_error(self, run, i):
        """Function for returning the Ri error structure."""

        return self.relax.data.res[run][i].relax_error


    def return_value(self, run, i, param, sim=None):
        """Function for returning the value and error corresponding to 'param'.

        If sim is set to an integer, return the value of the simulation and None.
        """

        # Arguments.
        self.run = run

        # Get the object name.
        object_name = self.return_data_name(param)

        # The data type does not exist.
        if not object_name:
            raise RelaxError, "The parameter " + `param` + " does not exist."

        # The error and simulation names.
        object_error = object_name + '_err'
        object_sim = object_name + '_sim'

        # Alias the residue specific data structure.
        data = self.relax.data.res[self.run][i]

        # Value and error.
        if sim == None:
            # Get the value.
            if hasattr(data, object_name):
                value = getattr(data, object_name)
            elif hasattr(self.relax.data, object_name):
                object = getattr(self.relax.data, object_name)
                value = object[self.run]
            else:
                value = None

            # Get the error.
            if hasattr(data, object_error):
                error = getattr(data, object_error)
            elif hasattr(self.relax.data, object_error):
                object = getattr(self.relax.data, object_error)
                error = object[self.run]
            else:
                error = None

            # Return the data.
            return value, error

        # Simulation value.
        else:
            # Get the value.
            if hasattr(data, object_sim):
                object = getattr(data, object_sim)
                value = object[sim]
            elif hasattr(self.relax.dat, object_sim):
                object = getattr(self.relax.dat, object_sim)
                value = object[self.run][sim]
            else:
                value = None

            # Return the data.
            return value, None


    def set(self, run=None, value=None, error=None, param=None, scaling=1.0, index=None):
        """Common function for setting parameter values."""

        # Arguments.
        self.run = run

        # Setting the model parameters prior to minimisation.
        #####################################################

        if param == None:
            # The values are supplied by the user:
            if value:
                # Test if the length of the value array is equal to the length of the parameter array.
                if len(value) != len(self.relax.data.res[self.run][index].params):
                    raise RelaxError, "The length of " + `len(value)` + " of the value array must be equal to the length of the parameter array, " + `self.relax.data.res[self.run][index].params` + ", for residue " + `self.relax.data.res[self.run][index].num` + " " + self.relax.data.res[self.run][index].name + "."

            # Default values.
            else:
                # Set 'value' to an empty array.
                value = []

                # Loop over the parameters.
                for i in xrange(len(self.relax.data.res[self.run][index].params)):
                    value.append(self.default_value(self.relax.data.res[self.run][index].params[i]))

            # Loop over the parameters.
            for i in xrange(len(self.relax.data.res[self.run][index].params)):
                # Get the object.
                object_name = self.return_data_name(self.relax.data.res[self.run][index].params[i])
                if not object_name:
                    raise RelaxError, "The data type " + `self.relax.data.res[self.run][index].params[i]` + " does not exist."

                # Initialise all data if it doesn't exist.
                if not hasattr(self.relax.data.res[self.run][index], object_name):
                    self.data_init(self.relax.data.res[self.run][index])

                # Set the value.
                if value[i] == None:
                    setattr(self.relax.data.res[self.run][index], object_name, None)
                else:
                    setattr(self.relax.data.res[self.run][index], object_name, float(value[i]) * scaling)


        # Individual data type.
        #######################

        else:
            # Get the object.
            object_name = self.return_data_name(param)
            if not object_name:
                raise RelaxError, "The data type " + `param` + " does not exist."

            # Initialise all data if it doesn't exist.
            if not hasattr(self.relax.data.res[self.run][index], object_name):
                self.data_init(self.relax.data.res[self.run][index])

            # Default value.
            if value == None:
                value = self.default_value(object_name)

            # Set the value.
            if value == None:
                setattr(self.relax.data.res[self.run][index], object_name, None)
            else:
                setattr(self.relax.data.res[self.run][index], object_name, float(value) * scaling)

            # Set the error.
            if error != None:
                setattr(self.relax.data.res[self.run][index], object_name+'_err', float(error) * scaling)

            # Update the other parameters if necessary.
            self.set_update(run=run, param=param, index=index)


    def set_error(self, run, instance, index, error):
        """Function for setting parameter errors."""

        # Arguments.
        self.run = run

        # Skip unselected residues.
        if not self.relax.data.res[self.run][instance].select:
            return

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                setattr(self.relax.data.res[self.run][instance], param + "_err", error)

            # Increment.
            inc = inc + 1


    def set_update(self, run, param, index):
        """Dummy function to do nothing!"""

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
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # Loop over all the parameter names.
            for object_name in param_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(self.relax.data.res[self.run][i], sim_object_name):
                    raise RelaxError, "Monte Carlo parameter values have already been set."


        # Set the Monte Carlo parameter values.
        #######################################

        # Loop over the residues.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # Loop over all the data names.
            for object_name in param_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(self.relax.data.res[self.run][i], sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(self.relax.data.res[self.run][i], sim_object_name)

                # Loop over the simulations.
                for j in xrange(self.relax.data.sim_number[self.run]):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(self.relax.data.res[self.run][i], object_name)))

            # Loop over all the minimisation object names.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(self.relax.data.res[self.run][i], sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(self.relax.data.res[self.run][i], sim_object_name)

                # Loop over the simulations.
                for j in xrange(self.relax.data.sim_number[self.run]):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(self.relax.data.res[self.run][i], object_name)))


    def sim_return_param(self, run, instance, index):
        """Function for returning the array of simulation parameter values."""

        # Arguments.
        self.run = run

        # Skip unselected residues.
        if not self.relax.data.res[self.run][instance].select:
            return

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                return getattr(self.relax.data.res[self.run][instance], param + "_sim")

            # Increment.
            inc = inc + 1


    def sim_return_selected(self, run, index):
        """Function for returning the array of selected simulation flags."""

        # Arguments.
        self.run = run

        # Return the array.
        return self.relax.data.res[self.run][index].select_sim
