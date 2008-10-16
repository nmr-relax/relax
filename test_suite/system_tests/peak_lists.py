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


class NMRView(TestCase):
    """TestCase class for the functional tests for the support of NMRView in relax."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_read_peak_list(self):
        """Test the reading of an NMRView peak list."""

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(70)
        self.relax.interpreter._Residue.create(72)
        self.relax.interpreter._Spin.name(name='N')

        # Read the peak list.
        self.relax.interpreter._Relax_fit.read(file="cNTnC.xpk", dir=sys.path[-1] + "/test_suite/shared_data/peak_lists", relax_time=0.0176, format='nmrview')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0][0], -6.88333129883)
        self.assertEqual(cdp.mol[0].res[1].spin[0].intensities[0][0], -5.49038267136)


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
        self.assertEqual(cdp.mol[0].res[2].spin[0].intensities[0][0], 1.356e+04)
        self.assertEqual(cdp.mol[0].res[3].spin[0].intensities[0][0], 9.884e+03)
        self.assertEqual(cdp.mol[0].res[4].spin[0].intensities[0][0], 2.041e+04)
        self.assertEqual(cdp.mol[0].res[5].spin[0].intensities[0][0], 9.305e+03)
        self.assertEqual(cdp.mol[0].res[6].spin[0].intensities[0][0], 3.154e+04)
        self.assertEqual(cdp.mol[0].res[7].spin[0].intensities[0][0], 9.180e+03)
        self.assertEqual(cdp.mol[0].res[8].spin[0].intensities[0][0], 1.532e+04)
