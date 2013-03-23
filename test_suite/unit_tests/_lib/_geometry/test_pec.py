###############################################################################
#                                                                             #
# Copyright (C) 2010-2013 Edward d'Auvergne                                   #
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
from math import pi
from unittest import TestCase

# relax module imports.
from lib.geometry.pec import pec


class Test_pseudo_ellipse(TestCase):
    """Unit tests for the lib.geometry.pec relax module."""


    def test_pec_0_0(self):
        """Test the pec() function for x = 0, y = 0 (nothing)."""

        # Check the value.
        self.assertAlmostEqual(pec(0, 0), 0.0)


    def test_pec_0_1(self):
        """Test the pec() function for x = 0, y = 1 (nothing)."""

        # Check the value.
        self.assertAlmostEqual(pec(0, 1), 0.0)


    def test_pec_1_0(self):
        """Test the pec() function for x = 1, y = 0 (nothing)."""

        # Check the value.
        self.assertAlmostEqual(pec(1, 0), 0.0)


    def test_pec_partial1(self):
        """Test the pec() function for x = pi/2, y = pi."""

        # Check the value.
        self.assertAlmostEqual(pec(pi/2, pi), 9.2141334381797524)


    def test_pec_partial2(self):
        """Test the pec() function for x = pi/2, y = pi/2."""

        # Check the value.
        self.assertAlmostEqual(pec(pi/2, pi/2), 2*pi)


    def test_pec_partial3(self):
        """Test the pec() function for x = pi/6, y = pi/2."""

        # Check the value.
        self.assertAlmostEqual(pec(pi/6, pi/2), 2.3058688920532275)


    def test_pec_pi_pi(self):
        """Test the pec() function for x = pi, y = pi (full sphere)."""

        # Check the value.
        self.assertAlmostEqual(pec(pi, pi), 4*pi)
