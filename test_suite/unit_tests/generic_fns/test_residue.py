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
from data.pipe_container import PipeContainer
from generic_fns import residue
from relax_errors import RelaxError, RelaxNoRunError, RelaxRunError, RelaxSpinSelectDisallowError


class Test_residue(TestCase):
    """Unit tests for the functions of the 'generic_fns.residue' module."""

    def setUp(self):
        """Set up for all the residue unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_copy(self):
        """Test the copying of the residue data.

        The function used is generic_fns.residues.copy().
        """

        # Create the first residue and add some data to its spin container.
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Copy the residue a few times.
        residue.copy(res_num_from=1, res_num_to=2)
        residue.copy(res_num_from=1, res_name_from='Ala', res_num_to=3)

        # Change the first residue's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2

        # Copy the residue once more.
        residue.copy(res_num_from=1, res_num_to=4, res_name_to='Met')

        # Test the new residue 2.
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].x, 1)

        # Test the new residue 3.
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].num, 3)
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].spin[0].x, 1)

        # Test the new residue 4.
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].num, 4)
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].name, 'Met')
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].spin[0].x, 2)


    def test_copy_fail(self):
        """Test the failure of the copying of the residue data.

        The function used is generic_fns.residues.copy().
        """

        # Create the a few residues.
        residue.create(1, 'Ala')
        residue.create(-1, 'His')

        # Copy a non-existant residue (1 Met).
        self.assertRaises(RelaxError, residue.copy, 1, 'Met', 2, 'Gly')

        # Copy a residue to a number which already exists.
        self.assertRaises(RelaxError, residue.copy, 1, 'Ala', -1, 'Gly')


    def test_creation(self):
        """Test the creation of a residue.

        The function used is generic_fns.residues.create().
        """

        # Create a few new residues.
        residue.create(1, 'Ala')
        residue.create(2, 'Leu')
        residue.create(-3, 'Ser')

        # Test that the residue numbers are correct.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].num, -3)

        # Test that the residue names are correct.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Leu')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].name, 'Ser')


    def test_creation_fail(self):
        """Test the failure of residue creation (by supplying two residues with the same number).

        The function used is generic_fns.residue.create().
        """

        # Create the first residue.
        residue.create(1, 'Ala')

        # Assert that a RelaxError occurs when the next added residue has the same sequence number as the first.
        self.assertRaises(RelaxError, residue.create, 1, 'Ala')


    def test_delete_name(self):
        """Test residue deletion using residue name identifiers.

        The function used is generic_fns.residues.delete().
        """

        # Create some residues and add some data to the spin containers.
        residue.create(1, 'Ala')
        residue.create(2, 'Ala')
        residue.create(3, 'Ala')
        residue.create(4, 'Gly')
        relax_data_store['orig'].mol[0].res[3].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[3].spin[0].x = 1

        # Delete the first residue.
        residue.delete(res_id=':Ala')

        # Test that the first residue is 4 Gly.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 4)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Gly')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 111)
        self.assert_(hasattr(relax_data_store['orig'].mol[0].res[0].spin[0], 'x'))


    def test_delete_num(self):
        """Test residue deletion using residue number identifiers.

        The function used is generic_fns.residues.delete().
        """

        # Create some residues and add some data to the spin containers.
        residue.create(1, 'Ala')
        residue.create(2, 'Ala')
        residue.create(3, 'Ala')
        residue.create(4, 'Gly')
        relax_data_store['orig'].mol[0].res[3].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[3].spin[0].x = 1

        # Delete the first residue.
        residue.delete(res_id=':1')

        # Test that the sequence.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 3)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].num, 4)
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].name, 'Gly')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].spin[0].num, 111)
        self.assert_(hasattr(relax_data_store['orig'].mol[0].res[2].spin[0], 'x'))


    def test_delete_all(self):
        """Test the deletion of all residues.

        The function used is generic_fns.residues.delete().
        """

        # Create some residues and add some data to the spin containers.
        residue.create(1, 'Ala')
        residue.create(2, 'Ala')
        residue.create(3, 'Ala')
        residue.create(4, 'Ala')
        relax_data_store['orig'].mol[0].res[3].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[3].spin[0].x = 1

        # Delete all residues.
        residue.delete(res_id=':1-4')

        # Test that the first residue defaults back to the empty residue.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, None)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, None)


    def test_delete_shift(self):
        """Test the deletion of multiple residues.

        The function used is generic_fns.residues.delete().
        """

        # Create some residues and add some data to the spin containers.
        residue.create(1, 'Ala')
        residue.create(2, 'Ala')
        residue.create(3, 'Ala')
        residue.create(4, 'Ala')
        relax_data_store['orig'].mol[0].res[3].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[3].spin[0].x = 1

        # Delete the first and third residues.
        residue.delete(res_id=':1,3')

        # Test that the remaining residues.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 4)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].num, 111)
        self.assert_(hasattr(relax_data_store['orig'].mol[0].res[1].spin[0], 'x'))


    def test_delete_fail(self):
        """Test the failure of residue deletion when an atom id is supplied.

        The function used is generic_fns.residues.delete().
        """

        # Supply an atom id.
        self.assertRaises(RelaxSpinSelectDisallowError, residue.delete, res_id='@2')


    def test_rename(self):
        """Test the renaming of a residue.

        The function tested is generic_fns.residue.rename().
        """

        # Create the first residue and add some data to its spin container.
        residue.create(-10, 'His')

        # Rename the residue.
        residue.rename(res_id=':-10', new_name='K')

        # Test that the residue has been renamed.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'K')


    def test_rename_many(self):
        """Test the renaming of multiple residues.

        The function used is generic_fns.residue.rename().
        """

        # Create the first residue and add some data to its spin container.
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111

        # Copy the residue a few times.
        residue.copy(res_num_from=1, res_num_to=2)
        residue.copy(res_num_from=1, res_name_from='Ala', res_num_to=3)

        # Change the first residue's data.
        relax_data_store['orig'].mol[0].res[0].name = 'His'

        # Copy the residue once more.
        residue.copy(res_num_from=1, res_num_to=4, res_name_to='Met')

        # Rename all alanines.
        residue.rename(res_id=':Ala', new_name='Gln')

        # Test the renaming of alanines.
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Gln')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].name, 'Gln')

        # Test that the other residues have not changed.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'His')
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].name, 'Met')


    def test_rename_no_spin(self):
        """Test the failure of renaming a residue when a spin id is given.

        The function tested is generic_fns.residue.rename().
        """

        # Try renaming using a atom id.
        self.assertRaises(RelaxSpinSelectDisallowError, residue.rename, res_id='@111', new_name='K')


    def test_renumber(self):
        """Test the renumbering of a residue.

        The function tested is generic_fns.residue.renumber().
        """

        # Create the first residue and add some data to its spin container.
        residue.create(-10, 'His')

        # Rename the residue.
        residue.renumber(res_id=':-10', new_number=10)

        # Test that the residue has been renumbered.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 10)


    def test_renumber_many_fail(self):
        """Test the renaming of multiple residues.

        The function used is generic_fns.residue.renumber().
        """

        # Create the first residue and add some data to its spin container.
        residue.create(1, 'Ala')

        # Copy the residue a few times.
        residue.copy(res_num_from=1, res_num_to=2)
        residue.copy(res_num_from=1, res_name_from='Ala', res_num_to=3)

        # Change the first residue's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].name = 'His'

        # Copy the residue once more.
        residue.copy(res_num_from=1, res_num_to=4, res_name_to='Met')

        # Try renumbering all alanines.
        self.assertRaises(RelaxError, residue.renumber, res_id=':Ala', new_number=10)


    def test_renumber_no_spin(self):
        """Test the failure of renaming a residue when a spin id is given.

        The function tested is generic_fns.residue.renumber().
        """

        # Try renaming using a atom id.
        self.assertRaises(RelaxSpinSelectDisallowError, residue.renumber, res_id='@111', new_number=10)
