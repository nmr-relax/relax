###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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


    def pdb(self, file, model, load_seq):
        """The pdb loading function."""

        # Test if sequence data is loaded.
        if not load_seq and not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the file exists.
        if not access(file, F_OK):
            raise RelaxFileError, ('PDB', file)

        # Load the first structure in the PDB file.
        if model == None:
            print "Loading the first structure from the PDB file."

            # Load the structure into 'str'.
            str = Scientific.IO.PDB.Structure(file)

            # Test the structure.
            if len(str) == 0:
                raise RelaxPdbLoadError, file

            # Place the structure in 'self.relax.data.pdb'.
            self.relax.data.pdb = str


        # Load the structure i from the PDB file.
        elif type(model) == int:
            print "Loading the structure i from the PDB file."

            # Load the structure into 'str'.
            str = Scientific.IO.PDB.Structure(file, model)

            # Test the structure.
            if len(str) == 0:
                raise RelaxPdbLoadError, file

            # Place the structure in 'self.relax.data.pdb'.
            self.relax.data.pdb = str

        # Load all NMR structures.
        elif match('[Aa][Ll][Ll]', model):
            print "Loading all NMR structures from the PDB file."

            # Initialisation.
            self.relax.data.pdb = []
            i = 1

            # Loop over all the other structures.
            while 1:
                # Load the pdb files.
                str = Scientific.IO.PDB.Structure(file, i)

                # Print out.
                print str

                # Test if the last structure has been reached.
                if len(str) == 0:
                    if i == 1:
                        raise RelaxPdbLoadError, file
                    del str
                    break

                # Add the structure to the list of structures in 'self.relax.data.pdb'.
                self.relax.data.pdb.append(str)

                # Increment i.
                i = i + 1

        # Bad model argument.
        else:
            raise RelaxInvalidError, ('model', model)

        # Print the PDB info.
        print self.relax.data.pdb

        # Sequence loading.
        if load_seq and not len(self.relax.data.res):
            self.relax.generic.sequence.load_PDB_sequence()
