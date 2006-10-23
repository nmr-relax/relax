#! /usr/bin/python

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


from math import cos, pi, sin, sqrt
from Numeric import Float64, array, dot

from more_thuente import more_thuente

def run():
    print "\n\n\n\n\n\n\n\n\n\n\n\n\t\t<<< Test Functions >>>\n\n\n"
    print "\nSelect the function to test:"
    while 1:
        input = raw_input('> ')
        valid_functions = ['1', '2', '3', '4', '5', '6']
        if input in valid_functions:
            func = int(input)
            break
        else:
            print "Choose a function number between 1 and 6."

    print "\nSelect a0:"
    while 1:
        input = raw_input('> ')
        valid_vals = ['1e-3', '1e-1', '1e1', '1e3']
        if input in valid_vals:
            a0 = float(input)
            break
        else:
            print "Choose a0 as one of ['1e-3', '1e-1', '1e1', '1e3']."

    print "Testing line minimiser using test function " + `func`
    if func == 1:
        f, df = func1, dfunc1
        mu, eta = 0.001, 0.1
    elif func == 2:
        f, df = func2, dfunc2
        mu, eta = 0.1, 0.1
    elif func == 3:
        f, df = func3, dfunc3
        mu, eta = 0.1, 0.1
    elif func == 4:
        f, df = func456, dfunc456
        beta1, beta2 = 0.001, 0.001
        mu, eta = 0.001, 0.001
    elif func == 5:
        f, df = func456, dfunc456
        beta1, beta2 = 0.01, 0.001
        mu, eta = 0.001, 0.001
    elif func == 6:
        f, df = func456, dfunc456
        beta1, beta2 = 0.001, 0.01
        mu, eta = 0.001, 0.001

    xk = array([0.0], Float64)
    pk = array([1.0], Float64)
    if func >= 4:
        args = (beta1, beta2)
    else:
        args = ()
    f0 = apply(f, (xk,)+args)
    g0 = apply(df, (xk,)+args)
    a = more_thuente(f, df, args, xk, pk, f0, g0, a_init=a0, mu=mu, eta=eta, print_flag=1)
    print "The minimum is at " + `a`


def func1(alpha, beta=2.0):
    """Test function 1.

    From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient
    decrease. ACM Trans. Math. Softw. 20, 286-307.

    The function is:
                              alpha
        phi(alpha)  =  - ---------------
                         alpha**2 + beta
    """

    return - alpha[0]/(alpha[0]**2 + beta)


def dfunc1(alpha, beta=2.0):
    """Derivative of test function 1.

    From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient
    decrease. ACM Trans. Math. Softw. 20, 286-307.

    The gradient is:
                             2*alpha**2                 1
        phi'(alpha)  =  --------------------  -  ---------------
                        (alpha**2 + beta)**2     alpha**2 + beta
    """

    temp = array([0.0], Float64)
    if alpha[0] > 1e90:
        return temp
    else:
        a = 2.0*(alpha[0]**2)/((alpha[0]**2 + beta)**2)
        b = 1.0/(alpha[0]**2 + beta)
        temp[0] = a - b
        return temp


def func2(alpha, beta=0.004):
    """Test function 2.

    From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient
    decrease. ACM Trans. Math. Softw. 20, 286-307.

    The function is:

        phi(alpha)  =  (alpha + beta)**5 - 2(alpha + beta)**4
    """

    return (alpha[0] + beta)**5 - 2.0*((alpha[0] + beta)**4)


def dfunc2(alpha, beta=0.004):
    """Derivative of test function 2.

    From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient
    decrease. ACM Trans. Math. Softw. 20, 286-307.

    The gradient is:

        phi'(alpha)  =  5(alpha + beta)**4 - 8(alpha + beta)**3
    """

    temp = array([0.0], Float64)
    temp[0] = 5.0*((alpha[0] + beta)**4) - 8.0*((alpha[0] + beta)**3)
    return temp


def func3(alpha, beta=0.01, l=39.0):
    """Test function 3.

    From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient
    decrease. ACM Trans. Math. Softw. 20, 286-307.

    The function is:

                                     2(1 - beta)       / l*pi         \ 
        phi(alpha)  =  phi0(alpha) + ----------- . sin | ---- . alpha |
                                        l*pi           \  2           /

        where:
                            /  1 - alpha,                     if alpha <= 1 - beta,
                            |
                            |  alpha - 1,                     if alpha >= 1 + beta,
            phi0(alpha) =  <
                            |   1                    1
                            | ------(alpha - 1)**2 + - beta,  if alpha in [1 - beta, 1 + beta].
                            \ 2*beta                 2
    """

    # Calculate phi0(alpha).
    if alpha[0] <= 1.0 - beta:
        phi0 = 1.0 - alpha[0]
    elif alpha[0] >= 1.0 + beta:
        phi0 = alpha[0] - 1.0
    else:
        phi0 = 0.5/beta * (alpha[0] - 1.0)**2 + 0.5*beta

    return phi0 + 2.0*(1.0 - beta)/(l*pi) * sin(0.5 * l * pi * alpha[0])


def dfunc3(alpha, beta=0.01, l=39.0):
    """Derivative of test function 3.

    From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient
    decrease. ACM Trans. Math. Softw. 20, 286-307.

    The gradient is:
                                                       / l*pi         \ 
        phi(alpha)  =  phi0'(alpha) + (1 - beta) . cos | ---- . alpha |
                                                       \  2           /

        where:
                             /  -1,        if alpha <= 1 - beta,
                             |
                             |  1,         if alpha >= 1 + beta,
            phi0'(alpha) =  <
                             | alpha - 1
                             | ---------,  if alpha in [1 - beta, 1 + beta].
                             \   beta
    """

    # Calculate phi0'(alpha).
    if alpha[0] <= 1.0 - beta:
        phi0_prime = -1.0
    elif alpha[0] >= 1.0 + beta:
        phi0_prime = 1.0
    else:
        phi0_prime = (alpha[0] - 1.0)/beta

    temp = array([0.0], Float64)
    temp[0] = phi0_prime + (1.0 - beta) * cos(0.5 * l * pi * alpha[0])
    return temp


def func456(alpha, beta1, beta2):
    """Test functions 4, 5, and 6.

    From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient
    decrease. ACM Trans. Math. Softw. 20, 286-307.

    The function is:

        phi(alpha)  =  gamma(beta1) * sqrt((1 - alpha)**2 + beta2**2)
                           + gamma(beta2) * sqrt(alpha**2 + beta1**2)

        where:
            gamma(beta) = sqrt(1 + beta**2) - beta
    """

    g1 = sqrt(1.0 + beta1**2) - beta1
    g2 = sqrt(1.0 + beta2**2) - beta2
    return g1 * sqrt((1.0 - alpha[0])**2 + beta2**2) + g2 * sqrt(alpha[0]**2 + beta1**2)


def dfunc456(alpha, beta1, beta2):
    """Test functions 4, 5, and 6.

    From More, J. J., and Thuente, D. J. 1994, Line search algorithms with guaranteed sufficient
    decrease. ACM Trans. Math. Softw. 20, 286-307.

    The function is:

                                                  (1 - alpha)
        phi'(alpha)  =  - gamma(beta1) * -------------------------------
                                         sqrt((1 - alpha)**2 + beta2**2)

                                                       a
                            + gamma(beta2) * -------------------------
                                             sqrt(alpha**2 + beta1**2)

        where:
            gamma(beta) = sqrt(1 + beta**2) - beta
    """

    temp = array([0.0], Float64)
    g1 = sqrt(1.0 + beta1**2) - beta1
    g2 = sqrt(1.0 + beta2**2) - beta2
    a = -g1 * (1.0 - alpha[0]) / sqrt((1.0 - alpha[0])**2 + beta2**2)
    b = g2 * alpha[0] / sqrt(alpha[0]**2 + beta1**2)
    temp[0] = a + b
    return temp


run()
