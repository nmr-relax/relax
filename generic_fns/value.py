###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


from re import compile, match


class Value:
    def __init__(self, relax):
        """Class containing functions for the setting up of data structures."""

        self.relax = relax


    def set(self, run=None, value=None, data_type=None, res_num=None, res_name=None):
        """Function for setting residue specific data values."""

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the residue number is a valid regular expression.
        if type(res_num) == str:
            try:
                compile(res_num)
            except:
                raise RelaxRegExpError, ('residue number', res_num)

        # Test if the residue name is a valid regular expression.
        if res_name:
            try:
                compile(res_name)
            except:
                raise RelaxRegExpError, ('residue name', res_name)

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific set function.
        set = self.relax.specific_setup.setup('set', function_type)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Residue skipping.
            ###################

            # Skip unselected residues.
            if not self.relax.data.res[run][i].select:
                continue

            # If 'res_num' is not None, skip the residue if there is no match.
            if type(res_num) == int and not self.relax.data.res[run][i].num == res_num:
                continue
            elif type(res_num) == str and not match(res_num, `self.relax.data.res[run][i].num`):
                continue

            # If 'res_name' is not None, skip the residue if there is no match.
            if res_name != None and not match(res_name, self.relax.data.res[run][i].name):
                continue


            # Go to the specific code.
            ##########################

            # Setting the model parameters prior to minimisation.
            if data_type == None:
                set(run=run, value=value, data_type=data_type, index=i)

            # Single data type.
            if type(data_type) == str:
                set(run=run, value=value, data_type=data_type, index=i)

            # Multiple data type.
            if type(data_type) == list:
                for j in range(len(data_type)):
                    # Get the value of the data type 'j'.
                    if type(value) == None:
                        val = None
                    elif type(value) == list:
                        val = value[j]
                    else:
                        val = value

                    # Set the value of data type 'j' to 'val'.
                    set(run=run, value=val, data_type=data_type[j], index=i)


            # Reset the minimisation statistics.
            ####################################

            # Chi-squared.
            if hasattr(self.relax.data.res[run][i], 'chi2'):
                self.relax.data.res[run][i].chi2 = None

            # Iteration count.
            if hasattr(self.relax.data.res[run][i], 'iter'):
                self.relax.data.res[run][i].iter = None

            # Function count.
            if hasattr(self.relax.data.res[run][i], 'f_count'):
                self.relax.data.res[run][i].f_count = None

            # Gradient count.
            if hasattr(self.relax.data.res[run][i], 'g_count'):
                self.relax.data.res[run][i].g_count = None

            # Hessian count.
            if hasattr(self.relax.data.res[run][i], 'h_count'):
                self.relax.data.res[run][i].h_count = None

            # Warning.
            if hasattr(self.relax.data.res[run][i], 'warning'):
                self.relax.data.res[run][i].warning = None
