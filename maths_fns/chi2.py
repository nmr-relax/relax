###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


from Numeric import Float64, sum, transpose, zeros


# Chi-squared value.
####################

def chi2(data, back_calc_vals, errors):
    """Function to calculate the chi-squared value.

    The chi-sqared equation
    ~~~~~~~~~~~~~~~~~~~~~~~
            _n_
            \    (yi - yi()) ** 2
    Chi2  =  >   ----------------
            /__    sigma_i ** 2
            i=1

    where:
        yi are the values of the measured data set.
        yi() are the values of the back calculated data set.
        sigma_i are the values of the error set.

    The chi-squared value is returned.
    """

    # Calculate the chi-squared statistic.
    return sum((1.0 / errors * (data - back_calc_vals))**2)


# Chi-squared gradient.
#######################

def dchi2(data, back_calc_vals, back_calc_grad, errors):
    """Function to create the chi-squared gradient.

    The chi-sqared gradient
    ~~~~~~~~~~~~~~~~~~~~~~~
                   _n_
     dChi2         \   /  yi - yi()      dyi()  \ 
    -------  =  -2  >  | ----------  .  ------- |
    dthetaj        /__ \ sigma_i**2     dthetaj /
                   i=1

    where:
        yi are the values of the measured data set.
        yi() are the values of the back calculated data set.
        sigma_i are the values of the error set.

    The chi-squared gradient vector is returned.
    """

    # Calculate the chi-squared gradient.
    return -2.0 * sum(1.0 / (errors**2) * (data - back_calc_vals) * back_calc_grad)


# Chi-squared Hessian.
######################

def d2chi2(data, back_calc_vals, back_calc_grad_j, back_calc_grad_k, back_calc_hess, errors):
    """Function to create the chi-squared Hessian.

    The chi-squared Hessian
    ~~~~~~~~~~~~~~~~~~~~~~~
                          _n_
         d2chi2           \       1      /  dyi()     dyi()                         d2yi()     \ 
    ---------------  =  2  >  ---------- | ------- . -------  -  (yi - yi()) . --------------- |
    dthetaj.dthetak       /__ sigma_i**2 \ dthetaj   dthetak                   dthetaj.dthetak /
                          i=1

    where:
        yi are the values of the measured relaxation data set.
        yi() are the values of the back calculated relaxation data set.
        sigma_i are the values of the error set.
    """

    # Calculate the chi-squared Hessian.
    #return 2.0 * sum(1.0 / (errors**2) * (back_calc_grad_j * back_calc_grad_k - (data - back_calc_vals) * back_calc_hess))
    #return 2.0 * sum((back_calc_grad_j * back_calc_grad_k - (data - back_calc_vals) * back_calc_hess) / errors**2)

    # Calculate the chi-squared Hessian.
    # This is faster than the above sums, and having the errors term first appears to minimise roundoff errors.
    d2chi2 = 0.0
    for i in xrange(len(data)):
        d2chi2 = d2chi2 + 2.0 / (errors[i]**2) * (back_calc_grad_j[i] * back_calc_grad_k[i] - (data[i] - back_calc_vals[i]) * back_calc_hess[i])

    return d2chi2
