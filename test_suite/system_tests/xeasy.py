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


class XEasy(TestCase):
    """TestCase class for the functional tests for the support of XEasy in relax."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_read_peak_list(self):
        """Test the reading of an XEasy peak list."""

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(15)
        self.relax.interpreter._Residue.create(21)
        self.relax.interpreter._Residue.create(22)
        self.relax.interpreter._Residue.create(29)
        self.relax.interpreter._Residue.create(52)
        self.relax.interpreter._Residue.create(69)
        self.relax.interpreter._Residue.create(70)
        self.relax.interpreter._Residue.create(73)
        self.relax.interpreter._Residue.create(79)
        self.relax.interpreter._Residue.create(84)
        self.relax.interpreter._Residue.create(87)
        self.relax.interpreter._Residue.create(95)
        self.relax.interpreter._Residue.create(96)
        self.relax.interpreter._Residue.create(100)
        self.relax.interpreter._Residue.create(104)
        self.relax.interpreter._Residue.create(107)
        self.relax.interpreter._Residue.create(110)
        self.relax.interpreter._Residue.create(112)
        self.relax.interpreter._Residue.create(120)
        self.relax.interpreter._Residue.create(141)
        self.relax.interpreter._Residue.create(165)
        self.relax.interpreter._Spin.name(name='N')

        # Read the peak list.
        self.relax.interpreter._Relax_fit.read(file="xeasy_r1_20ms.text", dir=sys.path[-1] + "/test_suite/shared_data/peak_lists", relax_time=0.020, format='xeasy')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0][0], 9.714e+03)
        self.assertEqual(cdp.mol[0].res[1].spin[0].intensities[0][0], 7.919e+03)
