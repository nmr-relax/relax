###############################################################################
#                                                                             #
# Copyright (C) 2006-2010 Edward d'Auvergne                                   #
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
import sys

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()


class Sequence(SystemTestCase):
    """Class for testing the sequence functions."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_load_protein_asp_atoms_from_pdb(self):
        """Load all aspartic acid atoms from the single residue in a loaded protein PDB file."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

        # Load all the ASP atoms (1 molecule, 1 ASP residue, and all atoms).
        self.interpreter.structure.load_spins(spin_id=':ASP')

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Ap4Aase_res1-12_mol1')
        self.assertEqual(len(cdp.mol[0].res), 1)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, 7)
        self.assertEqual(cdp.mol[0].res[0].name, 'ASP')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 12)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, 91)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'N')
        self.assertEqual(cdp.mol[0].res[0].spin[1].num, 92)
        self.assertEqual(cdp.mol[0].res[0].spin[1].name, 'H')
        self.assertEqual(cdp.mol[0].res[0].spin[2].num, 93)
        self.assertEqual(cdp.mol[0].res[0].spin[2].name, 'CA')
        self.assertEqual(cdp.mol[0].res[0].spin[3].num, 94)
        self.assertEqual(cdp.mol[0].res[0].spin[3].name, 'HA')
        self.assertEqual(cdp.mol[0].res[0].spin[4].num, 95)
        self.assertEqual(cdp.mol[0].res[0].spin[4].name, 'CB')
        self.assertEqual(cdp.mol[0].res[0].spin[5].num, 96)
        self.assertEqual(cdp.mol[0].res[0].spin[5].name, '1HB')
        self.assertEqual(cdp.mol[0].res[0].spin[6].num, 97)
        self.assertEqual(cdp.mol[0].res[0].spin[6].name, '2HB')
        self.assertEqual(cdp.mol[0].res[0].spin[7].num, 99)
        self.assertEqual(cdp.mol[0].res[0].spin[7].name, 'CG')
        self.assertEqual(cdp.mol[0].res[0].spin[8].num, 100)
        self.assertEqual(cdp.mol[0].res[0].spin[8].name, 'OD1')
        self.assertEqual(cdp.mol[0].res[0].spin[9].num, 101)
        self.assertEqual(cdp.mol[0].res[0].spin[9].name, 'OD2')
        self.assertEqual(cdp.mol[0].res[0].spin[10].num, 102)
        self.assertEqual(cdp.mol[0].res[0].spin[10].name, 'C')
        self.assertEqual(cdp.mol[0].res[0].spin[11].num, 103)
        self.assertEqual(cdp.mol[0].res[0].spin[11].name, 'O')


    def test_load_protein_gly_N_Ca_spins_from_pdb(self):
        """Load the glycine backbone amide N and Ca spins from a loaded protein PDB file."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

        # Generate the sequence of nitrogen spins (1 molecule, all GLY residues, and only N spins).
        self.interpreter.structure.load_spins(spin_id=':GLY@N')

        # Append to the sequence the alpha carbon spins (1 molecule, all GLY residues, and only Ca spins).
        self.interpreter.structure.load_spins(spin_id=':GLY@CA')

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Ap4Aase_res1-12_mol1')
        self.assertEqual(len(cdp.mol[0].res), 3)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 2)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'N')
        self.assertEqual(cdp.mol[0].res[0].spin[1].num, 2)
        self.assertEqual(cdp.mol[0].res[0].spin[1].name, 'CA')

        # 2nd residue.
        self.assertEqual(cdp.mol[0].res[1].num, 4)
        self.assertEqual(cdp.mol[0].res[1].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[1].spin), 2)
        self.assertEqual(cdp.mol[0].res[1].spin[0].num, 51)
        self.assertEqual(cdp.mol[0].res[1].spin[0].name, 'N')
        self.assertEqual(cdp.mol[0].res[1].spin[1].num, 53)
        self.assertEqual(cdp.mol[0].res[1].spin[1].name, 'CA')

        # 3rd residue.
        self.assertEqual(cdp.mol[0].res[2].num, 12)
        self.assertEqual(cdp.mol[0].res[2].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[2].spin), 2)
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 167)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assertEqual(cdp.mol[0].res[2].spin[1].num, 169)
        self.assertEqual(cdp.mol[0].res[2].spin[1].name, 'CA')


    def test_load_protein_gly_N_spins_from_pdb(self):
        """Load the glycine backbone amide N spins from a loaded protein PDB file."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

        # Generate the sequence (1 molecule, all GLY residues, and only N spins).
        self.interpreter.structure.load_spins(spin_id=':GLY@N')

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Ap4Aase_res1-12_mol1')
        self.assertEqual(len(cdp.mol[0].res), 3)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'N')

        # 2nd residue.
        self.assertEqual(cdp.mol[0].res[1].num, 4)
        self.assertEqual(cdp.mol[0].res[1].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[1].spin), 1)
        self.assertEqual(cdp.mol[0].res[1].spin[0].num, 51)
        self.assertEqual(cdp.mol[0].res[1].spin[0].name, 'N')

        # 3rd residue.
        self.assertEqual(cdp.mol[0].res[2].num, 12)
        self.assertEqual(cdp.mol[0].res[2].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[2].spin), 1)
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 167)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')


    def test_load_protein_N_spins_from_pdb(self):
        """Load the protein backbone amide N spins from a loaded PDB file."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

        # Generate the sequence (1 molecule, all residues, and only N spins).
        self.interpreter.structure.load_spins(spin_id='@N')

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'Ap4Aase_res1-12_mol1')
        self.assertEqual(len(cdp.mol[0].res), 12)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'N')

        # 2nd residue.
        self.assertEqual(cdp.mol[0].res[1].num, 2)
        self.assertEqual(cdp.mol[0].res[1].name, 'PRO')
        self.assertEqual(len(cdp.mol[0].res[1].spin), 1)
        self.assertEqual(cdp.mol[0].res[1].spin[0].num, 11)
        self.assertEqual(cdp.mol[0].res[1].spin[0].name, 'N')

        # 3rd residue.
        self.assertEqual(cdp.mol[0].res[2].num, 3)
        self.assertEqual(cdp.mol[0].res[2].name, 'LEU')
        self.assertEqual(len(cdp.mol[0].res[2].spin), 1)
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 28)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')

        # 4th residue.
        self.assertEqual(cdp.mol[0].res[3].num, 4)
        self.assertEqual(cdp.mol[0].res[3].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[3].spin), 1)
        self.assertEqual(cdp.mol[0].res[3].spin[0].num, 51)
        self.assertEqual(cdp.mol[0].res[3].spin[0].name, 'N')

        # 5th residue.
        self.assertEqual(cdp.mol[0].res[4].num, 5)
        self.assertEqual(cdp.mol[0].res[4].name, 'SER')
        self.assertEqual(len(cdp.mol[0].res[4].spin), 1)
        self.assertEqual(cdp.mol[0].res[4].spin[0].num, 59)
        self.assertEqual(cdp.mol[0].res[4].spin[0].name, 'N')

        # 6th residue.
        self.assertEqual(cdp.mol[0].res[5].num, 6)
        self.assertEqual(cdp.mol[0].res[5].name, 'MET')
        self.assertEqual(len(cdp.mol[0].res[5].spin), 1)
        self.assertEqual(cdp.mol[0].res[5].spin[0].num, 71)
        self.assertEqual(cdp.mol[0].res[5].spin[0].name, 'N')

        # 7th residue.
        self.assertEqual(cdp.mol[0].res[6].num, 7)
        self.assertEqual(cdp.mol[0].res[6].name, 'ASP')
        self.assertEqual(len(cdp.mol[0].res[6].spin), 1)
        self.assertEqual(cdp.mol[0].res[6].spin[0].num, 91)
        self.assertEqual(cdp.mol[0].res[6].spin[0].name, 'N')

        # 8th residue.
        self.assertEqual(cdp.mol[0].res[7].num, 8)
        self.assertEqual(cdp.mol[0].res[7].name, 'SER')
        self.assertEqual(len(cdp.mol[0].res[7].spin), 1)
        self.assertEqual(cdp.mol[0].res[7].spin[0].num, 104)
        self.assertEqual(cdp.mol[0].res[7].spin[0].name, 'N')

        # 9th residue.
        self.assertEqual(cdp.mol[0].res[8].num, 9)
        self.assertEqual(cdp.mol[0].res[8].name, 'PRO')
        self.assertEqual(len(cdp.mol[0].res[8].spin), 1)
        self.assertEqual(cdp.mol[0].res[8].spin[0].num, 116)
        self.assertEqual(cdp.mol[0].res[8].spin[0].name, 'N')

        # 10th residue.
        self.assertEqual(cdp.mol[0].res[9].num, 10)
        self.assertEqual(cdp.mol[0].res[9].name, 'PRO')
        self.assertEqual(len(cdp.mol[0].res[9].spin), 1)
        self.assertEqual(cdp.mol[0].res[9].spin[0].num, 133)
        self.assertEqual(cdp.mol[0].res[9].spin[0].name, 'N')

        # 11th residue.
        self.assertEqual(cdp.mol[0].res[10].num, 11)
        self.assertEqual(cdp.mol[0].res[10].name, 'GLU')
        self.assertEqual(len(cdp.mol[0].res[10].spin), 1)
        self.assertEqual(cdp.mol[0].res[10].spin[0].num, 150)
        self.assertEqual(cdp.mol[0].res[10].spin[0].name, 'N')

        # 12th residue.
        self.assertEqual(cdp.mol[0].res[11].num, 12)
        self.assertEqual(cdp.mol[0].res[11].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[11].spin), 1)
        self.assertEqual(cdp.mol[0].res[11].spin[0].num, 167)
        self.assertEqual(cdp.mol[0].res[11].spin[0].name, 'N')


    def test_read(self):
        """The sequence.read() test."""

        # Read the sequence.
        self.interpreter.sequence.read(file='test_seq', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data', res_num_col=1, res_name_col=2)
