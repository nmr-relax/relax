###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2008 Edward d'Auvergne                            #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

"""Module containing functions for calculating the chi-squared value, gradient, and Hessian."""

# Python module imports.
from numpy import dot, sum, transpose


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
        - i is the index over data sets.
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - sigma_i are the values of the error set.


    @param data:            The vector of yi values.
    @type data:             numpy rank-1 size N array
    @param back_calc_vals:  The vector of yi(theta) values.
    @type back_calc_vals:   numpy rank-1 size N array
    @param errors:          The vector of sigma_i values.
    @type errors:           numpy rank-1 size N array
    @return:                The chi-squared value.
    @rtype:                 float
    """

    # Calculate the chi-squared statistic.
    return sum((1.0 / errors * (data - back_calc_vals))**2, axis=0)


# Chi-squared gradient.
#######################


def dchi2(dchi2, M, data, back_calc_vals, back_calc_grad, errors):
    """Calculate the full chi-squared gradient.

    The chi-squared gradient
    ========================

    The equation is::

                             _n_
        dchi^2(theta)        \   / yi - yi(theta)     dyi(theta) \ 
        -------------  =  -2  >  | --------------  .  ---------- |
           dthetaj           /__ \   sigma_i**2        dthetaj   /
                             i=1

    where
        - i is the index over data sets.
        - j is the parameter index of the gradient.
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - dyi(theta)/dthetaj are the values of the back calculated gradient for parameter j.
        - sigma_i are the values of the error set.


    @param dchi2:           The chi-squared gradient data structure to place the gradient elements
                            into.
    @type dchi2:            numpy rank-1 size M array
    @param M:               The dimensions of the gradient.
    @type M:                int
    @param data:            The vector of yi values.
    @type data:             numpy rank-1 size N array
    @param back_calc_vals:  The vector of yi(theta) values.
    @type back_calc_vals:   numpy rank-1 size N array
    @param back_calc_grad:  The matrix of dyi(theta)/dtheta values.
    @type back_calc_grad:   numpy rank-2 size MxN array
    @param errors:          The vector of sigma_i values.
    @type errors:           numpy rank-1 size N array
    """

    # Calculate the chi-squared gradient.
    grad = -2.0 * dot(1.0 / (errors**2) * (data - back_calc_vals), transpose(back_calc_grad))

    # Pack the elements.
    for i in xrange(M):
        dchi2[i] = grad[i]


def dchi2_element(data, back_calc_vals, back_calc_grad_j, errors):
    """Calculate the chi-squared gradient element j.

    The chi-squared gradient
    ========================

    The equation is::

                             _n_
        dchi^2(theta)        \   / yi - yi(theta)     dyi(theta) \ 
        -------------  =  -2  >  | --------------  .  ---------- |
           dthetaj           /__ \   sigma_i**2        dthetaj   /
                             i=1

    where
        - i is the index over data sets.
        - j is the parameter index of the gradient.
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - dyi(theta)/dthetaj are the values of the back calculated gradient for parameter j.
        - sigma_i are the values of the error set.


    @param data:                The vector of yi values.
    @type data:                 numpy rank-1 size N array
    @param back_calc_vals:      The vector of yi(theta) values.
    @type back_calc_vals:       numpy rank-1 size N array
    @param back_calc_grad_j:    The vector of dyi(theta)/dthetaj values for parameter j.
    @type back_calc_grad_j:     numpy rank-1 size N array
    @param errors:              The vector of sigma_i values.
    @type errors:               numpy rank-1 size N array
    @return:                    The chi-squared gradient element j.
    @rtype:                     float
    """

    # Calculate the chi-squared gradient.
    return -2.0 * sum(1.0 / (errors**2) * (data - back_calc_vals) * back_calc_grad_j, axis=0)


# Chi-squared Hessian.
######################


def d2chi2(d2chi2, M, data, back_calc_vals, back_calc_grad, back_calc_hess, errors):
    """Calculate the full chi-squared Hessian.

    The chi-squared Hessian
    =======================

    The equation is::

                              _n_
        d2chi^2(theta)        \       1      / dyi(theta)   dyi(theta)                        d2yi(theta)   \ 
        ---------------  =  2  >  ---------- | ---------- . ----------  -  (yi-yi(theta)) . --------------- |
        dthetaj.dthetak       /__ sigma_i**2 \  dthetaj      dthetak                        dthetaj.dthetak /
                              i=1

    where
        - i is the index over data sets.
        - j is the parameter index for the first dimension of the Hessian.
        - k is the parameter index for the second dimension of the Hessian.
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - dyi(theta)/dthetaj are the values of the back calculated gradient for parameter j.
        - d2yi(theta)/dthetaj.dthetak are the values of the back calculated Hessian for the
        parameters j and k.
        - sigma_i are the values of the error set.


    @param d2chi2:              The chi-squared Hessian data structure to place the Hessian elements
                                into.
    @type d2chi2:               numpy rank-2 size MxM array
    @param M:                   The size of the first dimension of the Hessian.
    @type M:                    int
    @param data:                The vector of yi values.
    @type data:                 numpy rank-1 size N array
    @param back_calc_vals:      The vector of yi(theta) values.
    @type back_calc_vals:       numpy rank-1 size N array
    @param back_calc_grad:      The matrix of dyi(theta)/dtheta values.
    @type back_calc_grad:       numpy rank-2 size MxN array
    @param back_calc_hess:      The matrix of d2yi(theta)/dtheta.dtheta values.
    @type back_calc_hess:       numpy rank-3 size MxMxN array
    @param errors:              The vector of sigma_i values.
    @type errors:               numpy rank-1 size N array
    """

    # Calculate the chi-squared Hessian.
    for j in xrange(M):
        for k in xrange(M):
            d2chi2[j, k] = 0.0
            for i in xrange(len(data)):
                d2chi2[j, k] = d2chi2[j, k] + 2.0 / (errors[i]**2) * (back_calc_grad[j, i] * back_calc_grad[k, i] - (data[i] - back_calc_vals[i]) * back_calc_hess[j, k, i])


def d2chi2_element(data, back_calc_vals, back_calc_grad_j, back_calc_grad_k, back_calc_hess_jk, errors):
    """Calculate the chi-squared Hessian element {j, k}.

    The chi-squared Hessian
    =======================

    The equation is::

                              _n_
        d2chi^2(theta)        \       1      / dyi(theta)   dyi(theta)                        d2yi(theta)   \ 
        ---------------  =  2  >  ---------- | ---------- . ----------  -  (yi-yi(theta)) . --------------- |
        dthetaj.dthetak       /__ sigma_i**2 \  dthetaj      dthetak                        dthetaj.dthetak /
                              i=1

    where
        - i is the index over data sets.
        - j is the parameter index for the first dimension of the Hessian.
        - k is the parameter index for the second dimension of the Hessian.
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - dyi(theta)/dthetaj are the values of the back calculated gradient for parameter j.
        - d2yi(theta)/dthetaj.dthetak are the values of the back calculated Hessian for the
        parameters j and k.
        - sigma_i are the values of the error set.


    @param data:                The vector of yi values.
    @type data:                 numpy rank-1 size N array
    @param back_calc_vals:      The vector of yi(theta) values.
    @type back_calc_vals:       numpy rank-1 size N array
    @param back_calc_grad_j:    The vector of dyi(theta)/dthetaj values for parameter j.
    @type back_calc_grad_j:     numpy rank-1 size N array
    @param back_calc_grad_k:    The vector of dyi(theta)/dthetak values for parameter k.
    @type back_calc_grad_k:     numpy rank-1 size N array
    @param back_calc_hess_jk:   The vector of d2yi(theta)/dthetaj.dthetak values at {j, k}.
    @type back_calc_hess_jk:    numpy rank-1 size N array
    @param errors:              The vector of sigma_i values.
    @type errors:               numpy rank-1 size N array
    @return:                    The chi-squared Hessian element {j,k}.
    @rtype:                     float
    """

    # Calculate the chi-squared Hessian.
    #return 2.0 * sum(1.0 / (errors**2) * (back_calc_grad_j * back_calc_grad_k - (data - back_calc_vals) * back_calc_hess), axis=0)
    #return 2.0 * sum((back_calc_grad_j * back_calc_grad_k - (data - back_calc_vals) * back_calc_hess) / errors**2, axis=0)

    # Calculate the chi-squared Hessian.
    # This is faster than the above sums, and having the errors term first appears to minimise roundoff errors.
    d2chi2 = 0.0
    for i in xrange(len(data)):
        d2chi2 = d2chi2 + 2.0 / (errors[i]**2) * (back_calc_grad_j[i] * back_calc_grad_k[i] - (data[i] - back_calc_vals[i]) * back_calc_hess_jk[i])

    # Return the {j, k} element.
    return d2chi2
