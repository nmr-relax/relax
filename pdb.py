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

import MMTK
from MMTK.Proteins import Protein
from os import stat
from stat import S_ISREG, ST_MODE


class PDB:
    def __init__(self, relax):
        """Class containing the pdb loading functions."""

        self.relax = relax


    def pdb(self, file):
        """The pdb loading function."""

        # Test if the file exists.
        if not S_ISREG(stat(file)[ST_MODE]):
            raise RelaxFileError, ('PDB', file)

        # Load the file.
        self.relax.data.pdb = MMTK.PDB.PDBConfiguration(file)
        print self.relax.data.pdb

        # Strip the protons.
        self.relax.data.pdb.deleteHydrogens()

        # Create the protein.
        self.relax.data.protein = Protein(self.relax.data.pdb.createPeptideChains())
        print self.relax.data.protein
