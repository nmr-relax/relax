/*
 * Copyright (C) 2003-2013 Edward d'Auvergne
 *
 * This file is part of the program relax (http://www.nmr-relax.com).
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdio.h>
#include <math.h>
#include "c_chi2.h"

/* Define the function for calculating the square of a number. */
#define square(x) (x)*(x)


double chi2(double *values, double *sd, double *back_calc, int num_times) {
    /* Function to calculate the chi-squared value.

    The chi-sqared equation
    =======================

    The equation is::

                    _n_
                    \    (yi - yi(theta)) ** 2
    chi^2(theta)  =  >   ---------------------
                    /__      sigma_i ** 2
                    i=1

    where:
        - i is the index over data sets.
        - theta is the parameter vector.
        - yi are the values of the measured data set.
        - yi(theta) are the values of the back calculated data set.
        - sigma_i are the values of the error set.

    The chi-squared value is returned.
    */

    int i;
    double chi2 = 0.0;

    /* Loop over the time points and sum the chi-squared components */
    for (i = 0; i < num_times; ++i) {
        chi2 = chi2 + square((values[i] - back_calc[i]) / sd[i]);
    }

    return chi2;
}


void dchi2(double dchi2[], double data[], double back_calc_vals[], double back_calc_grad[][MAX_DATA], double errors[], int num_times, int M) {
    /* Calculate the full chi-squared gradient.

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
    @param data:            The vector of yi values.
    @type data:             numpy rank-1 size N array
    @param back_calc_vals:  The vector of yi(theta) values.
    @type back_calc_vals:   numpy rank-1 size N array
    @param back_calc_grad:  The matrix of dyi(theta)/dtheta values.
    @type back_calc_grad:   numpy rank-2 size MxN array
    @param errors:          The vector of sigma_i values.
    @type errors:           numpy rank-1 size N array
    @param M:               The dimensions of the gradient.
    @type M:                int
    */

    /* Declarations. */
    int i, j;

    /* Calculate the chi-squared gradient. */
    for (j = 0; j < M; ++j) {
        for (i = 0; i < num_times; ++i) {
            dchi2[j] += -2.0 / (errors[i]*errors[i]) * (data[i] - back_calc_vals[i]) * back_calc_grad[j][i];
        }
    }
}
