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

/* Include the exponential header file to access the square() function and the maximum dimensions. */
#include "exponential.h"


void exponential_sat(double Iinf, double R, double relax_times[MAX_DATA], double back_calc[MAX_DATA], int num_times) {
    /* Back calculate the intensity values from the exponential of the saturation recovery experiment.
     *
     * The function used is::
     *
     *     I = Iinf * (1 - exp(-R.t)).
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value. */
        if (R == 0.0)
            back_calc[i] = 0.0;

        /* Back calculate. */
        else
            back_calc[i] = Iinf * (1.0 - exp(-relax_times[i] * R));

    }
}


void exponential_sat_dIinf(double Iinf, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times) {
    /* Calculate the dIinf partial derivate of the saturation recovery exponential curve.
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value. */
        if (R == 0.0)
            back_calc_grad[param_index][i] = 0.0;

        /* The partial derivate. */
        else
            back_calc_grad[param_index][i] = (1.0 - exp(-relax_times[i] * R));
    }
}


void exponential_sat_dR(double Iinf, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times) {
    /* Calculate the dR partial derivate of the 2-parameter exponential curve.
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value. */
        if (R == 0.0)
            back_calc_grad[param_index][i] = Iinf * relax_times[i];

        /* The partial derivate. */
        else
            back_calc_grad[param_index][i] = Iinf * relax_times[i] * exp(-relax_times[i] * R);
    }
}


void exponential_sat_dIinf2(double Iinf, double R, int Iinf_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times) {
    /* Calculate the dIinf double partial derivate of the saturation recovery experiment.
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Everything is zero! */
        back_calc_hess[Iinf_index][Iinf_index][i] = 0.0;
    }
}


void exponential_sat_dR_dIinf(double Iinf, double R, int R_index, int Iinf_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times) {
    /* Calculate the dR, dIinf second partial derivate of the 2-parameter exponential curve.
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value. */
        if (R == 0.0)
            back_calc_hess[Iinf_index][R_index][i] = relax_times[i];

        /* The second partial derivate. */
        else
            back_calc_hess[Iinf_index][R_index][i] = relax_times[i] * exp(-relax_times[i] * R);

        /* Hessian symmetry. */
        back_calc_hess[R_index][Iinf_index][i] = back_calc_hess[Iinf_index][R_index][i];
    }
}


void exponential_sat_dR2(double Iinf, double R, int R_index, double relax_times[MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], int num_times) {
    /* Calculate the dR second partial derivate of the saturation recovery experiment.
    */

    /* Declarations. */
    int i;

    /* Loop over the time points. */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value. */
        if (R == 0.0)
            back_calc_hess[R_index][R_index][i] = -Iinf * square(relax_times[i]);

        /* The partial derivate. */
        else
            back_calc_hess[R_index][R_index][i] = -Iinf * square(relax_times[i]) * exp(-relax_times[i] * R);
    }
}
