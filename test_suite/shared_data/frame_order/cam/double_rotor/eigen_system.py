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

# Module docstring.
"""Script for determining the full eigensystem of the double rotor system."""

# Python module imports
from numpy import array, cross, dot, float64, transpose
from numpy.linalg import inv, norm


# The axes of the double rotor.
axis1 = array([ -7.778375610280605e-01,   6.284649244351433e-01, -7.532653237683726e-04], float64)
axis2 = array([-0.487095774865268, -0.60362450312215, -0.63116968030708 ], float64)

# The cross product.
axis3 = cross(axis1, axis2)
axis3 = axis3 / norm(axis3)

# Printout.
print("\n")
print("Axis 1:       %s" % axis1)
print("Axis 2:       %s" % axis2)
print("Axis 3:       %s" % axis3)
print("Axis 1 norm:  %s" % norm(axis1))
print("Axis 2 norm:  %s" % norm(axis2))
print("Axis 3 norm:  %s" % norm(axis3))

# Eigenframe.
frame = transpose(array([axis1, axis2, axis3]))
print("Eigenframe:\n%s" % frame)

# Dot products.
print("Dot 1 to 2:   %s" % dot(axis1, axis2))
print("Dot 1 to 3:   %s" % dot(axis1, axis3))
print("Dot 2 to 3:   %s" % dot(axis2, axis3))
print inv(frame) - transpose(frame)
