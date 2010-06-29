###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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

# Module docstring.
"""Module for the pseudo-elliptical functions."""

# Python module import.
from math import factorial, pi


def pec(x, y):
    """The 2D pseudo-elliptic cosine function.

    This is defined as::

        int_-pi^pi (1 - cos(theta_max)).dphi,

    where::

        theta_max = 1 / sqrt(cos**2(phi)/x**2 + sin**2(phi)/y**2).

    The function is approximated as::

                _inf
                \        (-1)**n
        2*pi*x*y >  ----------------- fn(x, y),
                /___ 4**n * (2n + 2)!
                 n=0

    and where the individual functions are::

        n: 0; fn(x,y) = 1
        n: 1; fn(x,y) = 2*a + 2*b
        n: 2; fn(x,y) = 6*a^2 + 4*a*b + 6*b^2
        n: 3; fn(x,y) = 20*a^3 + 12*a^2*b + 12*a*b^2 + 20*b^3
        n: 4; fn(x,y) = 70*a^4 + 40*a^3*b + 36*a^2*b^2 + 40*a*b^3 + 70*b^4
        n: 5; fn(x,y) = 252*a^5 + 140*a^4*b + 120*a^3*b^2 + 120*a^2*b^3 + 140*a*b^4 + 252*b^5
        n: 6; fn(x,y) = 924*a^6 + 504*a^5*b + 420*a^4*b^2 + 400*a^3*b^3 + 420*a^2*b^4 + 504*a*b^5 + 924*b^6
        n: 7; fn(x,y) = 3432*a^7 + 1848*a^6*b + 1512*a^5*b^2 + 1400*a^4*b^3 + 1400*a^3*b^4 + 1512*a^2*b^5 + 1848*a*b^6 + 3432*b^7
        n: 8; fn(x,y) = 12870*a^8 + 6864*a^7*b + 5544*a^6*b^2 + 5040*a^5*b^3 + 4900*a^4*b^4 + 5040*a^3*b^5 + 5544*a^2*b^6 + 6864*a*b^7 + 12870*b^8
        n: 9; fn(x,y) = 48620*a^9 + 25740*a^8*b + 20592*a^7*b^2 + 18480*a^6*b^3 + 17640*a^5*b^4 + 17640*a^4*b^5 + 18480*a^3*b^6 + 20592*a^2*b^7 + 25740*a*b^8 + 48620*b^9
        n: 10; fn(x,y) = 184756*a^10 + 97240*a^9*b + 77220*a^8*b^2 + 68640*a^7*b^3 + 64680*a^6*b^4 + 63504*a^5*b^5 + 64680*a^4*b^6 + 68640*a^3*b^7 + 77220*a^2*b^8 + 97240*a*b^9 + 184756*b^10
        n: 11; fn(x,y) = 705432*a^11 + 369512*a^10*b + 291720*a^9*b^2 + 257400*a^8*b^3 + 240240*a^7*b^4 + 232848*a^6*b^5 + 232848*a^5*b^6 + 240240*a^4*b^7 + 257400*a^3*b^8 + 291720*a^2*b^9 + 369512*a*b^10 + 705432*b^11


    @param x:       The theta_x cone angle (in rad).
    @type x:        float
    @param y:       The theta_y cone angle (in rad).
    @type y:        float
    @return:        The approximate function value.
    @rtype:         float
    """

    # Init.
    fn = 0.0
    fact = 1.0

    # The x powers.
    a = x**2
    a2 = a**2
    a3 = a**3
    a4 = a**4
    a5 = a**5
    a6 = a**6
    a7 = a**7
    a8 = a**8
    a9 = a**9
    a10 = a**10

    # The y powers.
    b = y**2
    b2 = b**2
    b3 = b**3
    b4 = b**4
    b5 = b**5
    b6 = b**6
    b7 = b**7
    b8 = b**8
    b9 = b**9
    b10 = b**10

    # Term 0.
    f0 = 1.0
    fn = fn + f0 / factorial(2)

    # Term 1.
    f1 = 2*a + 2*b
    fn = fn - f1 / 4.0 / factorial(4)

    # Term 2.
    f2 = 6*a2 + 4*a*b + 6*b2
    fn = fn + f2 / 16.0 / factorial(6)

    # Term 3.
    f3 = 20*a3 + 12*a2*b + 12*a*b2 + 20*b3
    fn = fn - f3 / 64.0 / factorial(8)

    # Term 4.
    f4 = 70*a4 + 40*a3*b + 36*a2*b2 + 40*a*b3 + 70*b4
    fn = fn + f4 / 256.0 / factorial(10)

    # Term 5.
    f5 = 252*a5 + 140*a4*b + 120*a3*b2 + 120*a2*b3 + 140*a*b4 + 252*b5
    fn = fn - f5 / 1024.0 / factorial(12)

    # Term 6.
    f6 = 924*a6 + 504*a5*b + 420*a4*b2 + 400*a3*b3 + 420*a2*b4 + 504*a*b5 + 924*b6
    fn = fn + f6 / 4096.0 / factorial(14)

    # Term 7.
    f7 = 3432*a7 + 1848*a6*b + 1512*a5*b2 + 1400*a4*b3 + 1400*a3*b4 + 1512*a2*b5 + 1848*a*b6 + 3432*b7
    fn = fn - f7 / 16384.0 / factorial(16)

    # Term 8.
    f8 = 12870*a8 + 6864*a7*b + 5544*a6*b2 + 5040*a5*b3 + 4900*a4*b4 + 5040*a3*b5 + 5544*a2*b6 + 6864*a*b7 + 12870*b8
    fn = fn + f8 / 65536.0 / factorial(18)

    # Term 9.
    f9 = 48620*a9 + 25740*a8*b + 20592*a7*b2 + 18480*a6*b3 + 17640*a5*b4 + 17640*a4*b5 + 18480*a3*b6 + 20592*a2*b7 + 25740*a*b8 + 48620*b9
    fn = fn - f9 / 262144.0 / factorial(20)

    # Term 10.
    f10 = 184756*a10 + 97240*a9*b + 77220*a8*b2 + 68640*a7*b3 + 64680*a6*b4 + 63504*a5*b5 + 64680*a4*b6 + 68640*a3*b7 + 77220*a2*b8 + 97240*a*b9 + 184756*b10
    fn = fn + f10 / 1048576.0 / factorial(22)

    # Common factor.
    fn = 2.0 * pi * x * y * fn

    # Return the approximate function value.
    return fn
