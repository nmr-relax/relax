/*
 * Copyright (C) 2006-2014 Edward d'Auvergne
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

/* Get the maximum dimensions. */
#include "dimensions.h"


void exponential(double I0, double R, double relax_times[MAX_DATA], double back_calc[MAX_DATA], int num_times) {
    /* Function to back calculate the intensity values from an exponential.
     *
     * The function used is::
     *
     *     I = I0 * exp(-R.t)
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value. */
        if (R == 0.0)
            back_calc[i] = I0;

        /* Back calculate. */
        else
            back_calc[i] = I0 * exp(-relax_times[i] * R);

    }
}


void exponential_dI0(double I0, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times) {
    /* Calculate the dI0 partial derivate of the 2-parameter exponential curve.
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value. */
        if (R == 0.0)
            back_calc_grad[param_index][i] = 1.0;

        /* The partial derivate. */
        else
            back_calc_grad[param_index][i] = exp(-relax_times[i] * R);
    }
}


void exponential_dR(double I0, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times) {
    /* Calculate the dR partial derivate of the 2-parameter exponential curve.
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value. */
        if (R == 0.0)
            back_calc_grad[param_index][i] = -I0 * relax_times[i];

        /* The partial derivate. */
        else
            back_calc_grad[param_index][i] = -I0 * relax_times[i] * exp(-relax_times[i] * R);
    }
}


void exponential_dI02(double I0, double R, int I0_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times) {
    /* Calculate the dI0 double partial derivate of the 2-parameter exponential curve.
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Everything is zero! */
        back_calc_hess[I0_index][I0_index][i] = 0.0;
    }
}


void exponential_dR_dI0(double I0, double R, int R_index, int IO_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times) {
    /* Calculate the dR, dI0 second partial derivate of the 2-parameter exponential curve.
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value. */
        if (R == 0.0)
            back_calc_hess[IO_index][R_index][i] = -relax_times[i];

        /* The second partial derivate. */
        else
            back_calc_hess[IO_index][R_index][i] = -relax_times[i] * exp(-relax_times[i] * R);

        /* Hessian symmetry. */
        back_calc_hess[R_index][IO_index][i] = back_calc_hess[IO_index][R_index][i];
    }
}


void exponential_dR2(double I0, double R, int R_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times) {
    /* Calculate the dR second partial derivate of the 2-parameter exponential curve.
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value. */
        if (R == 0.0)
            back_calc_hess[R_index][R_index][i] = I0 * square(relax_times[i]);

        /* The partial derivate. */
        else
            back_calc_hess[R_index][R_index][i] = I0 * square(relax_times[i]) * exp(-relax_times[i] * R);
    }
}
