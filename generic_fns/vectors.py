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

from math import sqrt
from Numeric import dot


class Vectors:
    def __init__(self, relax):
        """Class containing the function to calculate the XH vector from the loaded structure."""

        self.relax = relax


    def vectors(self, run, heteronuc, proton):
        """Function for calculating the XH vector from the loaded structure."""

        # Test if the PDB file has been loaded.
        if not self.relax.data.pdb.has_key(run):
            raise RelaxPdbError

        # Test if sequence data is loaded.
        if not len(self.relax.data.res[run]):
            raise RelaxSequenceError

        # Reassign the first peptide chain of the first structure.
        if type(self.relax.data.pdb[run]) == list:
            raise RelaxError, "Calculation of vectors from multiple structures is not yet implemented."
        else:
            pdb_residues = self.relax.data.pdb[run].peptide_chains[0].residues

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Find the corresponding residue in the PDB.
            pdb_res = None
            for j in xrange(len(pdb_residues)):
                if self.relax.data.res[run][i].name == pdb_residues[j].name and self.relax.data.res[run][i].num == pdb_residues[j].number:
                    pdb_res = pdb_residues[j]
                    break
            if pdb_res == None:
                raise RelaxNoResError, (self.relax.data.res[run][i].num, self.relax.data.res[run][i].name)

            # Test if the proton atom exists for residue i.
            if not pdb_res.atoms.has_key(proton):
                print "The proton atom " + `proton` + " could be found for residue '" + `self.relax.data.res[run][i].num` + " " + self.relax.data.res[run][i].name + "'."
                self.relax.data.res[run][i].xh_vect = None

            # Test if the heteronucleus atom exists for residue i.
            elif not pdb_res.atoms.has_key(heteronuc):
                print "The heteronucleus atom " + `heteronuc` + " could be found for residue '" + `self.relax.data.res[run][i].num` + " " + self.relax.data.res[run][i].name + "'."
                self.relax.data.res[run][i].xh_vect = None

            # Calculate the vector.
            else:
                # Get the proton position.
                posH = pdb_res.atoms[proton].position.array

                # Get the heteronucleus position.
                posX = pdb_res.atoms[heteronuc].position.array

                # Calculate the vector and place it in 'self.relax.data.res[run][i].xh_vect'.
                self.relax.data.res[run][i].xh_vect = posH - posX

                # Calculate the normalised vector.
                self.relax.data.res[run][i].xh_unit = self.relax.data.res[run][i].xh_vect / sqrt(dot(self.relax.data.res[run][i].xh_vect, self.relax.data.res[run][i].xh_vect))
