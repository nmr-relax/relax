/*
Copyright (C) 2003 Edward d'Auvergne

This file is part of the program relax.

Relax is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Relax is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with relax; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/


double chi2(double data[], double back_calc[], double errors[]) {
	/* Function to calculate the chi-squared value.

	The chi-sqared equation
	~~~~~~~~~~~~~~~~~~~~~~~
	        _n_
	        \    (yi - yi()) ** 2
	Chi2  =  >   ----------------
	        /__    sigma_i ** 2
	        i=1

	where:
		yi are the values of the measured data set.
		yi() are the values of the back calculated data set.
		sigma_i are the values of the error set.

	The chi-squared value is returned.
	*/

	int i;
	double chi2;

	chi2 = 0.0;
	for (i = 0; i <= 5; ++i) {
		chi2 = chi2 + (data[i] - back_calc[i]) / errors[i];
	}

	return chi2;
}
