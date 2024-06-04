###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
# Copyright (C) 2013 Troels E. Linnet                                         #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""The module for the system tests for chemical shift support in relax."""


# Python module imports.
from os import sep

# relax module imports.
from pipe_control.mol_res_spin import spin_loop
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Chemical_shift(SystemTestCase):
    """System test class for checking the handling of chemical shifts."""


    def setUp(self):
        """Set up for all the system tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('cs', 'mf')


    def test_read_nmrpipe_seriestab(self):
        """Test the reading of chemical shifts from an NMRPipe seriesTab peak list."""

        # Read the spins from peak list.
        self.interpreter.spectrum.read_spins(file="seriesTab.ser", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists')

        # Read the chemical shift from the list.
        self.interpreter.chemical_shift.read(file="seriesTab.ser", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists')

        # Test the data.
        cs = [128.374, 127.066, 124.523]
        i = 0
        for spin in spin_loop():
            # Check the shift.
            self.assertEqual(spin.chemical_shift, cs[i])

            # Increment the index.
            i += 1


    def test_read_nmrpipe_seriestab_multi(self):
        """Test the reading of chemical shifts from an NMRPipe seriesTab peak list with multi columns."""

        # Read the spins from peak list.
        self.interpreter.spectrum.read_spins(file="seriesTab_multi.ser", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists')

        # Read the chemical shift from the list.
        self.interpreter.chemical_shift.read(file="seriesTab_multi.ser", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists')

        # Test the data.
        cs = [115.994, 125.899, 123.001, 120.839, 128.998]
        i = 0
        for spin in spin_loop():
            # Check the shift.
            self.assertEqual(spin.chemical_shift, cs[i])

            # Increment the index.
            i += 1


    def test_read_nmrview(self):
        """Test the reading of chemical shifts from an NMRView peak list."""

        # Create the sequence data, and name the spins.
        self.interpreter.spin.create(res_num=70, spin_name='N')
        self.interpreter.spin.create(res_num=70, spin_name='HN')
        self.interpreter.spin.create(res_num=72, spin_name='N')
        self.interpreter.spin.create(res_num=72, spin_name='HN')

        # Read the peak list.
        self.interpreter.chemical_shift.read(file="cNTnC.xpk", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists')

        # Test the data.
        cs = [116.37241, 10.75274, 126.41302, 9.67752]
        i = 0
        for spin in spin_loop():
            # Check the shift.
            self.assertEqual(spin.chemical_shift, cs[i])

            # Increment the index.
            i += 1


    def test_read_sparky(self):
        """Test the reading of chemical shifts from a Sparky peak list."""

        # Create the sequence data, and name the spins.
        for res_num in [3, 4, 5, 6, 40]:
            self.interpreter.spin.create(res_num=res_num, spin_name='N')
            self.interpreter.spin.create(res_num=res_num, spin_name='HN')
        self.interpreter.spin.create(res_num=40, spin_name='NE1')
        self.interpreter.spin.create(res_num=40, spin_name='HE1')

        # Load the peak list.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists'
        self.interpreter.chemical_shift.read(file='ref_ave.list', dir=path)

        # Test the data.
        cs = [122.454, 8.397, 111.978, 8.720, 115.069, 8.177, 120.910, 8.813, 123.335, 8.005, 130.204, 10.294]
        i = 0
        for spin in spin_loop():
            # No data.
            if i > 12:
                self.assertTrue(not hasattr(spin, 'chemical_shift'))

            # Check the shift.
            self.assertEqual(spin.chemical_shift, cs[i])

            # Increment the index.
            i += 1


    def test_read_xeasy(self):
        """Test the reading of chemical shifts from a XEasy peak list."""

        # Create the sequence data, and name the spins.
        for res_num in [21, 96, 104, 110]:
            self.interpreter.spin.create(res_num=res_num, spin_name='N')
            self.interpreter.spin.create(res_num=res_num, spin_name='HN')
        self.interpreter.spin.create(res_num=79, spin_name='NE1')
        self.interpreter.spin.create(res_num=79, spin_name='HE1')

        # Load the peak list.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'peak_lists'
        self.interpreter.chemical_shift.read(file='xeasy_r1_20ms.text', dir=path)

        # Test the data.
        cs = [134.221, 10.014, 118.450, 8.364, 127.582, 9.211, 129.041, 9.882, 132.592, 10.481]
        i = 0
        for spin in spin_loop():
            # No data.
            if i > 10:
                self.assertTrue(not hasattr(spin, 'chemical_shift'))

            # Check the shift.
            self.assertEqual(spin.chemical_shift, cs[i])

            # Increment the index.
            i += 1
