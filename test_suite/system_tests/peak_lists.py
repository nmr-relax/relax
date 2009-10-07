###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
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
from os import sep
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_loop


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

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(20)
        self.relax.interpreter._Residue.create(23)
        self.relax.interpreter._Residue.create(34)
        self.relax.interpreter._Residue.create(35)
        self.relax.interpreter._Residue.create(36)
        self.relax.interpreter._Spin.name(name='N')

        # Relaxation delays.
        delays = [0.0109016,
                  0.0218032,
                  0.0436064,
                  0.0436064,
                  0.0872128,
                  0.1744260,
                  0.3488510,
                  0.6977020,
                  1.3954000,
                  1.9949900]

        # Load the data.
        for i in range(10):
            # Read the peak intensities.
            self.relax.interpreter._Spectrum.read_intensities(file="generic_intensity.txt", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id=repr(i), int_method='height', int_col=i+2, res_num_col=2, res_name_col=3, spin_name_col=5)

            # Set the relaxation times.
            relax_fit.relax_time(time=delays[i], spectrum_id=repr(i))

        # The actual intensities.
        heights = [[1.0000, 0.9714, 0.9602, 0.9626, 0.8839, 0.8327, 0.7088, 0.5098, 0.2410, 0.1116],
                   [1.0000, 0.9789, 0.9751, 0.9762, 0.9074, 0.8532, 0.7089, 0.5170, 0.2444, 0.1537],
                   [1.0000, 0.9659, 0.9580, 0.9559, 0.9325, 0.8460, 0.7187, 0.5303, 0.2954, 0.1683],
                   [1.0000, 0.9657, 0.9389, 0.9366, 0.9331, 0.8683, 0.7169, 0.5357, 0.2769, 0.1625],
                   [1.0000, 1.0060, 0.9556, 0.9456, 0.9077, 0.8411, 0.6788, 0.4558, 0.2448, 0.1569]
        ]

        # Test the data.
        for i in range(10):
            for j in range(5):
                self.assertEqual(cdp.mol[0].res[0].spin[j].intensities[i], heights[j][i])


    def test_read_peak_list_generic2(self):
        """Test the reading of a generic peak intensity list (test number 2)."""

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(20)
        self.relax.interpreter._Residue.create(23)
        self.relax.interpreter._Residue.create(34)
        self.relax.interpreter._Residue.create(35)
        self.relax.interpreter._Residue.create(36)
        self.relax.interpreter._Spin.name(name='N')

        # Spectrum ids.
        spectrum_ids = ['0.0109016', '0.0218032', '0.0436064', '0.0436064', '0.0872128', '0.1744260', '0.3488510', '0.6977020', '1.3954000', '1.9949900']

        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="generic_intensity2.txt", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id=spectrum_ids, int_col=range(2, 12), int_method='volume', mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None)

        # The intensities.
        intensities = []
        intensities.append([1.0000, 0.9714, 0.9602, 0.9626, 0.8839, 0.8327, 0.7088, 0.5098, 0.2410, 0.1116])
        intensities.append([1.0000, 0.9789, 0.9751, 0.9762, 0.9074, 0.8532, 0.7089, 0.5170, 0.2444, 0.1537])
        intensities.append([1.0000, 0.9659, 0.9580, 0.9559, 0.9325, 0.8460, 0.7187, 0.5303, 0.2954, 0.1683])
        intensities.append([1.0000, 0.9657, 0.9389, 0.9366, 0.9331, 0.8683, 0.7169, 0.5357, 0.2769, 0.1625])
        intensities.append([1.0000, 1.0060, 0.9556, 0.9456, 0.9077, 0.8411, 0.6788, 0.4558, 0.2448, 0.1569])

        # Test the spectrum ids.
        self.assertEqual(cdp.spectrum_ids, spectrum_ids)

        # Test the data.
        index = 0
        for spin in spin_loop():
            for j in xrange(len(spin.intensities)):
                self.assertEqual(spin.intensities[j], intensities[index][j])

            # Increment the index.
            index = index + 1


    def test_read_peak_list_nmrview(self):
        """Test the reading of an NMRView peak list."""

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(70)
        self.relax.interpreter._Residue.create(72)
        self.relax.interpreter._Spin.name(name='N')

        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="cNTnC.xpk", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], -0.1694)
        self.assertEqual(cdp.mol[0].res[1].spin[0].intensities[0], -0.1142)


    def test_read_peak_list_sparky(self):
        """Test the reading of an Sparky peak list."""

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(3)
        self.relax.interpreter._Residue.create(4)
        self.relax.interpreter._Residue.create(5)
        self.relax.interpreter._Residue.create(6)
        self.relax.interpreter._Spin.name(name='N')

        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="ref_ave.list", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], 6262)
        self.assertEqual(cdp.mol[0].res[1].spin[0].intensities[0], 148614)
        self.assertEqual(cdp.mol[0].res[2].spin[0].intensities[0], 166842)
        self.assertEqual(cdp.mol[0].res[3].spin[0].intensities[0], 128690)


    def test_read_peak_list_xeasy(self):
        """Test the reading of an XEasy peak list."""

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
        self.relax.interpreter._Spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', int_method='height')

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

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(79)
        self.relax.interpreter._Spin.name(name='NE1')

        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', heteronuc='NE1', proton='HE1', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], 1.532e+04)


    def test_read_peak_list_xeasy_3(self):
        """Test the reading of an XEasy peak list (3)."""

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(100)
        self.relax.interpreter._Spin.name(name='C')

        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', heteronuc='C', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], 6.877e+03)


    def test_read_peak_list_xeasy_4(self):
        """Test the reading of an XEasy peak list (4)."""

        # Create the sequence data, and name the spins.
        self.relax.interpreter._Residue.create(107)
        self.relax.interpreter._Spin.name(name='C')

        # Read the peak list.
        self.relax.interpreter._Spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', heteronuc='C', proton='HE1', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities[0], 7.123e+03)
