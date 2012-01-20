###############################################################################
#                                                                             #
# Copyright (C) 2007-2012 Edward d'Auvergne                                   #
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

# relax module imports.
from generic_fns import pipes, value
from test_suite.unit_tests.value_testing_base import Value_base_class



class Test_value(Value_base_class, TestCase):
    """Unit tests for the functions of the 'generic_fns.value' module."""

    # Place the generic_fns.value module into the class namespace.
    value_fns = value


    def test_partition_params1(self):
        """First test of the generic_fns.value.partition_params() function."""

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
        """Second test of the generic_fns.value.partition_params() function."""

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
        """Third test of the generic_fns.value.partition_params() function."""

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
        """Forth test of the generic_fns.value.partition_params() function."""

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
        """Fifth test of the generic_fns.value.partition_params() function."""

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
        """Sixth test of the generic_fns.value.partition_params() function."""

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
