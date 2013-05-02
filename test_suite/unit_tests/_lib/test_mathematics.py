###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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

# Module docstring.
"""Unit tests of the lib.mathematics module."""

# Python module imports.
from unittest import TestCase

# relax module imports.
from lib.mathematics import order_of_magnitude, round_to_next_order


class Test_mathematics(TestCase):
    """Unit tests for the lib.mathematics relax module."""

    def test_order_of_magnitude0(self):
        """0th test of the lib.mathematics.order_of_magnitude function."""

        self.assertEqual(order_of_magnitude(0.123), 0.0)


    def test_order_of_magnitude1(self):
        """1st test of the lib.mathematics.order_of_magnitude function."""

        self.assertEqual(order_of_magnitude(1.1), 1.0)


    def test_order_of_magnitude2(self):
        """2nd test of the lib.mathematics.order_of_magnitude function."""

        self.assertEqual(order_of_magnitude(12), 2.0)


    def test_order_of_magnitude3(self):
        """3rd test of the lib.mathematics.order_of_magnitude function."""

        self.assertEqual(order_of_magnitude(123), 3.0)


    def test_order_of_magnitude4(self):
        """4th test of the lib.mathematics.order_of_magnitude function."""

        self.assertEqual(order_of_magnitude(1234), 4.0)


    def test_round_to_next_order0(self):
        """0th test of the lib.mathematics.round_to_next_order function."""

        self.assertEqual(round_to_next_order(0.123), 1.0)


    def test_round_to_next_order1(self):
        """1st test of the lib.mathematics.round_to_next_order function."""

        self.assertEqual(round_to_next_order(1.1), 10.0)


    def test_round_to_next_order2(self):
        """2nd test of the lib.mathematics.round_to_next_order function."""

        self.assertEqual(round_to_next_order(12), 100.0)


    def test_round_to_next_order3(self):
        """3rd test of the lib.mathematics.round_to_next_order function."""

        self.assertEqual(round_to_next_order(123), 1000.0)


    def test_round_to_next_order4(self):
        """4th test of the lib.mathematics.round_to_next_order function."""

        self.assertEqual(round_to_next_order(1234), 10000.0)
