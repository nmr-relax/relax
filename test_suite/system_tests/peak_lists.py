###############################################################################
#                                                                             #
# Copyright (C) 2008-2010 Edward d'Auvergne                                   #
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

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_loop
from status import Status; status = Status()


class Peak_lists(SystemTestCase):
    """TestCase class for the functional tests for the support of different peak intensity files."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_bug_17276_peak_lists(self):
        """Test catching bug #17276, the duplicated peak list reading failure submitted by Leanne Minall."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'bug_17276_peak_lists.py')


    def test_ccpn_analysis(self):
        """Test bug #17341 (https://gna.org/bugs/index.php?17341), the CCPN Analysis 2.1 peak list reading submitted by Madeleine Strickland."""

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'peak_lists'+sep+'ccpn_analysis.py')

        # Spectrum names.
        names = ['T1A_0010', 'T1A_0020', 'T1A_0030', 'T1A_0050', 'T1A_0070', 'T1A_0100', 'T1A_0150', 'T1A_0200', 'T1A_0300', 'T1A_0400', 'T1A_0600', 'T1A_0800', 'T1A_1000', 'T1A_1200']

        # Relaxation times (in seconds).
        times = [0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.2]

        # Check the spectrum IDs and relaxation times.
        for i in range(len(times)):
            self.assertEqual(cdp.spectrum_ids[i], names[i])
            self.assertEqual(cdp.relax_times[names[i]], times[i])

        # The peak heights.
        heights = [
                [1.41e06, 1.33e06, 1.31e06, 1.31e06, 1.28e06, 1.20e06, 1.18e06, 1.07e06, 9.70e05, 8.47e05, 7.00e05, 5.25e05, 4.23e05, 3.10e05],
                [1.79e06, 1.76e06, 1.71e06, 1.70e06, 1.66e06, 1.56e06, 1.51e06, 1.41e06, 1.24e06, 1.11e06, 8.43e05, 6.79e05, 5.04e05, 4.18e05]
        ]

        # Check the heights.
        for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
            print spin
            # The data.
            if res_num == 1501:
                index = 0
            elif res_num == 1504:
                index = 1

            # No data.
            else:
                # There should be no intensity data.
                self.assert_(not hasattr(spin, 'intensities'))

                # Do not perform the height checks.
                continue

            # Check the data.
            self.assert_(hasattr(spin, 'intensities'))

            # Check the values.
            for i in range(len(times)):
                self.assertEqual(spin.intensities[names[i]], heights[index][i])


    def test_read_peak_list_generic(self):
        """Test the reading of a generic peak intensity list."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(20, 'GLY')
        self.interpreter.residue.create(23, 'ALA')
        self.interpreter.residue.create(34, 'CYS')
        self.interpreter.residue.create(35, 'MET')
        self.interpreter.residue.create(36, 'LYS')
        self.interpreter.spin.name(name='N')

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
            self.interpreter.spectrum.read_intensities(file="generic_intensity.txt", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id=repr(i), int_method='height', int_col=i+3, res_num_col=1, res_name_col=2)

            # Set the relaxation times.
            self.interpreter.relax_fit.relax_time(time=delays[i], spectrum_id=repr(i))

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
                self.assertEqual(cdp.mol[0].res[j].spin[0].intensities[repr(i)], heights[j][i])


    def test_read_peak_list_nmrview(self):
        """Test the reading of an NMRView peak list."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(70)
        self.interpreter.residue.create(72)
        self.interpreter.spin.name(name='N')

        # Read the peak list.
        self.interpreter.spectrum.read_intensities(file="cNTnC.xpk", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities.values()[0], -0.1694)
        self.assertEqual(cdp.mol[0].res[1].spin[0].intensities.values()[0], -0.1142)


    def test_read_peak_list_sparky(self):
        """Test the reading of an Sparky peak list."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(3)
        self.interpreter.residue.create(4)
        self.interpreter.residue.create(5)
        self.interpreter.residue.create(6)
        self.interpreter.spin.name(name='N')

        # Read the peak list.
        self.interpreter.spectrum.read_intensities(file="ref_ave.list", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities.values()[0], 6262)
        self.assertEqual(cdp.mol[0].res[1].spin[0].intensities.values()[0], 148614)
        self.assertEqual(cdp.mol[0].res[2].spin[0].intensities.values()[0], 166842)
        self.assertEqual(cdp.mol[0].res[3].spin[0].intensities.values()[0], 128690)


    def test_read_peak_list_xeasy(self):
        """Test the reading of an XEasy peak list."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(15)
        self.interpreter.residue.create(21)
        self.interpreter.residue.create(22)
        self.interpreter.residue.create(29)
        self.interpreter.residue.create(52)
        self.interpreter.residue.create(69)
        self.interpreter.residue.create(70)
        self.interpreter.residue.create(73)
        self.interpreter.residue.create(79)
        self.interpreter.residue.create(84)
        self.interpreter.residue.create(87)
        self.interpreter.residue.create(95)
        self.interpreter.residue.create(96)
        self.interpreter.residue.create(100)
        self.interpreter.residue.create(104)
        self.interpreter.residue.create(107)
        self.interpreter.residue.create(110)
        self.interpreter.residue.create(112)
        self.interpreter.residue.create(120)
        self.interpreter.residue.create(141)
        self.interpreter.residue.create(165)
        self.interpreter.spin.name(name='N')

        # Read the peak list.
        self.interpreter.spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[ 0].spin[0].intensities.values()[0], 9.714e+03)
        self.assertEqual(cdp.mol[0].res[ 1].spin[0].intensities.values()[0], 7.919e+03)
        self.assertEqual(cdp.mol[0].res[ 2].spin[0].intensities.values()[0], 1.356e+04)
        self.assertEqual(cdp.mol[0].res[ 3].spin[0].intensities.values()[0], 9.884e+03)
        self.assertEqual(cdp.mol[0].res[ 4].spin[0].intensities.values()[0], 2.041e+04)
        self.assertEqual(cdp.mol[0].res[ 5].spin[0].intensities.values()[0], 9.305e+03)
        self.assertEqual(cdp.mol[0].res[ 6].spin[0].intensities.values()[0], 3.154e+04)
        self.assertEqual(cdp.mol[0].res[ 7].spin[0].intensities.values()[0], 9.180e+03)
        self.assertEqual(cdp.mol[0].res[ 9].spin[0].intensities.values()[0], 1.104e+04)
        self.assertEqual(cdp.mol[0].res[10].spin[0].intensities.values()[0], 7.680e+03)
        self.assertEqual(cdp.mol[0].res[11].spin[0].intensities.values()[0], 5.206e+03)
        self.assertEqual(cdp.mol[0].res[12].spin[0].intensities.values()[0], 2.863e+04)
        self.assertEqual(cdp.mol[0].res[14].spin[0].intensities.values()[0], 9.271e+03)
        self.assertEqual(cdp.mol[0].res[15].spin[0].intensities.values()[0], 7.919e+03)
        self.assertEqual(cdp.mol[0].res[16].spin[0].intensities.values()[0], 9.962e+03)
        self.assertEqual(cdp.mol[0].res[17].spin[0].intensities.values()[0], 1.260e+04)
        self.assertEqual(cdp.mol[0].res[18].spin[0].intensities.values()[0], 1.545e+04)
        self.assertEqual(cdp.mol[0].res[19].spin[0].intensities.values()[0], 1.963e+04)
        self.assertEqual(cdp.mol[0].res[20].spin[0].intensities.values()[0], 1.918e+04)


    def test_read_peak_list_xeasy_2(self):
        """Test the reading of an XEasy peak list (2)."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(79)
        self.interpreter.spin.name(name='NE1')

        # Read the peak list.
        self.interpreter.spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', heteronuc='NE1', proton='HE1', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities.values()[0], 1.532e+04)


    def test_read_peak_list_xeasy_3(self):
        """Test the reading of an XEasy peak list (3)."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(100)
        self.interpreter.spin.name(name='C')

        # Read the peak list.
        self.interpreter.spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', heteronuc='C', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities.values()[0], 6.877e+03)


    def test_read_peak_list_xeasy_4(self):
        """Test the reading of an XEasy peak list (4)."""

        # Create the sequence data, and name the spins.
        self.interpreter.residue.create(107)
        self.interpreter.spin.name(name='C')

        # Read the peak list.
        self.interpreter.spectrum.read_intensities(file="xeasy_r1_20ms.text", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists', spectrum_id='test', heteronuc='C', proton='HE1', int_method='height')

        # Test the data.
        self.assertEqual(cdp.mol[0].res[0].spin[0].intensities.values()[0], 7.123e+03)
