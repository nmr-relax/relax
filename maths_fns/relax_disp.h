/*
 * Copyright (C) 2006 Edward d'Auvergne
 * Copyright (C) 2009 Sebastien Morin
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


/* Required for the Python/C API??? */

#define PY_ARRAY_UNIQUE_SYMBOL numarray


/* The maximum number of parameters for this function */
#define MAXPARAMS 3

/* The maximum number of spectral time points */
#define MAXTIMES 30


/****************************************/
/* External, hence permanent, variables */
/****************************************/

/* Variables sent to the setup function to be stored for later use */
PyArrayObject *numpy_values, *numpy_sd, *numpy_cpmg_frqs, *numpy_scaling_matrix;
int num_params, num_times;
double *sd;

/* Variables sent to 'func', 'dfunc', and 'd2func' during optimisation */
/*PyArrayObject *numpy_params;*/

/* Pointers to contiguous PyArrayObjects */
double *values, *sd, *cpmg_frqs, *scaling_matrix;
/*double *params;*/


/* Variables used for storage during the function calls of optimisation */
double back_calc[MAXTIMES];

