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
from prompt.noe import Noe
from relax_errors import RelaxBoolError, RelaxNoneIntError, RelaxNoneStrError, RelaxStrError

# Unit test imports.
from data_types import DATA_TYPES
import fake_relax


class Test_noe(TestCase):
    """Unit tests for the functions of the 'prompt.noe' module."""

    # Instantiate the user function class.
    noe_fns = Noe(fake_relax.fake_instance())


    def test_read_argfail_spectrum_type(self):
        """The spectrum_type arg test of the noe.spectrum_type() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.noe_fns.spectrum_type, spectrum_type=data[1])


    def test_read_argfail_spectrum_id(self):
        """The spectrum_id arg test of the noe.spectrum_type() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str argument, and skip it.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.noe_fns.spectrum_type, spectrum_type='x', spectrum_id=data[1])
