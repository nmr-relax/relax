###############################################################################
#                                                                             #
# Copyright (C) 2015 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# relax module imports.
from lib.structure.internal import object
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_object(UnitTestCase):
    """Unit tests for the lib.structure.internal.object internal structural object module."""

    def test_add_atom_sort(self):
        """Test for automated atom sequence sorting of the add_atom() method."""

        # Initialise a structural object and add some atoms.
        struct = object.Internal()

        # Create three molecules 'X', 'Y', and 'Z' with some connected atoms.
        struct.add_atom(atom_name='A', res_name='UNK', res_num=1, mol_name='X', pos=[1., 0., -1.], element='S')
        struct.add_atom(atom_name='A', res_name='UNK', res_num=1, mol_name='Y', pos=[0., 0., 0.], element='S')
        struct.add_atom(atom_name='A', res_name='UNK', res_num=1, mol_name='Z', pos=[-1., 0., 1.], element='S')
        struct.add_atom(atom_name='A', res_name='UNK', res_num=3, mol_name='X', pos=[1., 2., -1.], element='S')
        struct.add_atom(atom_name='A', res_name='UNK', res_num=3, mol_name='Y', pos=[0., 2., 0.], element='S')
        struct.add_atom(atom_name='A', res_name='UNK', res_num=3, mol_name='Z', pos=[-1., 2., 1.], element='S')
        struct.connect_atom(mol_name='X', index1=0, index2=1)
        struct.connect_atom(mol_name='Y', index1=0, index2=1)
        struct.connect_atom(mol_name='Z', index1=0, index2=1)
        struct.add_atom(atom_name='A', res_name='UNK', res_num=2, mol_name='X', pos=[1., 20., -1.], element='S')
        struct.add_atom(atom_name='A', res_name='UNK', res_num=2, mol_name='Y', pos=[0., 20., 0.], element='S')
        struct.add_atom(atom_name='A', res_name='UNK', res_num=2, mol_name='Z', pos=[-1., 20., 1.], element='S')

        # The sorted data.
        data = [[
            ['A', 'UNK', 1, [1., 0., -1.], 'S', [2]],
            ['A', 'UNK', 2, [1., 20., -1.], 'S', []],
            ['A', 'UNK', 3, [1., 2., -1.], 'S', [0]]
        ], [
            ['A', 'UNK', 1, [0., 0., 0.], 'S', [2]],
            ['A', 'UNK', 2, [0., 20., 0.], 'S', []],
            ['A', 'UNK', 3, [0., 2., 0.], 'S', [0]]
        ], [
            ['A', 'UNK', 1, [-1., 0., 1.], 'S', [2]],
            ['A', 'UNK', 2, [-1., 20., 1.], 'S', []],
            ['A', 'UNK', 3, [-1., 2., 1.], 'S', [0]]
        ]]
        mol_names = ['X', 'Y', 'Z']

        # Test the object.
        self.assertEqual(len(struct.structural_data), 1)
        for i in range(len(struct.structural_data[0].mol)):
            # Alias.
            mol = struct.structural_data[0].mol[i]

            # Check the molecule data.
            self.assertEqual(mol.mol_name, mol_names[i])

            # Loop over the atoms.
            for j in range(len(mol.atom_name)):
                self.assertEqual(mol.atom_name[j], data[i][j][0])
                self.assertEqual(mol.res_name[j], data[i][j][1])
                self.assertEqual(mol.res_num[j], data[i][j][2])
                self.assertEqual(mol.x[j], data[i][j][3][0])
                self.assertEqual(mol.y[j], data[i][j][3][1])
                self.assertEqual(mol.z[j], data[i][j][3][2])
                self.assertEqual(mol.element[j], data[i][j][4])
                self.assertEqual(mol.bonded[j], data[i][j][5])
