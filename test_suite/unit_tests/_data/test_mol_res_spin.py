###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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

# Python module imports.
from unittest import TestCase

# relax module imports.
from data.mol_res_spin import MoleculeList


class Test_mol_res_spin(TestCase):
    """Unit tests for the data.mol_res_spin relax module."""

    def setUp(self):
        """Create a mol-res-spin structure for testing all the object methods."""

        # The initial empty structure.
        self.mol = MoleculeList()

        # Add a test object to the first molecule, first residue, first spin.
        self.mol[0].res[0].spin[0].x = 1


    def test_add_mol(self):
        """Unit test for the 'add_item()' method of the MolecularList class."""

        # The name of the new molecule.
        name = 'Ap4Aase'

        # Add a molecule.
        self.mol.add_item(mol_name=name)

        # Test that the molecule exists.
        self.assertEqual(self.mol[1].name, name)

        # Test that the molecule's single spin system container does not have the object 'x'.
        self.assert_(not hasattr(self.mol[1].res[0].spin[0], 'x'))


    def test_add_res(self):
        """Unit test for the 'add_item()' method of the ResidueList class."""

        # The name and number of the new residue.
        name = 'LEU'
        num = -5

        # Add the residue.
        self.mol[0].res.add_item(res_name=name, res_num=num)

        # Test that the residue exists.
        self.assertEqual(self.mol[0].res[1].name, name)
        self.assertEqual(self.mol[0].res[1].num, num)

        # Test that the residues' single spin system container does not have the object 'x'.
        self.assert_(not hasattr(self.mol[0].res[1].spin[0], 'x'))


    def test_add_spin(self):
        """Unit test for the 'add_item()' method of the SpinList class."""

        # The name and number of the new spin.
        name = 'N'
        num = 1409

        # Add the spin.
        self.mol[0].res[0].spin.add_item(spin_name=name, spin_num=num, select=0)

        # Test that the spin exists.
        self.assertEqual(self.mol[0].res[0].spin[1].name, name)
        self.assertEqual(self.mol[0].res[0].spin[1].num, num)
        self.assertEqual(self.mol[0].res[0].spin[1].select, 0)

        # Test that the spin system container does not have the object 'x'.
        self.assert_(not hasattr(self.mol[0].res[0].spin[1], 'x'))


    def test_mol_container_repr(self):
        """Unit test for the validity of the MoleculeContainer.__repr__() method."""

        # Test that __repr__() returns a string.
        self.assert_(type(self.mol[0].__repr__()), str)


    def test_mol_list_repr(self):
        """Unit test for the validity of the MoleculeList.__repr__() method."""

        # Test that __repr__() returns a string.
        self.assert_(type(self.mol.__repr__()), str)


    def test_res_container_repr(self):
        """Unit test for the validity of the ResidueContainer.__repr__() method."""

        # Test that __repr__() returns a string.
        self.assert_(type(self.mol[0].res[0].__repr__()), str)


    def test_res_list_repr(self):
        """Unit test for the validity of the ResidueList.__repr__() method."""

        # Test that __repr__() returns a string.
        self.assert_(type(self.mol[0].res.__repr__()), str)


    def test_spin_container_repr(self):
        """Unit test for the validity of the SpinContainer.__repr__() method."""

        # Test that __repr__() returns a string.
        self.assert_(type(self.mol[0].res[0].spin[0].__repr__()), str)


    def test_spin_list_repr(self):
        """Unit test for the validity of the SpinList.__repr__() method."""

        # Test that __repr__() returns a string.
        self.assert_(type(self.mol[0].res[0].spin.__repr__()), str)
