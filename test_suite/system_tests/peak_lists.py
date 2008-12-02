###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
# Copyright (C) 2008 Sebastien Morin                                          #
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


class Peak_lists(TestCase):
    """TestCase class for the functional tests for the support of different peak intensity files."""
        
    def setUp(self):
        """Set up for all the functional tests."""
        
        # Create a data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')
        
        
    def tearDown(self):
        """Reset the relax data storage object."""
        
        ds.__reset__()
        
        
    def test_read_peak_list_generic(self):
        """Test the reading of a generic peak intensity list."""
        
        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(20)
        self.relax.interpreter._Residue.create(23)
        self.relax.interpreter._Residue.create(34)
        self.relax.interpreter._Residue.create(35)
        self.relax.interpreter._Residue.create(36)
        self.relax.interpreter._Spin.name(name='N')
        
        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="generic.txt", dir=sys.path[-1] + "/test_suite/shared_data/peak_lists", spectrum_id='test', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], 1.0000)


    def test_read_peak_list_nmrview(self):
        """Test the reading of an NMRView peak list."""

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(70)
        self.relax.interpreter._Residue.create(72)
        self.relax.interpreter._Spin.name(name='N')

        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="cNTnC.xpk", dir=sys.path[-1] + "/test_suite/shared_data/peak_lists", spectrum_id='test', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], -0.1694)
        self.assertEqual(cdp.mol[0].res[1].spin[0].intensities[0], -0.1142)


    def test_read_peak_list_sparky(self):
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
        self.relax.interpreter._Spectrum.read_intensities(file="ref_ave.list", dir=sys.path[-1] + "/test_suite/shared_data/peak_lists", spectrum_id='test', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], 6262)
        self.assertEqual(cdp.mol[0].res[1].spin[0].intensities[0], 148614)
        self.assertEqual(cdp.mol[0].res[2].spin[0].intensities[0], 166842)
        self.assertEqual(cdp.mol[0].res[3].spin[0].intensities[0], 128690)


    def test_read_peak_list_xeasy(self):
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
        self.relax.interpreter._Spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=sys.path[-1] + "/test_suite/shared_data/peak_lists", spectrum_id='test', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], 9.714e+03)
        self.assertEqual(cdp.mol[0].res[1].spin[0].intensities[0], 7.919e+03)
        self.assertEqual(cdp.mol[0].res[2].spin[0].intensities[0], 1.356e+04)
        self.assertEqual(cdp.mol[0].res[3].spin[0].intensities[0], 9.884e+03)
        self.assertEqual(cdp.mol[0].res[4].spin[0].intensities[0], 2.041e+04)
        self.assertEqual(cdp.mol[0].res[5].spin[0].intensities[0], 9.305e+03)
        self.assertEqual(cdp.mol[0].res[6].spin[0].intensities[0], 3.154e+04)
        self.assertEqual(cdp.mol[0].res[7].spin[0].intensities[0], 9.180e+03)
        self.assertEqual(cdp.mol[0].res[9].spin[0].intensities[0], 1.104e+04)
        self.assertEqual(cdp.mol[0].res[10].spin[0].intensities[0], 7.680e+03)
        self.assertEqual(cdp.mol[0].res[11].spin[0].intensities[0], 5.206e+03)
        self.assertEqual(cdp.mol[0].res[12].spin[0].intensities[0], 2.863e+04)
        self.assertEqual(cdp.mol[0].res[14].spin[0].intensities[0], 9.271e+03)
        self.assertEqual(cdp.mol[0].res[15].spin[0].intensities[0], 7.919e+03)
        self.assertEqual(cdp.mol[0].res[16].spin[0].intensities[0], 9.962e+03)
        self.assertEqual(cdp.mol[0].res[17].spin[0].intensities[0], 1.260e+04)
        self.assertEqual(cdp.mol[0].res[18].spin[0].intensities[0], 1.545e+04)
        self.assertEqual(cdp.mol[0].res[19].spin[0].intensities[0], 1.963e+04)
        self.assertEqual(cdp.mol[0].res[20].spin[0].intensities[0], 1.918e+04)


    def test_read_peak_list_xeasy_2(self):
        """Test the reading of an XEasy peak list (2)."""

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(79)
        self.relax.interpreter._Spin.name(name='NE1')

        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=sys.path[-1] + "/test_suite/shared_data/peak_lists", spectrum_id='test', heteronuc='NE1', proton='HE1', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], 1.532e+04)


    def test_read_peak_list_xeasy_3(self):
        """Test the reading of an XEasy peak list (3)."""

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(100)
        self.relax.interpreter._Spin.name(name='C')

        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=sys.path[-1] + "/test_suite/shared_data/peak_lists", spectrum_id='test', heteronuc='C', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], 6.877e+03)


    def test_read_peak_list_xeasy_4(self):
        """Test the reading of an XEasy peak list (4)."""

        # Get the current data pipe.
        cdp = pipes.get_pipe()

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(107)
        self.relax.interpreter._Spin.name(name='C')

        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=sys.path[-1] + "/test_suite/shared_data/peak_lists", spectrum_id='test', heteronuc='C', proton='HE1', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], 7.123e+03)
