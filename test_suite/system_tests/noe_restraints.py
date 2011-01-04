###############################################################################
#                                                                             #
# Copyright (C) 2008-2010 Edward d'Auvergne                                   #
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
from os import sep

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import create_molecule, create_residue, create_spin
from status import Status


class Noe_restraints(SystemTestCase):
    """Class for testing various aspects specific to NOE restraints."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('test', 'N-state')


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
                 ['N3', 'O2', 'H42', 'N4']],
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
                create_residue(res_nums[i][j], mol_name=mol_names[i])

                # Loop over the atoms.
                for k in range(len(spin_names[i][j])):
                    # Create the spin.
                    create_spin(spin_names[i][j][k], res_num=res_nums[i][j], mol_name=mol_names[i])

        # Display the sequence for debugging.
        self.interpreter.sequence.display()


    def test_read_generic_phthalic_acid(self):
        """Test the reading of phthalic acid NOE restraints in generic format."""

        # Set the file name.
        ds.file_name = 'phthalic_acid'

        # Execute the script.
        self.interpreter.run(script_file=Status().install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'phthalic_acid_noes.py')

        # The restraint data.
        restraints = [
            ['@H1',  '@H6',  3.0, 5.0],
            ['@H3',  '@H9',  3.0, 5.0],
            ['@H3',  '@H10', 3.0, 5.0],
            ['@H3',  '@H11', 3.0, 5.0],
            ['@H3',  '@H19', 3.0, 5.0],
            ['@H3',  '@Q9',  3.0, 6.0],
            ['@H4',  '@H8',  3.0, 5.0],
            ['@H4',  '@H9',  3.0, 5.0],
            ['@H4',  '@H10', 3.0, 5.0],
            ['@H4',  '@H11', 3.0, 5.0],
            ['@H4',  '@H15', 3.0, 5.0],
            ['@H4',  '@H19', 3.0, 5.0],
            ['@H4',  '@Q9',  3.0, 6.0],
            ['@H5',  '@H9',  3.0, 5.0],
            ['@H5',  '@Q7',  3.0, 6.0],
            ['@H5',  '@Q9',  3.0, 6.0],
            ['@H6',  '@H8',  3.0, 5.0],
            ['@H6',  '@H9',  3.0, 5.0],
            ['@H6',  '@H10', 3.0, 5.0],
            ['@H6',  '@H11', 3.0, 5.0],
            ['@H6',  '@H15', 3.0, 5.0],
            ['@H6',  '@Q7',  3.0, 6.0],
            ['@H6',  '@H19', 3.0, 5.0],
            ['@H6',  '@Q9',  3.0, 6.0],
            ['@H26', '@H1',  3.0, 5.0],
            ['@H26', '@H8',  3.0, 5.0],
            ['@H26', '@H9',  3.0, 5.0],
            ['@H26', '@H10', 3.0, 5.0],
            ['@H26', '@H11', 3.0, 5.0],
            ['@H26', '@H15', 3.0, 5.0],
            ['@H26', '@Q7',  3.0, 6.0],
            ['@H26', '@H19', 3.0, 5.0],
            ['@H26', '@Q9',  3.0, 6.0],
            ['@H27', '@H1',  3.0, 5.0],
            ['@H27', '@H8',  3.0, 5.0],
            ['@H27', '@H9',  3.0, 5.0],
            ['@H27', '@H11', 3.0, 5.0],
            ['@H27', '@H13', 3.0, 5.0],
            ['@H27', '@H15', 3.0, 5.0],
            ['@H27', '@Q7',  3.0, 6.0],
            ['@H27', '@H19', 3.0, 5.0],
            ['@H27', '@Q9',  3.0, 6.0],
            ['@H28', '@H1',  3.0, 5.0],
            ['@H28', '@H8',  3.0, 5.0],
            ['@H28', '@H9',  3.0, 5.0],
            ['@H28', '@H11', 3.0, 5.0],
            ['@H28', '@H15', 3.0, 5.0],
            ['@H28', '@Q7',  3.0, 6.0],
            ['@H28', '@H19', 3.0, 5.0],
            ['@H28', '@Q9',  3.0, 6.0]
        ]

        # Test that the restraints are properly set.
        for i in range(len(restraints)):
            # Atom ids.
            self.assertEqual(cdp.noe_restraints[i][0], restraints[i][0])
            self.assertEqual(cdp.noe_restraints[i][1], restraints[i][1])

            # Lower and upper bound.
            self.assertEqual(cdp.noe_restraints[i][2], restraints[i][2])
            self.assertEqual(cdp.noe_restraints[i][3], restraints[i][3])


    def test_read_xplor_methyl(self):
        """Test the reading of an Xplor NOE restraints file fragment with a methyl group."""

        # Set the file name.
        ds.file_name = 'pseudo_atoms.dat'

        # Execute the script.
        self.interpreter.run(script_file=Status().install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'n_state_model'+sep+'phthalic_acid_noes.py')

        # The restraint data.
        restraints = [
            ['@H28', '@H9',  3.0, 5.0],
            ['@H28', '@Q9',  3.0, 6.0]
        ]

        # Test that the restraints are properly set.
        for i in range(len(restraints)):
            # Atom ids.
            self.assertEqual(cdp.noe_restraints[i][0], restraints[i][0])
            self.assertEqual(cdp.noe_restraints[i][1], restraints[i][1])

            # Lower and upper bound.
            self.assertEqual(cdp.noe_restraints[i][2], restraints[i][2])
            self.assertEqual(cdp.noe_restraints[i][3], restraints[i][3])


    def test_read_xplor_rna(self):
        """Test the reading of RNA H-bond restraints in Xplor format."""

        # Generate the RNA sequence.
        self.rna_seq()

        # Read the Xplor input file.
        self.interpreter.noe.read_restraints(file='noe_rna_hbond.dat', dir=Status().install_path + sep+'test_suite'+sep+'shared_data'+sep+'noe_restraints')

        # The restraint data.
        restraints = [
            ['#A:1@N1',  '#B:4@H3',  1.93, 0.20, 0.20],
            ['#A:1@N1',  '#B:4@N3',  2.95, 0.20, 0.20],
            ['#A:1@N6',  '#B:4@O4',  2.83, 0.20, 0.20],
            ['#A:1@H62', '#B:4@O4',  1.82, 0.20, 0.20],
            ['#A:2@H3',  '#B:3@N1',  1.93, 0.20, 0.20],
            ['#A:2@N3',  '#B:3@N1',  2.95, 0.20, 0.20],
            ['#A:2@O4',  '#B:3@N6',  2.83, 0.20, 0.20],
            ['#A:2@O4',  '#B:3@H62', 1.82, 0.20, 0.20],
            ['#A:3@H1',  '#B:2@N3',  1.89, 0.20, 0.20],
            ['#A:3@N1',  '#B:2@N3',  2.91, 0.20, 0.20],
            ['#A:3@H22', '#B:2@O2',  2.08, 0.20, 0.20],
            ['#A:3@N2',  '#B:2@O2',  3.08, 0.20, 0.20],
            ['#A:3@O6',  '#B:2@H42', 1.71, 0.20, 0.20],
            ['#A:3@O6',  '#B:2@N4',  2.72, 0.20, 0.20],
            ['#A:4@N3',  '#B:1@H1',  1.89, 0.20, 0.20],
            ['#A:4@N3',  '#B:1@N1',  2.91, 0.20, 0.20],
            ['#A:4@O2',  '#B:1@H22', 2.08, 0.20, 0.20],
            ['#A:4@O2',  '#B:1@N2',  3.08, 0.20, 0.20],
            ['#A:4@H42', '#B:1@O6',  1.71, 0.20, 0.20],
            ['#A:4@N4',  '#B:1@O6',  2.72, 0.20, 0.20]
        ]

        # Test that the restraints are properly set.
        for i in range(len(restraints)):
            # Atom ids.
            self.assertEqual(cdp.noe_restraints[i][0], restraints[i][0])
            self.assertEqual(cdp.noe_restraints[i][1], restraints[i][1])

            # Lower and upper bound.
            self.assertEqual(cdp.noe_restraints[i][2], restraints[i][2]-restraints[i][3])
            self.assertEqual(cdp.noe_restraints[i][3], restraints[i][2]+restraints[i][4])
