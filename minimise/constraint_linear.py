###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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


from Numeric import dot, matrixmultiply


class Constraint_linear:
    def __init__(self, A=None, b=None):
        """Class for the creation of linear inequality constraint functions and gradients.

        The constraints are in the form:

            A.x >= b

        where:
            A is an m*n matrix where the rows are the transposed vectors, ai, of length
            n.  The elements of ai are the coefficients of the model parameters.

            x is the vector of model parameters of dimension n.

            b is the vector of scalars of dimension m.

            m is the number of constraints.

            n is the number of model parameters.


        eg if 0 <= q <= 1, q >= 1 - 2r, and 0 <= r, then:

            | 1  0 |            |  0 |
            |      |            |    |
            |-1  0 |   | q |    | -1 |
            |      | . |   | >= |    |
            | 1  2 |   | r |    |  1 |
            |      |            |    |
            | 0  1 |            |  2 |
        """

        # Initialise arguments.
        self.A = A
        self.b = b


    def func(self, x):
        """The constraint function.

        A vector containing the constraint values is returned.
        """

        return dot(self.A, x) - self.b


    def dfunc(self, x):
        """The constraint gradient.

        As the inequality constraints are linear, the gradient matrix is constant and equal to the
        coefficient matrix A.  Therefore this function simply returns the matrix.
        """

        return self.A
