###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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

#from maths_fns.mapping import Mapping


class Jw_mapping:
    def __init__(self, relax):
        """Class containing functions specific to reduced spectral density mapping."""

        self.relax = relax


    def calculate(self, run=None, print_flag=1):
        """Calculation of the spectral density values."""

        # Run argument.
        self.run = run

        # Test if the frequency has been set.
        if not hasattr(self.relax.data, 'jw_frq') or not self.relax.data.jw_frq.has_key(self.run) or type(self.relax.data.jw_frq[self.run]) != float:
            raise RelaxError, "The frequency for the run " + `self.run` + " has not been set up."

        # Test if the nucleus type has been set.
        if not hasattr(self.relax.data, 'gx'):
            raise RelaxNucleusError

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if the CSA and bond length values have been set.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # CSA value.
            if not hasattr(self.relax.data.res[self.run][i], 'csa') or self.relax.data.res[self.run][i].csa == None:
                raise RelaxNoValueError, "CSA"

            # Bond length value.
            if not hasattr(self.relax.data.res[self.run][i], 'r') or self.relax.data.res[self.run][i].r == None:
                raise RelaxNoValueError, "bond length"


        # Reduced spectral density mapping.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            res = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not res.select:
                continue


    def return_value(self, run, i, data_type):
        """Function for returning the value and error corresponding to 'data_type'."""

        # Arguments.
        self.run = run

        # Get the object.
        object_name = self.get_data_name(data_type)
        if not object_name:
            raise RelaxError, "The model-free data type " + `data_type` + " does not exist."
        object_error = object_name + "_err"

        # Get the value.
        if hasattr(self.relax.data.res[self.run][i], object_name):
            value = getattr(self.relax.data.res[self.run][i], object_name)
        else:
            value = None

        # Get the error.
        if hasattr(self.relax.data.res[self.run][i], object_error):
            error = getattr(self.relax.data.res[self.run][i], object_error)
        else:
            error = None

        # Return the data.
        return value, error



    def set_frq(self, run=None, frq=None):
        """Function for selecting which relaxation data to use in the J(w) mapping."""

        # Run argument.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the frequency has been set.
        if hasattr(self.relax.data, 'jw_frq') and self.relax.data.jw_frq.has_key(self.run):
            raise RelaxError, "The frequency for the run " + `self.run` + " has already been set."

        # Create the data structure if it doesn't exist.
        if not hasattr(self.relax.data, 'jw_frq'):
            self.relax.data.jw_frq = {}

        # Set the frequency.
        self.relax.data.jw_frq[self.run] = frq
