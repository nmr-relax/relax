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


from os import F_OK, access, mkdir


class RW:
    def __init__(self, relax):
        """Class containing functions for reading and writing data."""

        self.relax = relax


    def read_results(self, run=None, data_type=None, file='results', dir=None):
        """Function for reading the data out of a file."""

        # Test if the sequence data has been read.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Equation type specific function setup.
        self.read_function = self.relax.specific_setup.setup('read', data_type)
        if self.read_function == None:
            raise RelaxFuncSetupError, ('read', data_type)

        # The results file.
        if dir == None:
            dir = run
        file_name = dir + '/' + file
        if not access(file_name, F_OK):
            raise RelaxFileError, ('relaxation data', file_name)

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file_name)

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Read the results.
        self.read_function(file_data, run)


    def write_results(self, run=None, file="results", dir=None, force=0):
        """Create the directories and files for output.

        The directory with the name of the run will be created.  The results will be placed in the
        file 'results' in the run directory.
        """

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Directory creation.
        if dir == None:
            dir = run
        try:
            mkdir(dir)
        except OSError:
            pass

        # Determine the equation type.
        equation = self.relax.specific_setup.get_equation(run)

        # Equation type specific header writing function setup.
        self.write_header = self.relax.specific_setup.setup('write_header', equation)
        if self.write_header == None:
            raise RelaxFuncSetupError, ('write_header', res.equations[run])

        # Equation type specific function setup.
        self.write_function = self.relax.specific_setup.setup('write_results', equation)
        if self.write_function == None:
            raise RelaxFuncSetupError, ('write_results', res.equations[run])

        # The results file.
        file_name = dir + '/' + file
        if access(file_name, F_OK) and not force:
            raise RelaxFileOverwriteError, (file_name, 'force flag')
        results_file = open(file_name, 'w')

        # Write the header.
        self.write_header(results_file, run)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Reassign data structure.
            res = self.relax.data.res[i]

            # Skip unselected residues.
            if not res.select:
                continue

            # Write the results.
            self.write_function(results_file, run, i)

        # Close the results file.
        results_file.close()
