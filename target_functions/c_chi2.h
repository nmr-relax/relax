/*
 * Copyright (C) 2006  Gary S Thompson (see https://gna.org/users for contact
 *                                      details)
 * Copyright (C) 2014 Edward d'Auvergne
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

#ifndef RELAX_C_CHI2 
#define RELAX_C_CHI2

/* The maximum number of parameters and data points */
#define MAX_PARAMS 10
#define MAX_DATA 50

double chi2(double values[], double sd[], double back_calc[], int num_times);
void dchi2(double dchi2[], double data[], double back_calc_vals[], double back_calc_grad[][MAX_DATA], double errors[], int num_times, int M);
void d2chi2(double d2chi2[MAX_PARAMS][MAX_PARAMS], double data[MAX_DATA], double back_calc_vals[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], double back_calc_hess[MAX_PARAMS][MAX_PARAMS][MAX_DATA], double errors[MAX_DATA], int num_times, int M);

#endif
