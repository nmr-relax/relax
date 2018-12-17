###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the minfx optimisation library,                        #
# https://gna.org/projects/minfx                                              #
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
"""Eigenvalue Hessian modification.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from numpy import dot, sort
from numpy.linalg import eig, inv


def eigenvalue(dfk, d2fk, I, print_prefix, print_flag, return_matrix=0):
    """The eigenvalue Hessian modification.

    This modification is based on equation 6.14 from page 144 of 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

    Returns the modified Newton step.
    """

    # Calculate the eigenvalues.
    eigen = eig(d2fk)
    eigenvals = sort(eigen[0])

    # Modify the Hessian if the smallest eigenvalue is negative.
    tau = None
    if eigenvals[0] < 0.0:
        tau = max(0.0, 1e-2 - eigenvals[0])
        matrix = d2fk + tau * I
    else:
        matrix = d2fk

    # Debugging.
    if print_flag >= 3:
        eigen_new = eig(matrix)
        eigenvals_new = sort(eigen_new[0])
        print(print_prefix + "d2fk:\n" + repr(d2fk))
        print(print_prefix + "eigenvals(d2fk): " + repr(eigenvals))
        print(print_prefix + "tau: " + repr(tau))
        print(print_prefix + "matrix:\n" + repr(matrix))
        print(print_prefix + "eigenvals(matrix): " + repr(eigenvals_new))
        print(print_prefix + "Newton dir: " + repr(-dot(inv(matrix), dfk)))

    # Calculate the Newton direction.
    if return_matrix:
        return -dot(inv(matrix), dfk), matrix
    else:
        return -dot(inv(matrix), dfk)
