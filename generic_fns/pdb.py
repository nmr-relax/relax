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

from os import F_OK, access, stat
from re import match
import Scientific
import Scientific.IO.PDB
from sys import exc_info


class PDB:
    def __init__(self, relax):
        """Class containing the pdb loading functions."""

        self.relax = relax


    def pdb(self, run=None, file=None, dir=None, model=None, first_model=1, load_seq=1):
        """The pdb loading function."""

        # Arguments.
        self.run = run
        self.file = file
        self.dir = dir
        self.model = model
        self.first_model = first_model
        self.load_seq = load_seq

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if sequence data is loaded.
        if not self.load_seq and not len(self.relax.data.res[self.run]):
            raise RelaxNoSequenceError, self.run

        # The file path.
        self.file_path = self.file
        if self.dir:
            self.file_path = dir + '/' + self.file_path

        # Test if the file exists.
        if not access(self.file_path, F_OK):
            raise RelaxFileError, ('PDB', self.file_path)

        # Load the structures.
        self.load_structures()

        # Model.
        if type(self.relax.data.pdb[self.run]) != list:
            self.relax.data.pdb[self.run].user_model = self.model

        # Sequence loading.
        if self.load_seq and not self.relax.data.res.has_key(self.run):
            self.relax.generic.sequence.load_PDB_sequence(self.run)

        # Load into Molmol (if running).
        self.relax.generic.molmol.open_pdb(self.run)


    def load_structures(self):
        """Function for loading the structures from the PDB file."""

        # Load the structure i from the PDB file.
        if type(self.model) == int:
            print "Loading structure " + `self.model` + " from the PDB file."

            # Load the structure into 'str'.
            str = Scientific.IO.PDB.Structure(self.file_path, self.model)

            # Test the structure.
            if len(str) == 0:
                raise RelaxPdbLoadError, self.file_path

            # Print the PDB info.
            print str

            # Place the structure in 'self.relax.data.pdb[self.run]'.
            self.relax.data.pdb[self.run] = str


        # Load all structures.
        else:
            print "Loading all structures from the PDB file."

            # Initialisation.
            pdb_array = []
            i = self.first_model

            # Loop over all the other structures.
            while 1:
                # Load the pdb files.
                str = Scientific.IO.PDB.Structure(self.file_path, i)

                # Test if the last structure has been reached.
                if len(str) == 0:
                    if i == self.first_model:
                        raise RelaxPdbLoadError, self.file_path
                    del str
                    break

                # Print the PDB info.
                print str

                # Append the structure.
                pdb_array.append(str)

                # Increment i.
                i = i + 1

            # Single structure.
            if len(pdb_array) == 1:
                self.relax.data.pdb[self.run] = pdb_array[0]

            # Multiple structures.
            else:
                self.relax.data.pdb[self.run] = pdb_array
