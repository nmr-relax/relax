###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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
from prompt.value import Value
from relax_errors import RelaxError, RelaxListFloatStrError, RelaxListStrError, RelaxNoneFloatStrListError, RelaxNoneStrError, RelaxNoneStrListError
from test_suite.unit_tests.value_testing_base import Value_base_class

# Unit test imports.
from data_types import DATA_TYPES
import fake_relax


class Test_value(Value_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.value' module."""

    # Instantiate the user function class.
    value_fns = Value(fake_relax.fake_instance())


    def test_set_argfail_val(self):
        """The val arg test of the value.set() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None, float, int, str, or bin arguments, and skip them.
            if data[0] == 'None' or data[0] == 'int' or data[0] == 'bin' or data[0] == 'str' or data[0] == 'float':
                continue

            # Catch all number lists.
            if data[0] == 'int list' or data[0] == 'float list' or data[0] == 'number list':
                self.assertRaises(RelaxError, self.value_fns.set, val=data[1], param='CSA')
                if len(data[1]) != 1:
                    self.assertRaises(RelaxError, self.value_fns.set, val=data[1], param=['CSA'])

            # Catch all other list arguments.
            elif type(data[1]) == list:
                self.assertRaises(RelaxListFloatStrError, self.value_fns.set, val=data[1], param=None)

            # All other arguments.
            else:
                self.assertRaises(RelaxNoneFloatStrListError, self.value_fns.set, val=data[1], param='CSA')


    def test_set_argfail_param(self):
        """The param arg test of the value.set() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # Catch the string list arguments.
            if data[0] == 'str list':
                if len(data[1]) != 1:
                    self.assertRaises(RelaxError, self.value_fns.set, param=data[1], val=[1.0])
                else:
                    self.assertRaises(RelaxError, self.value_fns.set, param=data[1], val=[1.0, 2.0])

            # Catch all other list arguments.
            elif type(data[1]) == list:
                self.assertRaises(RelaxListStrError, self.value_fns.set, param=data[1], val=None)

            # All other arguments.
            else:
                self.assertRaises(RelaxNoneStrListError, self.value_fns.set, param=data[1], val=None)


    def test_set_argfail_spin_id(self):
        """The spin_id arg test of the value.set() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and str arguments, and skip them.
            if data[0] == 'None' or data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneStrError, self.value_fns.set, spin_id=data[1])
