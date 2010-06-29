###############################################################################
#                                                                             #
# Copyright (C) 2008-2010 Edward d'Auvergne                                   #
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
from prompt.eliminate import Eliminate
from relax_errors import RelaxNoneFunctionError, RelaxTupleError

# Unit test imports.
from data_types import DATA_TYPES



def dummy_function():
    pass



class Test_eliminate(TestCase):
    """Unit tests for the functions of the 'prompt.eliminate' module."""

    # Instantiate the user function class.
    eliminate_fns = Eliminate()


    def test_eliminate_function(self):
        """The function arg unit test of the eliminate() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and func arguments, and skip them.
            if data[0] == 'None' or data[0] == 'function':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneFunctionError, self.eliminate_fns.eliminate, function=data[1])


    def test_eliminate_args(self):
        """The args arg unit test of the eliminate() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the None and tuple arguments, and skip them.
            if data[0] == 'None' or data[0] == 'tuple' or data[0] == 'float tuple' or data[0] == 'str tuple':
                continue

            # The argument test.
            self.assertRaises(RelaxTupleError, self.eliminate_fns.eliminate, function=dummy_function, args=data[1])
