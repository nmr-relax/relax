/*
 * Copyright (C) 2006 Edward d'Auvergne
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


/* This include must come first */
#include <Python.h>

/* The header for all functions which will be called */
#include "relax_fit.h"



void exponential(double *params, double *relax_times, double *back_calc, int num_times) {
	/* Function to back calculate the peak intensities.
	*/

    /* Declarations */
    double Rx, I0;
    int i;


    /* Loop over the time points */
    /* for (i = 0; i < num_times; i++) { */
    for (i = 0; i < num_times; i++) {
        /* Zero Rx value */
        if (params[0] == 0.0)
            back_calc[i] = 0.0;

        /* Back calculate */
        else
            back_calc[i] = params[1] * exp(-relax_times[i] * params[0]);

    }
}
