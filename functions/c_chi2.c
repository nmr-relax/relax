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
