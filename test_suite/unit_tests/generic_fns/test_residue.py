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
from relax_errors import RelaxError, RelaxNoRunError, RelaxRunError



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


    def test_delete(self):
        """Test the deletion of a residue.

        The function used is generic_fns.residues.delete().
        """

        # Create the first residue and add some data to its spin container.
        residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Delete the residue.
        residue.delete(res_num=1, res_name='Ala')

        # Test that the residue no longer exists (and defaults back to the empty residue).
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, None)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, None)
        self.assertNotEqual(relax_data_store['orig'].mol[0].res[1].spin[0].num, 111)
        self.assert_(not hasattr(relax_data_store['orig'].mol[0].res[1].spin[0], 'x'))


    def test_delete_fail(self):
        """Test the failure of the deletion of a non-existant residue.

        The function used is generic_fns.residues.delete().
        """

        # Delete a non-existant residue (1 Met).
        self.assertRaises(RelaxError, residue.delete, 1, 'Met')
