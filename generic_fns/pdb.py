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


    def pdb(self, run, file, model, load_seq):
        """The pdb loading function."""

        # Arguments.
        self.run = run
        self.file = file
        self.model = model
        self.load_seq = load_seq

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if sequence data is loaded.
        if not self.load_seq and not len(self.relax.data.res[self.run]):
            raise RelaxNoSequenceError

        # Test if the file exists.
        if not access(self.file, F_OK):
            raise RelaxFileError, ('PDB', self.file)

        # Load the structures.
        self.load_structures()

        # Print the PDB info.
        print self.relax.data.pdb[self.run]

        # Sequence loading.
        if self.load_seq and not self.relax.data.res.has_key(self.run):
            self.relax.generic.sequence.load_PDB_sequence(self.run)

        # Load into Molmol (if running).
        self.relax.generic.molmol.open_pdb(self.run)


    def load_structures(self):
        """Function for loading the structures from the PDB file."""

        # Load the first structure in the PDB file.
        if self.model == None:
            print "Loading the first structure from the PDB file."

            # Load the structure into 'str'.
            str = Scientific.IO.PDB.Structure(self.file)

            # Test the structure.
            if len(str) == 0:
                raise RelaxPdbLoadError, self.file

            # Place the structure in 'self.relax.data.pdb[self.run]'.
            self.relax.data.pdb[self.run] = str


        # Load the structure i from the PDB file.
        elif type(self.model) == int:
            print "Loading the structure i from the PDB file."

            # Load the structure into 'str'.
            str = Scientific.IO.PDB.Structure(self.file, self.model)

            # Test the structure.
            if len(str) == 0:
                raise RelaxPdbLoadError, self.file

            # Place the structure in 'self.relax.data.pdb[self.run]'.
            self.relax.data.pdb[self.run] = str

        # Load all NMR structures.
        elif match('[Aa][Ll][Ll]', self.model):
            print "Loading all NMR structures from the PDB file."

            # Initialisation.
            self.relax.data.pdb[self.run] = []
            i = 1

            # Loop over all the other structures.
            while 1:
                # Load the pdb files.
                str = Scientific.IO.PDB.Structure(self.file, i)

                # Print out.
                print str

                # Test if the last structure has been reached.
                if len(str) == 0:
                    if i == 1:
                        raise RelaxPdbLoadError, self.file
                    del str
                    break

                # Add the structure to the list of structures in 'self.relax.data.pdb[self.run]'.
                self.relax.data.pdb[self.run].append(str)

                # Increment i.
                i = i + 1

        # Bad model argument.
        else:
            raise RelaxInvalidError, ('model', self.model)
