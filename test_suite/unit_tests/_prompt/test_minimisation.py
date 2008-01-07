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
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store
from prompt.minimisation import Minimisation
from relax_errors import RelaxIntError
from test_suite.unit_tests.minimisation_testing_base import Minimisation_base_class

# Unit test imports.
from data_types import DATA_TYPES
import fake_relax


class Test_minimisation(Minimisation_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.minimisation' module."""

    # Instantiate the user function class.
    minimisation_fns = Minimisation(fake_relax.fake_instance())


    def test_calc_argfail_print_flag(self):
        """The print_flag arg test of the minimisation.calc() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the int and bin arguments, and skip them.
            if data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxIntError, self.minimisation_fns.calc, print_flag=data[1])
