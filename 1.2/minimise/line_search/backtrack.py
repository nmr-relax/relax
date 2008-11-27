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


from Numeric import dot

def backtrack(func, args, x, f, g, p, a_init=1.0, rho=0.5, c=1e-4, max_iter=500):
    """Backtracking line search.

    Procedure 3.1, page 41, from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright,
    1999, 2nd ed.

    Requires the gradient vector at point xk.


    Function options
    ~~~~~~~~~~~~~~~~

    func   - The function to minimise.
    args   - The tuple of arguments to supply to the functions func.
    x      - The parameter vector.
    f      - The function value at the point x.
    g      - The gradient vector at the point x.
    p      - The descent direction.
    a_init - Initial step length.
    rho    - The step length scaling factor (should be between 0 and 1).
    c      - Constant between 0 and 1 determining the slope for the sufficient decrease condition.


    Returned objects
    ~~~~~~~~~~~~~~~~

    The parameter vector, minimised along the direction xk + ak.pk, to be used at k+1.


    Internal variables
    ~~~~~~~~~~~~~~~~~~

    ai  - The step length at line search iteration i.
    xai - The parameter vector at step length ai.
    fai - The function value at step length ai.
    """

    # Initialise values.
    a = a_init
    f_count = 0
    i = 0

    while i <= max_iter:
        fk = apply(func, (x + a*p,)+args)
        f_count = f_count + 1

        # Check if the sufficient decrease condition is met.  If not, scale the step length by rho.
        if fk <= f + c*a*dot(g, p):
            return a, f_count
        else:
            a = rho*a

        # Increment the counter.
        i = i + 1
