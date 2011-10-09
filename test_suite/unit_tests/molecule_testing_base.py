###############################################################################
#                                                                             #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
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

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import copy_residue, create_residue
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoPipeError, RelaxResSelectDisallowError, RelaxSpinSelectDisallowError
from test_suite.unit_tests.base_classes import UnitTestCase


class Molecule_base_class(UnitTestCase):
    """Testing base class for 'prompt.molecule' and corresponding 'generic_fns.mol_spin_res' fns.

    This base class also contains many shared unit tests.
    """

    def setUp(self):
        """Set up for all the molecule unit tests."""

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        ds.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        pipes.switch('orig')


    def setup_data(self):
        """Function for setting up some data for the unit tests."""

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Create the first residue and add some data to its spin container.
        create_residue(1, 'Ala')
        dp.mol[0].res[0].spin[0].num = 111
        dp.mol[0].res[0].spin[0].x = 1
        dp.mol[0].name = 'Old mol'

        # Create a second molecule.
        dp.mol.add_item('New mol')

        # Copy the residue to the new molecule.
        copy_residue(res_from=':1', res_to='#New mol')
        copy_residue(res_from='#Old mol:1', res_to='#New mol:5')

        # Change the first residue's data.
        dp.mol[0].res[0].spin[0].num = 222
        dp.mol[0].res[0].spin[0].x = 2


    def test_copy_molecule_between_pipes(self):
        """Test the copying of the molecule data between different data pipes.

        The function tested is both generic_fns.mol_res_spin.copy_molecule() and
        prompt.molecule.copy().
        """

        # Get the data pipes.
        dp = pipes.get_pipe('orig')
        dp_test = pipes.get_pipe('test')

        # Create the first molecule and residue and add some data to its spin container.
        self.molecule_fns.create('Old mol')
        create_residue(1, 'Ala')
        dp.mol[0].res[0].spin[0].num = 111
        dp.mol[0].res[0].spin[0].x = 1

        # Copy the molecule to the second data pipe.
        self.molecule_fns.copy(mol_from='#Old mol', pipe_to='test')
        self.molecule_fns.copy(pipe_from='orig', mol_from='#Old mol', pipe_to='test', mol_to='#New mol')

        # Change the first molecule's data.
        dp.mol[0].res[0].spin[0].num = 222
        dp.mol[0].res[0].spin[0].x = 2

        # Test the original molecule.
        self.assertEqual(dp.mol[0].name, 'Old mol')
        self.assertEqual(dp.mol[0].res[0].num, 1)
        self.assertEqual(dp.mol[0].res[0].name, 'Ala')
        self.assertEqual(dp.mol[0].res[0].spin[0].num, 222)
        self.assertEqual(dp.mol[0].res[0].spin[0].x, 2)

        # Test the new molecule.
        self.assertEqual(dp_test.mol[0].name, 'Old mol')
        self.assertEqual(dp_test.mol[0].res[0].num, 1)
        self.assertEqual(dp_test.mol[0].res[0].name, 'Ala')
        self.assertEqual(dp_test.mol[0].res[0].spin[0].num, 111)
        self.assertEqual(dp_test.mol[0].res[0].spin[0].x, 1)

        # Test the second new molecule.
        self.assertEqual(dp_test.mol[1].name, 'New mol')
        self.assertEqual(dp_test.mol[1].res[0].num, 1)
        self.assertEqual(dp_test.mol[1].res[0].name, 'Ala')
        self.assertEqual(dp_test.mol[1].res[0].spin[0].num, 111)
        self.assertEqual(dp_test.mol[1].res[0].spin[0].x, 1)


    def test_copy_molecule_between_pipes_fail_no_pipe(self):
        """Test the failure of copying of the molecule data between different data pipes.

        The function tested is both generic_fns.mol_res_spin.copy_molecule() and
        prompt.molecule.copy().
        """

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Create the first molecule and residue and add some data to its spin container.
        self.molecule_fns.create('Old mol')
        create_residue(1, 'Ala')
        dp.mol[0].res[0].spin[0].num = 111
        dp.mol[0].res[0].spin[0].x = 1

        # Copy the molecule to the second data pipe.
        self.assertRaises(RelaxNoPipeError, self.molecule_fns.copy, mol_from='#Old mol', pipe_to='test2')


    def test_copy_molecule_within_pipe(self):
        """Test the copying of the molecule data within a single data pipe.

        The function tested is both generic_fns.mol_res_spin.copy_molecule() and
        prompt.molecule.copy().
        """

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Create the first molecule and residue and add some data to its spin container.
        self.molecule_fns.create('Old mol')
        create_residue(1, 'Ala')
        dp.mol[0].res[0].spin[0].num = 111
        dp.mol[0].res[0].spin[0].x = 1

        # Copy the molecule a few times.
        self.molecule_fns.copy(mol_from='#Old mol', mol_to='#2')
        self.molecule_fns.copy(mol_from='#Old mol', pipe_to='orig', mol_to='#3')

        # Change the first molecule's data.
        dp.mol[0].res[0].spin[0].num = 222
        dp.mol[0].res[0].spin[0].x = 2

        # Copy the molecule once more.
        self.molecule_fns.copy(mol_from='#Old mol', mol_to='#4')

        # Test the original molecule.
        self.assertEqual(dp.mol[0].name, 'Old mol')
        self.assertEqual(dp.mol[0].res[0].num, 1)
        self.assertEqual(dp.mol[0].res[0].name, 'Ala')
        self.assertEqual(dp.mol[0].res[0].spin[0].num, 222)
        self.assertEqual(dp.mol[0].res[0].spin[0].x, 2)

        # Test the new molecule 2.
        self.assertEqual(dp.mol[1].name, 2)
        self.assertEqual(dp.mol[1].res[0].num, 1)
        self.assertEqual(dp.mol[1].res[0].name, 'Ala')
        self.assertEqual(dp.mol[1].res[0].spin[0].num, 111)
        self.assertEqual(dp.mol[1].res[0].spin[0].x, 1)

        # Test the new molecule 3.
        self.assertEqual(dp.mol[2].name, 3)
        self.assertEqual(dp.mol[2].res[0].num, 1)
        self.assertEqual(dp.mol[2].res[0].name, 'Ala')
        self.assertEqual(dp.mol[2].res[0].spin[0].num, 111)
        self.assertEqual(dp.mol[2].res[0].spin[0].x, 1)

        # Test the new molecule 4.
        self.assertEqual(dp.mol[3].name, 4)
        self.assertEqual(dp.mol[3].res[0].num, 1)
        self.assertEqual(dp.mol[3].res[0].name, 'Ala')
        self.assertEqual(dp.mol[3].res[0].spin[0].num, 222)
        self.assertEqual(dp.mol[3].res[0].spin[0].x, 2)


    def test_copy_molecule_within_pipe_fail(self):
        """Test the failure of the copying of the molecule data within a molecule.

        The function tested is both generic_fns.mol_res_spin.copy_molecule() and
        prompt.molecule.copy().
        """

        # Create a few molecules.
        self.molecule_fns.create('GST')
        self.molecule_fns.create('GB1')

        # Copy a non-existent molecule (MBP).
        self.assertRaises(RelaxError, self.molecule_fns.copy, mol_from='#MBP', mol_to='#IL4')

        # Copy a molecule to one which already exists.
        self.assertRaises(RelaxError, self.molecule_fns.copy, mol_from='#GST', mol_to='#GB1')


    def test_create_molecule(self):
        """Test the creation of a molecule data structure.

        The function tested is both generic_fns.mol_res_spin.create_molecule() and
        prompt.molecule.create().
        """

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Create a few new molecules.
        self.molecule_fns.create('Ap4Aase')
        self.molecule_fns.create('ATP')
        self.molecule_fns.create(mol_name='MgF4')

        # Test that the molecule names are correct.
        self.assertEqual(dp.mol[0].name, 'Ap4Aase')
        self.assertEqual(dp.mol[1].name, 'ATP')
        self.assertEqual(dp.mol[2].name, 'MgF4')


    def test_create_molecule_fail(self):
        """Test the failure of molecule creation by supplying two molecules with the same name.

        The function tested is both generic_fns.mol_res_spin.create_molecule() and
        prompt.molecule.create().
        """

        # Create the first molecule.
        self.molecule_fns.create('CaM')

        # Assert that a RelaxError occurs when the next added molecule has the same name as the first.
        self.assertRaises(RelaxError, self.molecule_fns.create, 'CaM')


    def test_delete_molecule(self):
        """Test molecule deletion.

        The function tested is both generic_fns.mol_res_spin.delete_molecule() and
        prompt.molecule.delete().
        """

        # Set up some data.
        self.setup_data()

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Delete the first molecule.
        self.molecule_fns.delete(mol_id='#Old mol')

        # Test that the first molecule is now 'New mol'.
        self.assertEqual(dp.mol[0].name, 'New mol')
        self.assertEqual(dp.mol[0].res[0].num, 1)
        self.assertEqual(dp.mol[0].res[0].name, 'Ala')
        self.assertEqual(dp.mol[0].res[0].spin[0].num, 111)
        self.assert_(hasattr(dp.mol[0].res[0].spin[0], 'x'))
        self.assertEqual(dp.mol[0].res[1].num, 5)
        self.assertEqual(dp.mol[0].res[1].name, 'Ala')
        self.assertEqual(dp.mol[0].res[1].spin[0].num, 111)
        self.assert_(hasattr(dp.mol[0].res[1].spin[0], 'x'))


    def test_delete_molecule_all(self):
        """Test the deletion of all molecules.

        The function tested is both generic_fns.mol_res_spin.delete_molecule() and
        prompt.molecule.delete().
        """

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Set up some data.
        self.setup_data()

        # Delete all molecules.
        self.molecule_fns.delete(mol_id='#Old mol')
        self.molecule_fns.delete(mol_id='#New mol')

        # Test that the first molecule defaults back to the empty container.
        self.assertEqual(dp.mol[0].name, None)
        self.assertEqual(dp.mol[0].res[0].num, None)
        self.assertEqual(dp.mol[0].res[0].name, None)
        self.assertEqual(dp.mol[0].res[0].spin[0].num, None)
        self.assertEqual(dp.mol[0].res[0].spin[0].name, None)


    def test_delete_molecule_fail(self):
        """Test the failure of molecule deletion when a residue or spin id is supplied.

        The function tested is both generic_fns.mol_res_spin.delete_molecule() and
        prompt.molecule.delete().
        """

        # Supply a spin id.
        self.assertRaises(RelaxSpinSelectDisallowError, self.molecule_fns.delete, mol_id='@2')

        # Supply a residue id.
        self.assertRaises(RelaxResSelectDisallowError, self.molecule_fns.delete, mol_id=':1')


    def test_display_molecule(self):
        """Test the display of molecular information.

        The function tested is both generic_fns.mol_res_spin.display_molecule() and
        prompt.molecule.display().
        """

        # Set up some data.
        self.setup_data()

        # The following should all work without error.
        self.molecule_fns.display()
        self.molecule_fns.display('#Old mol')
        self.molecule_fns.display(mol_id='#New mol')


    def test_display_molecule_fail(self):
        """Test the failure of the display of molecule information.

        The function tested is both generic_fns.mol_res_spin.display_molecule() and
        prompt.molecule.display().
        """

        # Set up some data.
        self.setup_data()

        # The following should fail.
        self.assertRaises(RelaxSpinSelectDisallowError, self.molecule_fns.display, '@N')
        self.assertRaises(RelaxResSelectDisallowError, self.molecule_fns.display, ':1')


    def test_name_molecule(self):
        """Test the renaming of a molecule.

        The function tested is both generic_fns.mol_res_spin.name_molecule() and
        prompt.molecule.name().
        """

        # Set up some data.
        self.setup_data()

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Rename the molecule.
        self.molecule_fns.name(mol_id='#New mol', name='K', force=True)

        # Test that the molecule has been renamed.
        self.assertEqual(dp.mol[1].name, 'K')


    def test_name_molecule_fail(self):
        """Test the failure of naming a molecule when a residue or spin id is given.

        The function tested is both generic_fns.mol_res_spin.name_molecule() and
        prompt.molecule.name().
        """

        # Try naming using a spin id.
        self.assertRaises(RelaxSpinSelectDisallowError, self.molecule_fns.name, mol_id='@111', name='K')

        # Try naming using a residue id.
        self.assertRaises(RelaxResSelectDisallowError, self.molecule_fns.name, mol_id=':1', name='K')


    def test_name_molecule_many_fail(self):
        """Test the failure of the naming of multiple molecules to the same name.

        The function tested is both generic_fns.mol_res_spin.name_molecule() and
        prompt.molecule.name().
        """

        # Set up some data.
        self.setup_data()

        # Test for the failure.
        self.assertRaises(RelaxError, self.molecule_fns.name, mol_id='#Old mol,New mol', name='K')
