###############################################################################
#                                                                             #
# Copyright (C) 2008-2011 Edward d'Auvergne                                   #
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
from os import path, sep
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
import dep_check
from generic_fns.mol_res_spin import Selection
from generic_fns.structure.scientific import Scientific_data
from relax_io import file_root
from status import Status; status = Status()


class Test_scientific(TestCase):
    """Unit tests for the functions of the 'generic_fns.structure.scientific' module."""

    def __init__(self, methodName='runTest'):
        """Skip scientific Python tests if not installed.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Missing module.
        if not dep_check.scientific_module:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Scientific Python', 'unit'])

        # Execute the base class method.
        super(Test_scientific, self).__init__(methodName)



    def setUp(self):
        """Set up for all the Scientific Python PDB structural object unit tests."""

        # The path to a PDB file.
        self.test_pdb_path = status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'Ap4Aase_res1-12.pdb'
        expanded = path.split(self.test_pdb_path)
        self.test_pdb_dir = expanded[0]
        self.test_pdb_file_name = expanded[1]
        self.test_pdb_root = file_root(self.test_pdb_path)

        # Instantiate the structural data object.
        self.data = Scientific_data()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Delete the structural data object.
        del self.data

        # Reset.
        ds.__reset__()


    def test___residue_loop(self):
        """Test the private Scientific_data.__residue_loop() method."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the residues.
        res_count = 0
        for res, res_num, res_name, res_index in self.data._Scientific_data__residue_loop(self.data.structural_data[0].mol[0]):
            res_count = res_count + 1

        # Test the number of residues looped over.
        self.assertEqual(res_count, 12)

        # Test the data of the last residue.
        self.assertEqual(res_num, 12)
        self.assertEqual(res_name, 'GLY')
        self.assertEqual(len(res.atoms), 7)
        self.assertEqual(list(res.atoms.keys()), ['C', 'H', 'CA', 'O', 'N', '1HA', '2HA'])


    def test___residue_loop_selection(self):
        """Test the private Scientific_data.__residue_loop() method with a selection object."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Create the selection object (which should match the residue name of None).
        sel_obj = Selection('#Ap4Aase_res1-12_mol1')

        # Loop over the residues.
        res_count = 0
        for res, res_num, res_name, res_index in self.data._Scientific_data__residue_loop(self.data.structural_data[0].mol[0], sel_obj):
            res_count = res_count + 1

        # Test the number of residues looped over.
        self.assertEqual(res_count, 12)

        # Test the data of the last residue.
        self.assertEqual(res_num, 12)
        self.assertEqual(res_name, 'GLY')
        self.assertEqual(len(res.atoms), 7)
        self.assertEqual(list(res.atoms.keys()), ['C', 'H', 'CA', 'O', 'N', '1HA', '2HA'])


    def test___residue_loop_selection_no_match(self):
        """Test the Scientific_data.__residue_loop() method with a non-matching selection object."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Create the non-matching selection object.
        sel_obj = Selection(':XXX')

        # Loop over the residues.
        res_count = 0
        for res, res_num, res_name, res_index in self.data._Scientific_data__residue_loop(self.data.structural_data[0].mol[0], sel_obj):
            res_count = res_count + 1

        # Test the number of residues looped over.
        self.assertEqual(res_count, 0)


    def test_atom_loop(self):
        """Test the Scientific_data.atom_loop() method."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for atom in self.data.atom_loop():
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 150)


    def test_atom_loop_mol_selection(self):
        """Test the Scientific_data.atom_loop() method with the '#XXX' mol selection."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for atom in self.data.atom_loop(atom_id='#XXX'):
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 0)


    def test_atom_loop_res_selection1(self):
        """Test the Scientific_data.atom_loop() method with the ':8' res selection."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for res_num, res_name in self.data.atom_loop(atom_id=':8', res_num_flag=True, res_name_flag=True):
            # Test the residue name and number.
            self.assertEqual(res_num, 8)
            self.assertEqual(res_name, 'SER')

            # Increment the atom count.
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 11)


    def test_atom_loop_res_selection2(self):
        """Test the Scientific_data.atom_loop() method with the ':PRO' res selection."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for atom in self.data.atom_loop(atom_id=':PRO', res_name_flag=True):
            # Test the residue name.
            self.assertEqual(atom[0], 'PRO')

            # Increment the atom count.
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 42)


    def test_atom_loop_spin_selection1(self):
        """Test the Scientific_data.atom_loop() method with the '@CA' spin selection."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for spin_name in self.data.atom_loop(atom_id='@CA', atom_name_flag=True):
            # Test the spin name.
            self.assertEqual(spin_name[0], 'CA')

            # Increment the atom count.
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 12)


    def test_atom_loop_spin_selection2(self):
        """Test the Scientific_data.atom_loop() method with the '@163' spin selection."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for model_num, mol_name, res_num, res_name, spin_num, spin_name, element, pos in self.data.atom_loop(atom_id='@163', model_num_flag=True, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True):
            # Test the spin info.
            self.assertEqual(model_num, 1)
            self.assertEqual(mol_name, 'Ap4Aase_res1-12_mol1')
            self.assertEqual(res_num, 11)
            self.assertEqual(res_name, 'GLU')
            self.assertEqual(spin_num, 163)
            self.assertEqual(spin_name, 'OE1')
            self.assertEqual(element, 'O')
            self.assertEqual(pos[0], float('10.055'))
            self.assertEqual(pos[1], float('-2.74'))
            self.assertEqual(pos[2], float('-13.193'))

            # Increment the atom count.
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 1)


    def test_load_pdb(self):
        """Load a PDB file using Scientific_data.load_pdb()."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # The ModelContainer and MolContainer.
        model = self.data.structural_data[0]
        mol = model.mol[0]

        # Test the structural data.
        self.assertEqual(len(self.data.structural_data), 1)
        self.assertEqual(len(model.mol), 1)
        self.assertEqual(model.num, 1)
        self.assertEqual(mol.mol_name, self.test_pdb_root+'_mol1')
        self.assertEqual(mol.file_name, self.test_pdb_file_name)
        self.assertEqual(mol.file_path, self.test_pdb_dir)
        self.assertEqual(mol.file_model, 1)
        self.assertEqual(mol.file_mol_num, 1)
