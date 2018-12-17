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
"""Backtracking line search algorithm.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from numpy import dot


def backtrack(func, args, x, f, g, p, a_init=1.0, rho=0.5, c=1e-4, max_iter=500):
    """Backtracking line search.

    Procedure 3.1, page 41, from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

    Requires the gradient vector at point xk.


    Internal variables
    ==================

    ai  - The step length at line search iteration i.
    xai - The parameter vector at step length ai.
    fai - The function value at step length ai.


    @param func:            The function to minimise.
    @type func:             func
    @param args:            The tuple of arguments to supply to the functions func.
    @type args:             tuple
    @param x:               The parameter vector.
    @type x:                numpy rank-1 array
    @param f:               The function value at the point x.
    @type f:                float
    @param g:               The gradient vector at the point x.
    @type g:                numpy rank-1 array
    @param p:               The descent direction.
    @type p:                numpy rank-1 array
    @keyword a_init:        Initial step length.
    @type a_init:           float
    @keyword rho:           The step length scaling factor (should be between 0 and 1).
    @type rho:              float
    @keyword c:             Constant between 0 and 1 determining the slope for the sufficient decrease condition.
    @type c:                float
    @keyword maxiter:       The maximum number of iterations.
    @type maxiter:          int
    @return:                The parameter vector, minimised along the direction xk + ak.pk, to be used at k+1.
    @rtype:                 numpy rank-1 array
    """

    # Initialise values.
    a = a_init
    f_count = 0
    i = 0

    while i <= max_iter:
        fk = func(*(x + a*p,)+args)
        f_count = f_count + 1

        # Check if the sufficient decrease condition is met.  If not, scale the step length by rho.
        if fk <= f + c*a*dot(g, p):
            return a, f_count
        else:
            a = rho*a

        # Increment the counter.
        i = i + 1

    # Right, couldn't find it before max_iter so return the function count and a step length significantly smaller than the starting length.
    return a_init * rho ** 10, f_count
