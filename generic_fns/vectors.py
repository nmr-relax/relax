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
from Numeric import Float64, dot, zeros


class Vectors:
    def __init__(self, relax):
        """Class containing the function to calculate the XH vector from the loaded structure."""

        self.relax = relax


    def set(self, run=None, res=None, xh_vect=None):
        """Function for setting the XH and XH unit vectors."""

        # Place the XH vector in 'self.relax.data.res'.
        self.relax.data.res[run][res].xh_vect = xh_vect

        # Calculate the normalised vector.
        self.relax.data.res[run][res].xh_unit = xh_vect / sqrt(dot(xh_vect, xh_vect))


    def vectors(self, run, heteronuc, proton):
        """Function for calculating the XH vector from the loaded structure."""

        # Test if the PDB file has been loaded.
        if not self.relax.data.pdb.has_key(run):
            raise RelaxPdbError, run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Number of structures.
        if type(self.relax.data.pdb[run]) == list:
            num_str = len(self.relax.data.pdb[run])
        else:
            num_str = 1

        # Create a temporary vector list for each residue.
        for i in xrange(len(self.relax.data.res[run])):
            self.relax.data.res[run][i].xh_vect = []

        # Loop over the structures.
        for i in xrange(num_str):
            # Print out.
            print "\nStructure " + `i` + "\n"

            # Reassign the first peptide chain of the first structure.
            if type(self.relax.data.pdb[run]) == list:
                pdb_residues = self.relax.data.pdb[run][i].peptide_chains[0].residues
            else:
                pdb_residues = self.relax.data.pdb[run].peptide_chains[0].residues

            # Loop over the sequence.
            for j in xrange(len(self.relax.data.res[run])):
                # Find the corresponding residue in the PDB.
                pdb_res = None
                for k in xrange(len(pdb_residues)):
                    if self.relax.data.res[run][j].num == pdb_residues[k].number:
                        pdb_res = pdb_residues[k]
                        break
                if pdb_res == None:
                    raise RelaxNoResError, self.relax.data.res[run][j].num

                # Test if the proton atom exists for residue i.
                if not pdb_res.atoms.has_key(proton):
                    print "The proton atom " + `proton` + " could be found for residue '" + `self.relax.data.res[run][j].num` + " " + self.relax.data.res[run][j].name + "'."
                    self.relax.data.res[run][j].xh_vect.append(None)

                # Test if the heteronucleus atom exists for residue i.
                elif not pdb_res.atoms.has_key(heteronuc):
                    print "The heteronucleus atom " + `heteronuc` + " could be found for residue '" + `self.relax.data.res[run][j].num` + " " + self.relax.data.res[run][j].name + "'."
                    self.relax.data.res[run][j].xh_vect.append(None)

                # Calculate the vector.
                else:
                    # Get the proton position.
                    posH = pdb_res.atoms[proton].position.array

                    # Get the heteronucleus position.
                    posX = pdb_res.atoms[heteronuc].position.array

                    # Calculate the vector.
                    self.relax.data.res[run][j].xh_vect.append(posH - posX)

        # Average the vectors and convert xh_vect from an array of vectors to a vector.
        for i in xrange(len(self.relax.data.res[run])):
            # No vectors.
            if self.relax.data.res[run][i].xh_vect[0] == None:
                del self.relax.data.res[run][i].xh_vect
                continue

            # Average vector.
            ave_vector = zeros(3, Float64)

            # Sum the vectors.
            for j in xrange(num_str):
                # Sum.
                ave_vector = ave_vector + self.relax.data.res[run][i].xh_vect[j]

            # Average the vector.
            ave_vector = ave_vector / num_str

            # Replace the temporary vector list with the average vector.
            self.relax.data.res[run][i].xh_vect = ave_vector

            # Calculate the normalised vector.
            self.relax.data.res[run][i].xh_unit = ave_vector / sqrt(dot(ave_vector, ave_vector))
