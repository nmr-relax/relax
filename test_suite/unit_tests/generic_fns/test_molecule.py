###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store
from generic_fns import molecule, residue
from relax_errors import RelaxError, RelaxNoPipeError



class Test_molecule(TestCase):
    """Unit tests for the functions of the 'generic_fns.molecule' module."""

    def setUp(self):
        """Set up for all the molecule unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        relax_data_store.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        relax_data_store.current_pipe = 'orig'


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def setup_data(self):
        """Function for setting up some data for testing."""

        # Create the first residue and add some data to its spin container.
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1
        relax_data_store['orig'].mol[0].name = 'Old mol'

        # Create a second molecule.
        relax_data_store['orig'].mol.add_item('New mol')

        # Copy the residue to the new molecule.
        residue.copy(res_from=':1', res_to='#New mol')
        residue.copy(res_from='#Old mol:1', res_to='#New mol:5')

        # Change the first residue's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2


    def test_copy_between_pipes(self):
        """Test the copying of the molecule data between different data pipes.

        The function used is generic_fns.molecule.copy().
        """

        # Create the first molecule and residue and add some data to its spin container.
        molecule.create('Old mol')
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Copy the molecule to the second data pipe.
        molecule.copy(mol_from='#Old mol', pipe_to='test')
        molecule.copy(pipe_from='orig', mol_from='#Old mol', pipe_to='test', mol_to='#New mol')

        # Change the first molecule's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2

        # Test the original molecule.
        self.assertEqual(relax_data_store['orig'].mol[0].name, 'Old mol')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 2)

        # Test the new molecule.
        self.assertEqual(relax_data_store['test'].mol[0].name, 'Old mol')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].spin[0].x, 1)

        # Test the second new molecule.
        self.assertEqual(relax_data_store['test'].mol[1].name, 'New mol')
        self.assertEqual(relax_data_store['test'].mol[1].res[0].num, 1)
        self.assertEqual(relax_data_store['test'].mol[1].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['test'].mol[1].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['test'].mol[1].res[0].spin[0].x, 1)


    def test_copy_between_pipes_fail_no_pipe(self):
        """Test the failure of copying of the molecule data between different data pipes.

        The function used is generic_fns.molecule.copy().
        """

        # Create the first molecule and residue and add some data to its spin container.
        molecule.create('Old mol')
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Copy the molecule to the second data pipe.
        self.assertRaises(RelaxNoPipeError, molecule.copy, mol_from='#Old mol', pipe_to='test2')


    def test_copy_within_pipe(self):
        """Test the copying of the molecule data within a single data pipe.

        The function used is generic_fns.molecule.copy().
        """

        # Create the first molecule and residue and add some data to its spin container.
        molecule.create('Old mol')
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Copy the molecule a few times.
        molecule.copy(mol_from='#Old mol', mol_to='#2')
        molecule.copy(mol_from='#Old mol', pipe_to='orig', mol_to='#3')

        # Change the first molecule's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2

        # Copy the molecule once more.
        molecule.copy(mol_from='#Old mol', mol_to='#4')

        # Test the original molecule.
        self.assertEqual(relax_data_store['orig'].mol[0].name, 'Old mol')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 2)

        # Test the new molecule 2.
        self.assertEqual(relax_data_store['orig'].mol[1].name, 2)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].x, 1)

        # Test the new molecule 3.
        self.assertEqual(relax_data_store['orig'].mol[2].name, 3)
        self.assertEqual(relax_data_store['orig'].mol[2].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[2].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[2].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[2].res[0].spin[0].x, 1)

        # Test the new molecule 4.
        self.assertEqual(relax_data_store['orig'].mol[3].name, 4)
        self.assertEqual(relax_data_store['orig'].mol[3].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[3].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[3].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[3].res[0].spin[0].x, 2)


    def test_copy_within_pipe_fail(self):
        """Test the failure of the copying of the molecule data within a molecule.

        The function used is generic_fns.molecule.copy().
        """

        # Create a few molecules.
        molecule.create('GST')
        molecule.create('GB1')

        # Copy a non-existent molecule (MBP).
        self.assertRaises(RelaxError, molecule.copy, mol_from='#MBP', mol_to='#IL4')

        # Copy a molecule to one which already exists.
        self.assertRaises(RelaxError, molecule.copy, mol_from='#GST', mol_to='#GB1')


    def test_creation(self):
        """Test the creation of a molecule data structure.

        The function used is generic_fns.molecule.create().
        """

        # Create a few new molecules.
        molecule.create('Ap4Aase')
        molecule.create('ATP')
        molecule.create(mol_name='MgF4')

        # Test that the molecule names are correct.
        self.assertEqual(relax_data_store['orig'].mol[0].name, 'Ap4Aase')
        self.assertEqual(relax_data_store['orig'].mol[1].name, 'ATP')
        self.assertEqual(relax_data_store['orig'].mol[2].name, 'MgF4')


    def test_creation_fail(self):
        """Test the failure of molecule creation by supplying two molecules with the same name.

        The function used is generic_fns.molecule.create().
        """

        # Create the first molecule.
        molecule.create('CaM')

        # Assert that a RelaxError occurs when the next added molecule has the same name as the first.
        self.assertRaises(RelaxError, molecule.create, 'CaM')

