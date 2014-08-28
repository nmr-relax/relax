###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
from lib.periodic_table import periodic_table


class Test_periodic_table(TestCase):
    """Unit tests for the lib.periodic_table module."""


    def test_get_atomic_mass(self):
        """Test of the periodic_table.atomic_mass() method."""

        # Check the proton weight.
        weight = periodic_table.atomic_mass(symbol='H')
        self.assertEqual(weight, 1.007975)

        # Check the 1H weight.
        weight = periodic_table.atomic_weight(symbol='1H')
        self.assertEqual(weight, 1.0078250322)

        # Check the 2H weight.
        weight = periodic_table.atomic_weight(symbol='2H')
        self.assertEqual(weight, 2.0141017781)


    def test_get_atomic_weight(self):
        """Test of the periodic_table.atomic_weight() method."""

        # Check the proton weight.
        weight = periodic_table.atomic_weight(symbol='H')
        self.assertEqual(weight, 1.007975)

        # Check the helium weight.
        weight = periodic_table.atomic_weight(symbol='He')
        self.assertEqual(weight, 4.002602)
