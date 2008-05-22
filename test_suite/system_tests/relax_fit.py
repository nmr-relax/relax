###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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
import sys
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store
from generic_fns.mol_res_spin import return_spin_from_index, spin_index_loop


class Relax_fit(TestCase):
    """Class for testing various aspects specific to relaxation curve-fitting."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_curve_fitting(self):
        """Test the relaxation curve fitting C modules."""

        # Execute the script.
        self.relax.interpreter.run(script_file='test_suite/system_tests/scripts/relax_fit.py')


    def test_read_sparky(self):
        """The Sparky peak height loading test."""

        # Load the original state.
        self.relax.interpreter._State.load(state='basic_heights_T2_ncyc1', dir_name=sys.path[-1] + '/test_suite/shared_data/saved_states')

        # Create a new data pipe for the new data.
        self.relax.interpreter._Pipe.create('new', 'relax_fit')

        # Load the Lupin Ap4Aase sequence.
        self.relax.interpreter._Sequence.read(file="Ap4Aase.seq", dir=sys.path[-1] + "/test_suite/system_tests/data")

        # Read the peak heights.
        self.relax.interpreter._Relax_fit.read(file="T2_ncyc1_ave.list", dir=sys.path[-1] + "/test_suite/shared_data/curve_fitting", relax_time=0.0176)


        # Test the integrity of the data.
        #################################

        # Loop over the spins of the original data.
        for index in spin_index_loop():
            # Get the spins from both pipes.
            orig_spin, orig_id = return_spin_from_index(index, pipe='rx', return_spin_id=True)
            new_spin, new_id = return_spin_from_index(index, return_spin_id=True)

            # Check spin ids.
            self.assertEqual(orig_id, new_id)

            # Skip deselected spins.
            if not orig_spin.select:
                continue

            # Check intensities.
            self.assertEqual(orig_spin.intensities[0][0], new_spin.intensities[0][0])
