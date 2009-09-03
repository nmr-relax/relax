###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
from math import pi
from numpy import float64, zeros
from random import uniform
from unittest import TestCase

# relax module imports.
from generic_fns.angles import wrap_angles
from maths_fns.rotation_matrix import *


class Test_rotation_matrix(TestCase):
    """Unit tests for the maths_fns.rotation_matrix relax module."""

    def setUp(self):
        """Set up data used by the unit tests."""


    def test_R_to_euler_zyz(self):
        """Test the rotation matrix to zyz Euler angle conversion."""

        # Starting angles.
        alpha = uniform(0, 2*pi)
        beta =  uniform(0, pi)
        gamma = uniform(0, 2*pi)

        # Print out.
        print("Original angles:")
        print("alpha: %s" % alpha)
        print("beta: %s" % beta)
        print("gamma: %s\n" % gamma)

        # Generate the rotation matrix.
        R = zeros((3, 3), float64)
        R_euler_zyz(R, alpha, beta, gamma)

        # Get back the angles.
        alpha_new, beta_new, gamma_new = R_to_euler_zyz(R)

        # Wrap the angles.
        alpha_new = wrap_angles(alpha_new, 0, 2*pi)
        beta_new = wrap_angles(beta_new, 0, 2*pi)
        gamma_new = wrap_angles(gamma_new, 0, 2*pi)

        # Print out.
        print("New angles:")
        print("alpha: %s" % alpha_new)
        print("beta: %s" % beta_new)
        print("gamma: %s\n" % gamma_new)

        # Checks.
        self.assertAlmostEqual(alpha, alpha_new)
        self.assertAlmostEqual(beta, beta_new)
        self.assertAlmostEqual(gamma, gamma_new)
