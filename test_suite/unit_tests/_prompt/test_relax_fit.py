###############################################################################
#                                                                             #
# Copyright (C) 2008, 2010 Edward d'Auvergne                                  #
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
from prompt.relax_fit import Relax_fit
from relax_errors import RelaxNumError, RelaxStrError

# Unit test imports.
from data_types import DATA_TYPES


class Test_relax_fit(TestCase):
    """Unit tests for the functions of the 'prompt.relax_fit' module."""

    # Instantiate the user function class.
    relax_fit_fns = Relax_fit()


    def test_relax_time_argfail_time(self):
        """The time arg test of the relax_fit.relax_time() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float, bin, and int arguments, and skip them.
            if data[0] == 'float' or data[0] == 'bin' or data[0] == 'int':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.relax_fit_fns.relax_time, time=data[1])


    def test_relax_time_argfail_spectrum_id(self):
        """The spectrum_id arg test of the relax_fit.relax_time() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_fit_fns.relax_time, spectrum_id=data[1])


    def test_select_model_argfail_model(self):
        """The model arg test of the relax_fit.select_model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_fit_fns.select_model, model=data[1])
