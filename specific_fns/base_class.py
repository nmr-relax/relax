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


class Common_functions:
    def __init__(self):
        """Base class containing functions common to the specific functions."""


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
            else:
                value = None

            # Get the error.
            if hasattr(data, object_error):
                error = getattr(data, object_error)
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
            setattr(self.relax.data.res[self.run][index], object_name, float(value) * scaling)

            # Set the error.
            if error != None:
                setattr(self.relax.data.res[self.run][index], object_name+'_error', float(error))


    def sim_pack_data(self, run, i, sim_data):
        """Function for packing Monte Carlo simulation data."""

        # Test if the simulation data already exists.
        if hasattr(self.relax.data.res[run][i], 'relax_sim_data'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        self.relax.data.res[run][i].relax_sim_data = sim_data
