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


class Write:
    def __init__(self, relax):
        """Class containing functions for writing data."""

        self.relax = relax


    def write_data(self, run=None, file="results", force=0):
        """Create the directories and files for output.

        The directory with the name of the run will be created.  The results will be placed in the
        file 'results' in the run directory.
        """

        # Test if the run exists.
        if not run in self.relax.data.runs:
            print "The run '" + run + "' has not been created yet."
            return

        # Directory creation.
        try:
            mkdir(run)
        except OSError:
            pass

        # Equation type specific function setup.
        fns = self.relax.specific_setup.setup("print", self.relax.data.res[0].equations[run])
        if fns == None:
            return
        self.print_header, self.print_results = fns

        # The results file.
        file_name = run + "/" + file
        if access(file_name, F_OK) and not force:
            print "The file '" + file_name + "' already exists.  Set the force flag to 1 to overwrite."
            return
        results_file = open(file_name, 'w')

        # Print the header.
        self.print_header(results_file)

        # Print the results.
        self.print_results(results_file, run)

        # Close the results file.
        results_file.close()
