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
from generic_fns import eliminate
from prompt.eliminate import Eliminate
from relax_errors import RelaxFunctionError, RelaxNoneTupleError

# Unit test imports.
from data_types import DATA_TYPES
import fake_relax


class Test_eliminate(TestCase):
    """Unit tests for the functions of the 'prompt.eliminate' module."""

    # Instantiate the user function class.
    eliminate_fns = Eliminate(fake_relax.fake_instance())


    def test_eliminate_function(self):
        """The function arg unit test of the eliminate() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and func arguments, and skip them.
            if data[0] == 'None' and data[0] == 'func':
                continue

            # The argument test.
            self.assertRaises(RelaxFunctionError, self.eliminate_fns.eliminate, function=data[1])


    def test_eliminate_args(self):
        """The args arg unit test of the eliminate() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and tuple arguments, and skip them.
            if data[0] == 'None' and data[0] == 'tuple':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneTupleError, self.eliminate_fns.eliminate, args=data[1])
