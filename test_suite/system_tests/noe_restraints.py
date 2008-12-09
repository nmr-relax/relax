###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

# Python module imports.
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import create_molecule, create_residue, create_spin


class Noe_restraints(TestCase):
    """Class for testing various aspects specific to NOE restraints."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('test', 'N-state')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def rna_seq(self):
        """Generate the RNA sequence of the noe_rna_hbond.dat restraint file."""

        # Info.
        mol_names = ['A', 'B']
        res_nums = [
                [1, 2, 3, 4],
                [4, 3, 2, 1]
        ]
        spin_names = [
                [['N1', 'N6', 'H62'],
                 ['H3', 'N3', 'O4'],
                 ['H1', 'N1', 'H22', 'N2', 'O6'],
                 ['N3', 'O2', 'H42', 'H4']],
                [['H3', 'N3', 'O4'],
                 ['N1', 'N6', 'H62'],
                 ['N3', 'O2', 'H42', 'N4'],
                 ['H1', 'N1', 'H22', 'N2', 'O6']]
        ]
        
        # Loop over the molecules.
        for i in range(len(mol_names)):
            # Create the molecule.
            create_molecule(mol_names[i])

            # Loop over the residues.
            for j in range(len(res_nums[i])):
                # Create the residue.
                create_residue(res_nums[i][j])

                # Loop over the atoms.
                for k in range(len(spin_names[i][j][k])):
                    # Create the spin.
                    create_spin(spin_names[i][j][k]))


    def test_read_xplor_rna(self):
        """Test the reading of RNA H-bond restraints in Xplor format."""

        # Generate the RNA sequence.
        self.rna_seq()

        # Read the Xplor input file.
        self.relax.interpreter._Noe.read_restraints(file=noe_rna_hbond.dat, dir=sys.path[-1] + '/test_suite/shared_data/noe_restraints')
