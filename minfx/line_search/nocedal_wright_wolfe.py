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
"""A line search algorithm implemented using the strong Wolfe conditions.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Python module imports.
from copy import deepcopy
from numpy import dot, sqrt

# Minfx module imports.
from minfx.line_search.interpolate import cubic_ext, quadratic_fafbga

# Rename the interpolation functions.
quadratic = quadratic_fafbga


def nocedal_wright_wolfe(func, func_prime, args, x, f, g, p, a_init=1.0, max_a=1e5, mu=0.001, eta=0.9, tol=1e-10, print_flag=0):
    """A line search algorithm implemented using the strong Wolfe conditions.

    Algorithm 3.2, page 59, from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.

    Requires the gradient function.

    These functions require serious debugging and recoding to work properly (especially the safeguarding)!


    @param func:            The function to minimise.
    @type func:             func
    @param func_prime:      The function which returns the gradient vector.
    @type func_prime:       func
    @param args:            The tuple of arguments to supply to the functions func and dfunc.
    @type args:             args
    @param x:               The parameter vector at minimisation step k.
    @type x:                numpy array
    @param f:               The function value at the point x.
    @type f:                float
    @param g:               The function gradient vector at the point x.
    @type g:                numpy array
    @param p:               The descent direction.
    @type p:                numpy array
    @keyword a_init:        Initial step length.
    @type a_init:           flaot
    @keyword a_max:         The maximum value for the step length.
    @type a_max:            float
    @keyword mu:            Constant determining the slope for the sufficient decrease condition (0 < mu < eta < 1).
    @type mu:               float
    @keyword eta:           Constant used for the Wolfe curvature condition (0 < mu < eta < 1).
    @type eta:              float
    @keyword tol:           The function tolerance.
    @type tol:              float
    @keyword print_flag:    The higher the value, the greater the amount of info printed out.
    @type print_flag:       int
    """

    # Initialise values.
    i = 1
    f_count = 0
    g_count = 0
    a0 = {}
    a0['a'] = 0.0
    a0['phi'] = f
    a0['phi_prime'] = dot(g, p)
    a_last = deepcopy(a0)
    a_max = {}
    a_max['a'] = max_a
    a_max['phi'] = func(*(x + a_max['a']*p,)+args)
    a_max['phi_prime'] = dot(func_prime(*(x + a_max['a']*p,)+args), p)
    f_count = f_count + 1
    g_count = g_count + 1

    # Initialise sequence data.
    a = {}
    a['a'] = a_init
    a['phi'] = func(*(x + a['a']*p,)+args)
    a['phi_prime'] = dot(func_prime(*(x + a['a']*p,)+args), p)
    f_count = f_count + 1
    g_count = g_count + 1

    if print_flag:
        print("\n<Line search initial values>")
        print_data("Pre (a0)", i-1, a0)
        print_data("Pre (a_max)", i-1, a_max)

    while True:
        if print_flag:
            print("<Line search iteration i = " + repr(i) + " >")
            print_data("Initial (a)", i, a)
            print_data("Initial (a_last)", i, a_last)

        # Check if the sufficient decrease condition is violated.
        # If so, the interval (a(i-1), a) will contain step lengths satisfying the strong Wolfe conditions.
        if not a['phi'] <= a0['phi'] + mu * a['a'] * a0['phi_prime']:
            if print_flag:
                print("\tSufficient decrease condition is violated - zooming")
            return zoom(func, func_prime, args, f_count, g_count, x, f, g, p, mu, eta, i, a0, a_last, a, tol, print_flag=print_flag)
        if print_flag:
            print("\tSufficient decrease condition is OK")

        # Check if the curvature condition is met and if so, return the step length a which satisfies the strong Wolfe conditions.
        if abs(a['phi_prime']) <= -eta * a0['phi_prime']:
            if print_flag:
                print("\tCurvature condition OK, returning a")
            return a['a'], f_count, g_count
        if print_flag:
            print("\tCurvature condition is violated")

        # Check if the gradient is positive.
        # If so, the interval (a(i-1), a) will contain step lengths satisfying the strong Wolfe conditions.
        if a['phi_prime'] >= 0.0:
            if print_flag:
                print("\tGradient at a['a'] is positive - zooming")
            # The arguments to zoom are a followed by a_last, because the function value at a_last will be higher than at a.
            return zoom(func, func_prime, args, f_count, g_count, x, f, g, p, mu, eta, i, a0, a, a_last, tol, print_flag=print_flag)
        if print_flag:
            print("\tGradient is negative")

        # The strong Wolfe conditions are not met, and therefore interpolation between a and a_max will be used to find a value for a(i+1).
        #if print_flag:
        #    print("\tStrong Wolfe conditions are not met, doing quadratic interpolation")
        #a_new = cubic_ext(a['a'], a_max['a'], a['phi'], a_max['phi'], a['phi_prime'], a_max['phi_prime'], full_output=0)
        a_new = a['a'] + 0.25 * (a_max['a'] - a['a'])

        # Update.
        a_last = deepcopy(a)
        a['a'] = a_new
        a['phi'] = func(*(x + a['a']*p,)+args)
        a['phi_prime'] = dot(func_prime(*(x + a['a']*p,)+args), p)
        f_count = f_count + 1
        g_count = g_count + 1
        i = i + 1
        if print_flag:
            print_data("Final (a)", i, a)
            print_data("Final (a_last)", i, a_last)

        # Test if the difference in function values is less than the tolerance.
        if abs(a_last['phi'] - a['phi']) <= tol:
            if print_flag:
                print("abs(a_last['phi'] - a['phi']) <= tol")
            return a['a'], f_count, g_count


def print_data(text, k, a):
    """Temp func for debugging."""

    print(text + " data printout:")
    print("   Iteration:      " + repr(k))
    print("   a:              " + repr(a['a']))
    print("   phi:            " + repr(a['phi']))
    print("   phi_prime:      " + repr(a['phi_prime']))


def zoom(func, func_prime, args, f_count, g_count, x, f, g, p, mu, eta, i, a0, a_lo, a_hi, tol, print_flag=0):
    """Find the minimum function value in the open interval (a_lo, a_hi)

    Algorithm 3.3, page 60, from 'Numerical Optimization' by Jorge Nocedal and Stephen J. Wright, 1999, 2nd ed.
    """

    # Initialize aj.
    aj = {}
    j = 0
    aj_last = deepcopy(a_lo)

    while True:
        if print_flag:
            print("\n<Zooming iterate j = " + repr(j) + " >")

        # Interpolate to find a trial step length aj between a_lo and a_hi.
        aj_new = quadratic(a_lo['a'], a_hi['a'], a_lo['phi'], a_hi['phi'], a_lo['phi_prime'])

        # Safeguarding aj['a']
        aj['a'] = max(aj_last['a'] + 0.66*(a_hi['a'] - aj_last['a']), aj_new)

        # Calculate the function and gradient value at aj['a'].
        aj['phi'] = func(*(x + aj['a']*p,)+args)
        aj['phi_prime'] = dot(func_prime(*(x + aj['a']*p,)+args), p)
        f_count = f_count + 1
        g_count = g_count + 1

        if print_flag:
            print_data("a_lo", i, a_lo)
            print_data("a_hi", i, a_hi)
            print_data("aj", i, aj)

        # Check if the sufficient decrease condition is violated.
        if not aj['phi'] <= a0['phi'] + mu * aj['a'] * a0['phi_prime']:
            a_hi = deepcopy(aj)
        else:
            # Check if the curvature condition is met and if so, return the step length ai which satisfies the strong Wolfe conditions.
            if abs(aj['phi_prime']) <= -eta * a0['phi_prime']:
                if print_flag:
                    print("aj: " + repr(aj))
                    print("<Finished zooming>")
                return aj['a'], f_count, g_count

            # Determine if a_hi needs to be reset.
            if aj['phi_prime'] * (a_hi['a'] - a_lo['a']) >= 0.0:
                a_hi = deepcopy(a_lo)

            a_lo = deepcopy(aj)

        # Test if the difference in function values is less than the tolerance.
        if abs(aj_last['phi'] - aj['phi']) <= tol:
            if print_flag:
                print("abs(aj_last['phi'] - aj['phi']) <= tol")
                print("<Finished zooming>")
            return aj['a'], f_count, g_count

        # Update.
        aj_last = deepcopy(aj)
        j = j + 1
