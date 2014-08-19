###############################################################################
#                                                                             #
# Copyright (C) 2007-2013 Edward d'Auvergne                                   #
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

# Python module imports.
from unittest import TestCase

# relax module imports.
from pipe_control import pipes, spectrometer, value
from specific_analyses.relax_disp.data import generate_r20_key, set_exp_type
from test_suite.unit_tests.value_testing_base import Value_base_class



class Test_value(Value_base_class, TestCase):
    """Unit tests for the functions of the 'pipe_control.value' module."""

    # Place the pipe_control.value module into the class namespace.
    value_fns = value


    def test_partition_params1(self):
        """First test of the pipe_control.value.partition_params() function."""

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # The parameters and values.
        param = ['s2']
        val = [0.8]

        # Partition.
        spin_params, spin_values, other_params, other_values = value.partition_params(val, param)

        # Tests.
        self.assertEqual(spin_params, ['s2'])
        self.assertEqual(spin_values, [0.8])
        self.assertEqual(other_params, [])
        self.assertEqual(other_values, [])


    def test_partition_params2(self):
        """Second test of the pipe_control.value.partition_params() function."""

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # The parameters and values.
        param = ['Dx']
        val = [1e7]

        # Partition.
        spin_params, spin_values, other_params, other_values = value.partition_params(val, param)

        # Tests.
        self.assertEqual(spin_params, [])
        self.assertEqual(spin_values, [])
        self.assertEqual(other_params, ['Dx'])
        self.assertEqual(other_values, [1e7])


    def test_partition_params3(self):
        """Third test of the pipe_control.value.partition_params() function."""

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # The parameters and values.
        param = ['Dx', 's2']
        val = [1e7, 0.8]

        # Partition.
        spin_params, spin_values, other_params, other_values = value.partition_params(val, param)

        # Tests.
        self.assertEqual(spin_params, ['s2'])
        self.assertEqual(spin_values, [0.8])
        self.assertEqual(other_params, ['Dx'])
        self.assertEqual(other_values, [1e7])


    def test_partition_params4(self):
        """Forth test of the pipe_control.value.partition_params() function."""

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # The parameters and values.
        param = ['Dx', 's2', 'csa']
        val = [1e7, 0.8, -160e-6]

        # Partition.
        spin_params, spin_values, other_params, other_values = value.partition_params(val, param)

        # Tests.
        self.assertEqual(spin_params, ['s2', 'csa'])
        self.assertEqual(spin_values, [0.8, -160e-6])
        self.assertEqual(other_params, ['Dx'])
        self.assertEqual(other_values, [1e7])


    def test_partition_params5(self):
        """Fifth test of the pipe_control.value.partition_params() function."""

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # The parameters and values.
        param = ['Dpar', 's2', 'Dper', 'csa', 'theta']
        val = [1e7, 0.8, 2e7, -160e-6, 0.13]

        # Partition.
        spin_params, spin_values, other_params, other_values = value.partition_params(val, param)

        # Tests.
        self.assertEqual(spin_params, ['s2', 'csa'])
        self.assertEqual(spin_values, [0.8, -160e-6])
        self.assertEqual(other_params, ['Dpar', 'Dper', 'theta'])
        self.assertEqual(other_values, [1e7, 2e7, 0.13])


    def test_partition_params6(self):
        """Sixth test of the pipe_control.value.partition_params() function."""

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # The parameters and values.
        param = []
        val = []

        # Partition.
        spin_params, spin_values, other_params, other_values = value.partition_params(val, param)

        # Tests.
        self.assertEqual(spin_params, [])
        self.assertEqual(spin_values, [])
        self.assertEqual(other_params, [])
        self.assertEqual(other_values, [])


    def test_value_set_r1_rit(self):
        """Test of the pipe_control.value.set() function."""

        # Set the current data pipe to 'mf'.
        pipes.switch('relax_disp')

        # Set variables.
        exp_type = 'R1rho'
        frq = 800.1 * 1E6

        # Set an experiment type to the pipe.
        set_exp_type(spectrum_id='test', exp_type=exp_type)

        # Set a frequency to loop through.
        spectrometer.set_frequency(id='test', frq=frq, units='Hz')

        # Generate dic key.
        r20_key = generate_r20_key(exp_type=exp_type, frq=frq)

        # Set first similar to r2.
        value.set(val=None, param='r2')
        self.assertEqual(cdp.mol[0].res[0].spin[0].r2[r20_key], 10.0)

        # Then set for r1.
        value.set(val=None, param='r1')
        print(cdp.mol[0].res[0].spin[0])
        self.assertEqual(cdp.mol[0].res[0].spin[0].r1[r20_key], 5.0)

