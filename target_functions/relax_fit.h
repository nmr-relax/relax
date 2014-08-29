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


/* Get the maximum dimensions. */
#include "dimensions.h"

/* Python 2.2 and earlier support for Python C modules. */
#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

/* Define the function for calculating the square of a number. */
#define square(x) ((x)*(x))


/****************************************/
/* External, hence permanent, variables. */
/*****************************************/

/* Variables sent to the setup function to be stored for later use. */
static int num_params, num_times;

/* Hardcoded parameter indices. */
static int index_R = 0;
static int index_I0 = 1;

/* Variables used for storage during the function calls of optimisation. */
static double back_calc[MAX_DATA];
static double back_calc_grad[MAX_PARAMS][MAX_DATA];
static double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA];
static double dchi2_vals[MAX_PARAMS];
static double d2chi2_vals[MAX_PARAMS][MAX_PARAMS];
static double jacobian_matrix[MAX_PARAMS][MAX_DATA];
static double params[MAX_PARAMS];
static double relax_times[MAX_DATA];
static double scaling_matrix[MAX_PARAMS];
static double sd[MAX_DATA];
static double values[MAX_DATA];
static double variance[MAX_DATA];
