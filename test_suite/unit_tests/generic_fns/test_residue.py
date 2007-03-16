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
from data import Data
from data.pipe_container import PipeContainer
from generic_fns import residue
from relax_errors import RelaxError, RelaxNoRunError, RelaxRunError


# The relax data storage object.
relax_data_store = Data()


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
