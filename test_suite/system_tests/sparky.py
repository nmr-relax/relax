###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes


class Sparky(TestCase):
    """TestCase class for the functional tests for the support of Sparky in relax."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_read_peak_list(self):
        """Test the reading of an Sparky peak list."""

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(3)
        self.relax.interpreter._Residue.create(4)
        self.relax.interpreter._Residue.create(5)
        self.relax.interpreter._Residue.create(6)
        self.relax.interpreter._Spin.name(name='N')

        # Read the peak list.
        self.relax.interpreter._Relax_fit.read(file="ref_ave.list", dir=sys.path[-1] + "/test_suite/shared_data/peak_lists", relax_time=0.0, format='sparky')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0][0], 6262)
        self.assertEqual(cdp.mol[0].res[1].spin[0].intensities[0][0], 148614)
        self.assertEqual(cdp.mol[0].res[2].spin[0].intensities[0][0], 166842)
        self.assertEqual(cdp.mol[0].res[3].spin[0].intensities[0][0], 128690)
