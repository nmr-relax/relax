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

from re import match

from base_class import Common_functions
from maths_fns.jw_mapping import Jw_mapping


class Jw_mapping(Common_functions):
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

        # Frequency index.
        if self.relax.data.jw_frq[self.run] not in self.relax.data.num_frq[self.run]:
            raise RelaxError, "No relaxation data corresponding to the frequency " + `self.relax.data.jw_frq[self.run]` + " has been loaded."
 
        # Reduced spectral density mapping.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            res = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not res.select:
                continue

            # Frequency index.
            frq_index = None
            for j in xrange(res.num_frq):
                if res.frq[j] == self.relax.data.jw_frq[self.run]:
                    frq_index = j
            if frq_index == None:
                continue
            
            # Get the R1 value corresponding to the set frequency.


    def data_init(self, name):
        """Function for returning an initial data structure corresponding to 'name'."""

        return None


    def data_names(self):
        """Function for returning a list of names of data structures.

        Description
        ~~~~~~~~~~~

        r:  Bond length.

        csa:  CSA value.

        j0:  Spectral density value at 0 MHz.

        jwx:  Spectral density value at the frequency of the heteronucleus.

        jwh:  Spectral density value at the frequency of the heteronucleus.
        """

        # Initialise.
        names = []

        # Values.
        names.append('r')
        names.append('csa')

        # Spectral density values.
        names.append('j0')
        names.append('jwx')
        names.append('jwh')

        return names


    def default_value(self, param):
        """
        Reduced spectral density mapping default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        _______________________________________________________________________________________
        |                                       |              |                              |
        | Data type                             | Object name  | Value                        |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Bond length                           | r            | 1.02 * 1e-10                 |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | CSA                                   | csa          | -170 * 1e-6                  |
        |_______________________________________|______________|______________________________|

        """

        # Bond length.
        if param == 'r':
            return 1.02 * 1e-10

        # CSA.
        if param == 'CSA':
            return -170 * 1e-6


    def get_data_name(self, name):
        """
        Reduced spectral density mapping data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Bond length            | r            | '^r$' or '[Bb]ond[ -_][Ll]ength'                 |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | CSA                    | csa          | '^[Cc][Ss][Aa]$'                                 |
        |________________________|______________|__________________________________________________|

        """

        # Bond length.
        if match('^r$', name) or match('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if match('^[Cc][Ss][Aa]$', name):
            return 'csa'


    def return_value(self, run, i, data_type):
        """Function for returning the value and error corresponding to 'data_type'."""

        # Arguments.
        self.run = run

        # Get the object.
        object_name = self.get_data_name(data_type)
        if not object_name:
            raise RelaxError, "The reduced spectral density mapping data type " + `data_type` + " does not exist."
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


    def set(self, run=None, value=None, error=None, data_type=None, index=None):
        """
        Reduced spectral density mapping set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        In reduced spectral density mapping, only two values can be set, the bond length and CSA
        value.  These must be set prior to the calculation of spectral density values.

        """

        # Arguments.
        self.run = run

        # Setting the model parameters prior to calculation.
        ####################################################

        if data_type == None:
            # The values are supplied by the user:
            if value:
                # Test if the length of the value array is equal to 2.
                if len(value) != 2:
                    raise RelaxError, "The length of " + `len(value)` + " of the value array must be equal to two."

            # Default values.
            else:
                # Set 'value' to an empty array.
                value = []

                # CSA and Bond length.
                value.append(self.default_value('csa'))
                value.append(self.default_value('r'))

            # Initilise data.
            if not hasattr(self.relax.data.res[self.run][index], 'csa') or not hasattr(self.relax.data.res[self.run][index], 'csa'):
                self.initialise_data(self.relax.data.res[self.run][index], self.run)

            # CSA and Bond length.
            setattr(self.relax.data.res[self.run][index], 'csa', float(value[0]))
            setattr(self.relax.data.res[self.run][index], 'r', float(value[1]))


        # Individual data type.
        #######################

        else:
            # Get the object.
            object_name = self.get_data_name(data_type)
            if not object_name:
                raise RelaxError, "The reduced spectral density mapping data type " + `data_type` + " does not exist."

            # Initialise all data if it doesn't exist.
            if not hasattr(self.relax.data.res[self.run][index], object_name):
                self.initialise_data(self.relax.data.res[self.run][index], self.run)

            # Default value.
            if value == None:
                value = self.default_value(object_name)

            # Set the value.
            setattr(self.relax.data.res[self.run][index], object_name, float(value))

            # Set the error.
            if error != None:
                setattr(self.relax.data.res[self.run][index], object_name+'_error', float(error))


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
