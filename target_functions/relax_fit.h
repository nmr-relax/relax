/*
 * Copyright (C) 2006-2012 Edward d'Auvergne
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


/* The maximum number of parameters for this function */
#define MAXPARAMS 3

/* The maximum number of spectral time points */
#define MAXTIMES 30

/* Python 2.2 and earlier support for Python C modules */
#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif


/****************************************/
/* External, hence permanent, variables */
/****************************************/

/* Variables sent to the setup function to be stored for later use */
int num_params, num_times;

/* Pointers to PyObjects */
double *params, *values, *sd, *relax_times, *scaling_matrix;

/* Variables used for storage during the function calls of optimisation */
double back_calc[MAXTIMES];
