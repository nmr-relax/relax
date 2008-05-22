###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2008 Edward d'Auvergne                            #
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

"""Module containing functions for calculating the chi-squared value, gradient, and Hessian."""

# Python module imports.
from numpy import sum


# Chi-squared value.
####################


def chi2(data, back_calc_vals, errors):
    """Function to calculate the chi-squared value.

    The chi-squared equation
    ========================

    The equation is::

                        _n_
                        \    (yi - yi(theta)) ** 2
        chi^2(theta)  =  >   ---------------------
                        /__      sigma_i ** 2
                        i=1

    where
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - sigma_i are the values of the error set.


    @param data:            The vector of yi values.
    @type data:             numpy array
    @param back_calc_vals:  The vector of yi(theta) values.
    @type back_calc_vals:   numpy array
    @param errors:          The vector of sigma_i values.
    @type errors:           numpy array
    @return:                The chi-squared value.
    @rtype:                 float
    """

    # Calculate the chi-squared statistic.
    return sum((1.0 / errors * (data - back_calc_vals))**2, axis=0)


# Chi-squared gradient.
#######################


def dchi2(data, back_calc_vals, back_calc_grad, errors):
    """Function to create the chi-squared gradient.

    The chi-squared gradient
    ========================

    The equation is::

                             _n_
        dchi^2(theta)        \   / yi - yi(theta)     dyi(theta) \ 
        -------------  =  -2  >  | --------------  .  ---------- |
           dthetaj           /__ \   sigma_i**2        dthetaj   /
                             i=1

    where
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - dyi(theta)/dthetaj are the values of the back calculated gradient.
        - sigma_i are the values of the error set.

    @param data:            The vector of yi values.
    @type data:             numpy array
    @param back_calc_vals:  The vector of yi(theta) values.
    @type back_calc_vals:   numpy array
    @param back_calc_grad:  The matrix of dyi(theta)/dthetaj values.
    @type back_calc_grad:   numpy matrix
    @param errors:          The vector of sigma_i values.
    @type errors:           numpy array
    @return:                The chi-squared gradient.
    @rtype:                 numpy array
    """

    # Calculate the chi-squared gradient.
    return -2.0 * sum(1.0 / (errors**2) * (data - back_calc_vals) * back_calc_grad, axis=0)


# Chi-squared Hessian.
######################


def d2chi2(data, back_calc_vals, back_calc_grad_j, back_calc_grad_k, back_calc_hess, errors):
    """Function to create the chi-squared Hessian.

    The chi-squared Hessian
    =======================

    The equation is::

                              _n_
        d2chi^2(theta)        \       1      / dyi(theta)   dyi(theta)                        d2yi(theta)   \ 
        ---------------  =  2  >  ---------- | ---------- . ----------  -  (yi-yi(theta)) . --------------- |
        dthetaj.dthetak       /__ sigma_i**2 \  dthetaj      dthetak                        dthetaj.dthetak /
                              i=1

    where
        - theta is the parameter vector.
        - yi are the values of the measured relaxation data set.
        - yi(theta) are the values of the back calculated relaxation data set.
        - dyi(theta)/dthetaj are the values of the back calculated gradient.
        - d2yi(theta)/dthetaj.dthetak are the values of the back calculated Hessian.
        - sigma_i are the values of the error set.


    @param data:                The vector of yi values.
    @type data:                 numpy array
    @param back_calc_vals:      The vector of yi(theta) values.
    @type back_calc_vals:       numpy array
    @param back_calc_grad_j:    The matrix of dyi(theta)/dthetaj values.
    @type back_calc_grad_j:     numpy matrix
    @param back_calc_grad_k:    The matrix of dyi(theta)/dthetak values.
    @type back_calc_grad_k:     numpy matrix
    @param back_calc_hess:      The 3rd rank tensor of d2yi(theta)/dthetaj.dthetak values.
    @type back_calc_hess:       numpy matrix
    @param errors:              The vector of sigma_i values.
    @type errors:               numpy array
    @return:                    The chi-squared Hessian.
    @rtype:                     numpy 3rd rank tensor
    """

    # Calculate the chi-squared Hessian.
    #return 2.0 * sum(1.0 / (errors**2) * (back_calc_grad_j * back_calc_grad_k - (data - back_calc_vals) * back_calc_hess), axis=0)
    #return 2.0 * sum((back_calc_grad_j * back_calc_grad_k - (data - back_calc_vals) * back_calc_hess) / errors**2, axis=0)

    # Calculate the chi-squared Hessian.
    # This is faster than the above sums, and having the errors term first appears to minimise roundoff errors.
    d2chi2 = 0.0
    for i in xrange(len(data)):
        d2chi2 = d2chi2 + 2.0 / (errors[i]**2) * (back_calc_grad_j[i] * back_calc_grad_k[i] - (data[i] - back_calc_vals[i]) * back_calc_hess[i])

    return d2chi2
