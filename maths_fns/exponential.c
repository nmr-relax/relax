/*
 * Copyright (C) 2006 Edward d'Auvergne
 *
 * This file is part of the program relax.
 *
 * relax is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * relax is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with relax; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


/* This include must come first */
#include <Python.h>

/* The Numeric array object header file, must come second */
#include <Numeric/arrayobject.h>

/* The header for all functions which will be called */
#include "relax_fit.h"



void exponential(void) {
	/* Function to back calculate the peak intensities.
	*/

    /* Declarations */
    extern PyArrayObject *params, *relax_times;
    extern int *num_times;
    double Rx, I0;
    int i;


    /* Get the parameters */
    Rx = *(double *) (params->data);
    I0 = *(double *) (params->data + params->strides[0]);

    /* Loop over the time points */
    /* for (i = 0; i < num_times; i++) { */
    printf("\n\nNum times: %i\n", num_times);
    for (i = 0; i < 6; i++) {
        /* Back calculate */
        printf("%-20g", I0 * exp(-*(double *) (relax_times->data + i*relax_times->strides[0])/Rx));

    }
}
