###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


from os import F_OK, access, mkdir


class Read:
    def __init__(self, relax):
        """Class containing functions for writing data."""

        self.relax = relax


    def read_data(self, model=None, file=None, dir=None):
        """Function for reading the data out of a file."""

        # Test if the model exists.
        if not self.relax.data.equations.has_key(model):
            print "The model '" + model + "' has not been created yet."
            return

        # Equation type specific function setup.
        fns = self.relax.specific_setup.setup("print", model)
        if fns == None:
            return
        self.print_header, self.print_results = fns

        # The results file.
        file_name = model + "/" + file
        if access(file_name, F_OK) and not force:
            print "The file '" + file_name + "' already exists.  Set the force flag to 1 to overwrite."
            return
        results_file = open(file_name, 'w')

        # Print the header.
        self.print_header(results_file, model)

        # Print the results.
        self.print_results(results_file, model)

        # Close the results file.
        results_file.close()
