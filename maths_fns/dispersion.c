/*
 * Copyright (C) 2006 Edward d'Auvergne
 * Copyright (C) 2009 Sebastien Morin
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

/* The numpy array object header file, must come second */
#include <numpy/arrayobject.h>

/* The header for all functions which will be called */
#include "relax_disp.h"



void dispersion(double *params, double *cpmg_frqs, double *back_calc, int num_times) {
	/* Function to back calculate the effective transversal relaxation rate (R2eff).
	*/

    /* Declarations */
    double R2, Rex, kex;
    int i;


    /* Loop over the time points */
    for (i = 0; i < num_times; i++) {
        /* Back calculate */
        back_calc[i] = params[0] + params[1] * (1 - 2 * tanh(params[2] / (2 * 4 * cpmg_frqs[i])) * ((4 * cpmg_frqs[i] ) / params[2]));

    }
}
