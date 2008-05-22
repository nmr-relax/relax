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
from unittest import TestCase
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()



class Generic(TestCase):
    """Class for testing various aspects specific to relaxation curve-fitting."""

    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_value_diff(self):
        """S2 difference stored in a new data pipe."""

        # Init.
        pipes = ['orig1', 'orig2', 'new']
        s2 = [0.9, 0.7, None]

        # Loop over the data pipes to create and fill.
        for i in xrange(3):
            # Create the data pipe.
            self.relax.interpreter._Pipe.create(pipes[i], 'mf')

            # Load the Lupin Ap4Aase sequence.
            self.relax.interpreter._Sequence.read(file="Ap4Aase.seq", dir=sys.path[-1] + "/test_suite/system_tests/data")

            # Only select residue 8.
            self.relax.interpreter._Select.spin(spin_id=':8', change_all=True)

            # Set the order parameter value.
            if s2[i]:
                self.relax.interpreter._Value.set(s2[i], 'S2', spin_id=':8')

        # Calculate the difference and assign it to residue 8 (located in position 7).
        diff = ds['orig1'].mol[0].res[7].spin[0].s2 - ds['orig2'].mol[0].res[7].spin[0].s2
        self.relax.interpreter._Value.set(diff, 'S2', spin_id=':8')

        # Test if the difference is 0.2!
        self.assertAlmostEqual(ds['new'].mol[0].res[7].spin[0].s2, 0.2)
