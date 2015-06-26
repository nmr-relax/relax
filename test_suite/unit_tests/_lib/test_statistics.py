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

# relax module imports.
from lib.statistics import geometric_mean
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_statistics(UnitTestCase):
    """Unit tests for the functions of the 'lib.statistics' module."""

    def test_geometric_mean(self):
        """Check the geometric mean value of 4 for the values [2, 8]."""

        # Calculate the mean and check it.
        mean = geometric_mean(values=[2, 8])
        self.assertEqual(mean, 4.0)
