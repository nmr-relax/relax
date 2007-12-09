###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from generic_fns import value
from relax_errors import RelaxError
import specific_fns
from test_suite.unit_tests.value_testing_base import Value_base_class



class Test_value(Value_base_class, TestCase):
    """Unit tests for the functions of the 'generic_fns.value' module."""

    # Place the generic_fns.value module into the class namespace.
    value_fns = value


    def test_partition_params1(self):
        """First test of the generic_fns.value.partition_params() function."""

        # The parameters and values.
        param = ['S2']
        val = [0.8]

        # Partition.
        tensor_params, tensor_values, spin_params, spin_values = value.partition_params(val, param, specific_fns.model_free.return_data_name)

        # Tests.
        self.assertEqual(tensor_params, [])
        self.assertEqual(tensor_values, [])
        self.assertEqual(spin_params, ['S2'])
        self.assertEqual(spin_values, [0.8])


    def test_partition_params2(self):
        """Second test of the generic_fns.value.partition_params() function."""

        # The parameters and values.
        param = ['Dx']
        val = [1e7]

        # Partition.
        tensor_params, tensor_values, spin_params, spin_values = value.partition_params(val, param, specific_fns.model_free.return_data_name)

        # Tests.
        self.assertEqual(tensor_params, ['Dx'])
        self.assertEqual(tensor_values, [1e7])
        self.assertEqual(spin_params, [])
        self.assertEqual(spin_values, [])


    def test_partition_params3(self):
        """Third test of the generic_fns.value.partition_params() function."""

        # The parameters and values.
        param = ['Dx', 'S2']
        val = [1e7, 0.8]

        # Partition.
        tensor_params, tensor_values, spin_params, spin_values = value.partition_params(val, param, specific_fns.model_free.return_data_name)

        # Tests.
        self.assertEqual(tensor_params, ['Dx'])
        self.assertEqual(tensor_values, [1e7])
        self.assertEqual(spin_params, ['S2'])
        self.assertEqual(spin_values, [0.8])


    def test_partition_params4(self):
        """Forth test of the generic_fns.value.partition_params() function."""

        # The parameters and values.
        param = ['Dx', 'S2', 'CSA']
        val = [1e7, 0.8, -160e-6]

        # Partition.
        tensor_params, tensor_values, spin_params, spin_values = value.partition_params(val, param, specific_fns.model_free.return_data_name)

        # Tests.
        self.assertEqual(tensor_params, ['Dx'])
        self.assertEqual(tensor_values, [1e7])
        self.assertEqual(spin_params, ['S2', 'CSA'])
        self.assertEqual(spin_values, [0.8, -160e-6])


    def test_partition_params5(self):
        """Fifth test of the generic_fns.value.partition_params() function."""

        # The parameters and values.
        param = ['Dpar', 'S2', 'Dper', 'CSA', 'theta']
        val = [1e7, 0.8, 2e7, -160e-6, 0.13]

        # Partition.
        tensor_params, tensor_values, spin_params, spin_values = value.partition_params(val, param, specific_fns.model_free.return_data_name)

        # Tests.
        self.assertEqual(tensor_params, ['Dpar', 'Dper', 'theta'])
        self.assertEqual(tensor_values, [1e7, 2e7, 0.13])
        self.assertEqual(spin_params, ['S2', 'CSA'])
        self.assertEqual(spin_values, [0.8, -160e-6])


    def test_partition_params6(self):
        """Sixth test of the generic_fns.value.partition_params() function."""

        # The parameters and values.
        param = []
        val = []

        # Partition.
        tensor_params, tensor_values, spin_params, spin_values = value.partition_params(val, param, specific_fns.model_free.return_data_name)

        # Tests.
        self.assertEqual(tensor_params, [])
        self.assertEqual(tensor_values, [])
        self.assertEqual(spin_params, [])
        self.assertEqual(spin_values, [])
