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

from os import stat
from re import match
import Scientific
from stat import S_ISREG, ST_MODE
from sys import exc_info


class PDB:
    def __init__(self, relax):
        """Class containing the pdb loading functions."""

        self.relax = relax


    def pdb(self, file):
        """The pdb loading function."""

        # Test if the file exists.
        if not S_ISREG(stat(file)[ST_MODE]):
            raise RelaxFileError, ('PDB', file)

        # Initialisation.
        print "Loading the PDB file into 'self.relax.data.pdb'."
        self.relax.data.pdb = []
        i = 1

        # Loop over all models.
        while 1:
            # Load the pdb files.
            str = Scientific.IO.PDB.Structure(file, i)

            # Test if the last structure has been reached.
            if len(str) == 0:
                del str
                break

            # Add the structure to the list of structures in self.relax.data.pdb
            self.relax.data.pdb.append(str)

            # Print out.
            print self.relax.data.pdb[i-1]

            # Increment i.
            i = i + 1
