/*
 * Copyright (C) 2003, 2006 Edward d'Auvergne
 *
 * This file is part of the program relax.
 *
 * relax is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * relax is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with relax.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdio.h>
#include <math.h>

#define square(x) (x)*(x)


double chi2(double *values, double *sd, double *back_calc, int num_times) {
	/* Function to calculate the chi-squared value.

	The chi-sqared equation
	~~~~~~~~~~~~~~~~~~~~~~~
	          _n_
	          \    (yi - yi()) ** 2
	Chi2()  =  >   ----------------
	          /__    sigma_i ** 2
	          i=1

	where:
		yi are the values of the measured data set.
		yi() are the values of the back calculated data set.
		sigma_i are the values of the error set.

	The chi-squared value is returned.
	*/

	int i;
	double chi2 = 0.0;

    /* Loop over the time points and sum the chi-squared components */
	for (i = 0; i < num_times; ++i) {
		chi2 = chi2 + square((values[i] - back_calc[i]) / sd[i]);
	}

	return chi2;
}
