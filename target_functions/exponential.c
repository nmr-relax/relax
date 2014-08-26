/*
 * Copyright (C) 2006-2013 Edward d'Auvergne
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


/* The exponential function is needed. */
#include <math.h>

/* functions for the exponential */
#include "exponential.h"


void exponential(double I0, double R, double *relax_times, double *back_calc, int num_times) {
    /* Function to back calculate the intensity values from an exponential.
     *
     * The function used is::
     *
     *     I = I0 * exp(-R.t)
    */

    /* Declarations */
    int i;

    /* Loop over the time points */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value */
        if (R == 0.0)
            back_calc[i] = I0;

        /* Back calculate */
        else
            back_calc[i] = I0 * exp(-relax_times[i] * R);

    }
}

void exponential_dI0(double I0, double R, double *relax_times, double back_calc_grad[][MAXTIMES], int num_times) {
    /* Calculate the dI0 partial derivate of the 2-parameter exponential curve.
    */

    /* Declarations */
    int i;

    /* Loop over the time points */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value */
        if (R == 0.0)
            back_calc_grad[1][i] = 1.0;

        /* The partial derivate */
        else
            back_calc_grad[1][i] = exp(-relax_times[i] * R);
    }
}


void exponential_dR(double I0, double R, double *relax_times, double back_calc_grad[][MAXTIMES], int num_times) {
    /* Calculate the dR partial derivate of the 2-parameter exponential curve.
    */

    /* Declarations */
    int i;

    /* Loop over the time points */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value */
        if (R == 0.0)
            back_calc_grad[0][i] = -I0 * relax_times[i];

        /* The partial derivate */
        else
            back_calc_grad[0][i] = -I0 * relax_times[i] * exp(-relax_times[i] * R);
    }
}
