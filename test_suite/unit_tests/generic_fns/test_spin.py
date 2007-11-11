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
from generic_fns import residue, spin
from relax_errors import RelaxError, RelaxNoPipeError



class Test_spin(TestCase):
    """Unit tests for the functions of the 'generic_fns.spin' module."""


    def setUp(self):
        """Set up for all the residue unit tests."""

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
        """Function for setting up some data for the unit tests."""

        # Alias the relax data store.
        cdp = relax_data_store['orig']

        # Name the first molecule.
        cdp.mol[0].name = 'Old mol'

        # Create the first residue and add some data to its spin container.
        cdp.mol[0].res.add_item(1, 'Ala')
        cdp.mol[0].res[0].spin[0].num = 111
        cdp.mol[0].res[0].spin[0].name = 'C8'
        cdp.mol[0].res[0].spin[0].x = 1

        # Create a second residue.
        cdp.mol[0].res.add_item(2, 'Arg')
        cdp.mol[0].res[0].spin[0].num = 78
        cdp.mol[0].res[0].spin[0].name = 'NH'

        # Create a second molecule.
        cdp.mol.add_item('New mol')

        # Create the first and second residue of the second molecule and add some data to its spin container.
        cdp.mol[1].res.add_item(5, 'Lys')
        cdp.mol[1].res[0].spin[0].num = 239
        cdp.mol[1].res[0].spin[0].name = 'NH'
        cdp.mol[1].res.add_item(6, 'Thr')
        cdp.mol[1].res[1].spin.add_item(3239, 'NH')


    def test_copy_between_molecules(self):
        """Test the copying of the spin data between different molecules.

        The function used is generic_fns.spin.copy().
        """

        # Set up the data.
        self.setup_data()

        # Copy the spin '111' from the first molecule, first residue to the second molecule, fifth residue.
        spin.copy(spin_from='#Old mol:1@111', spin_to='#New mol:5@334')

        # Test the original spin.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].name, 'C8')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 1)

        # Test the new spin.
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].num, 239)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].name, 'NH')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[1].num, 334)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].name, 'C8')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[1].x, 1)


    def test_copy_between_residues(self):
        """Test the copying of the spin data between different residues.

        The function used is generic_fns.spin.copy().
        """

        # Set up the data.
        self.setup_data()

        # Copy the spin '111' from the first residue to the fifth residue.
        spin.copy(spin_from='#Old mol:1@111', spin_to='#Old mol:2')

        # Test the original spin.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 'C8')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 1)

        # Test the new spin.
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Arg')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].num, 'C8')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].x, 1)


    def test_copy_between_pipes(self):
        """Test the copying of the spin data between different data pipes.

        The function used is generic_fns.spin.copy().
        """

        # Set up the data.
        self.setup_data()

        # Copy the spin data.
        spin.copy(spin_from='#Old mol:1@111', pipe_to='test')

        # Change the first spin's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2

        # Test the original spin.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 2)

        # Test the new spin.
        self.assertEqual(relax_data_store['test'].mol[0].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].spin[0].x, 1)


    def test_copy_between_pipes_fail(self):
        """Test the copying of the spin data between different data pipes.

        The function used is generic_fns.spin.copy().
        """

        # Set up the data.
        self.setup_data()

        # Copy the spin to the second data pipe.
        self.assertRaises(RelaxNoPipeError, spin.copy, spin_from='#Old mol:1@111', pipe_to='test2')



    def test_copy_fail(self):
        """Test the failure of the copying of the spin data.

        The function used is generic_fns.spin.copy().
        """

        # Set up the data.
        self.setup_data()

        # Copy a non-existent residue (1 Met, @111).
        self.assertRaises(RelaxError, spin.copy, spin_from=':Met@111', spin_to=':2,Gly')

        # Copy a non-existent spin (1 Ala, @234).
        self.assertRaises(RelaxError, spin.copy, spin_from=':Ala@234', spin_to=':2,Gly')

        # Copy a spin to a number which already exists.
        self.assertRaises(RelaxError, spin.copy, spin_from=':1', spin_to=':2@78')



