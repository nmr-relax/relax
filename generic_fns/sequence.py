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

import sys


class Sequence:
    def __init__(self, relax):
        """Class containing functions specific to amino-acid sequence."""

        self.relax = relax


    def data_names(self):
        """Function for returning a list of names of data structures associated with the sequence."""

        return [ 'res' ]


    def load_PDB_sequence(self, run):
        """Function for loading the sequence out of a PDB file.

        This needs to be modified to handle multiple peptide chains.
        """

        print "Loading the sequence from the PDB file.\n"

        # Reassign the sequence of the first structure.
        if type(self.relax.data.pdb[run]) == list:
            res = self.relax.data.pdb[run][0].peptide_chains[0].residues
        else:
            res = self.relax.data.pdb[run].peptide_chains[0].residues

        # Add the run to 'self.relax.data.res'.
        self.relax.data.res.add_list(run)

        # Loop over the sequence.
        for i in xrange(len(res)):
            # Append a data container.
            self.relax.data.res[run].add_element()

            # Insert the data.
            self.relax.data.res[run][i].num = res[i].number
            self.relax.data.res[run][i].name = res[i].name
            self.relax.data.res[run][i].select = 1


    def read(self, run=None, file_name=None, num_col=0, name_col=1, sep=None, header_lines=None):
        """Function for reading sequence data."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the sequence data has already been read.
        if self.relax.data.res.has_key(run):
            raise RelaxError, "The sequence data has already been loaded."

        # Extract the data from the file.
        file_data = self.relax.file_ops.extract_data(file_name)

        # Remove the header.
        file_data = file_data[header_lines:]

        # Strip data.
        file_data = self.relax.file_ops.strip(file_data)

        # Do nothing if the file does not exist.
        if not file_data:
            raise RelaxFileEmptyError

        # Test if the sequence data is valid.
        for i in xrange(len(file_data)):
            try:
                int(file_data[i][num_col])
            except ValueError:
                raise RelaxError, "Sequence data is invalid."

        # Add the run to 'self.relax.data.res'.
        self.relax.data.res.add_list(run)

        # Fill the array 'self.relax.data.res[run]' with data containers and place sequence data into the array.
        for i in xrange(len(file_data)):
            # Append a data container.
            self.relax.data.res[run].add_element()

            # Insert the data.
            self.relax.data.res[run][i].num = int(file_data[i][num_col])
            self.relax.data.res[run][i].name = file_data[i][name_col]
            self.relax.data.res[run][i].select = 1
