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
from os import stat
from re import match
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

        # Load the file.
        print "Loading the PDB file into 'self.relax.data.pdb'."
        self.relax.data.pdb = MMTK.PDB.PDBConfiguration(file)
        print self.relax.data.pdb

        # Strip the protons from the peptide chains.
        for object in self.relax.data.pdb.objects:
            if hasattr(object, 'createPeptideChain'):
                object.deleteHydrogens()

        # Create an empty collection of molecules.
        self.relax.data.molecs = MMTK.Collection()
        print "Creating an empty collection of molecules:  " + `self.relax.data.molecs.objects`

        # Try to place the proteins in the collection of molecules.
        print "\nPlacing the proteins into the collection of molecules."
        try:
            self.relax.data.molecs.addObject(self.relax.data.pdb.createPeptideChains())
        except:
            print exc_info()[0].__doc__ + "  " + exc_info()[1].args[0]
        print "Collection:  " + `self.relax.data.molecs.objects`

        # Try to place any RNA or DNA in the collection of molecules.
        print "\nPlacing the nucleaic acids into the collection of molecules."
        try:
            self.relax.data.molecs.addObject(self.relax.data.pdb.createNucleotideChains())
        except:
            print exc_info()[0].__doc__ + "  " + exc_info()[1].args[0]
        print "Collection:  " + `self.relax.data.molecs.objects`

        # Try to place other molecules in the collection.
        print "\nPlacing the molecules into the collection."
        try:
            self.relax.data.molecs.addObject(self.relax.data.pdb.createMolecules())
        except:
            print exc_info()[0].__doc__ + "  " + exc_info()[1].args[0]
        print "Collection:  " + `self.relax.data.molecs.objects`

        # Test if the collection contains any proteins, and raise an exception otherwise.
        contains_protein = 0
        for object in self.relax.data.molecs.objects:
            if match('Pep', `object`):
                contains_protein = 1
        if not contains_protein:
            raise RelaxPdbLoadError, file
