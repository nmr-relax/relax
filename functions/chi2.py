def chi2(data, back_calc_vals, errors):
	"""Function to calculate the chi-squared value.

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

	"""

	# Calculate the chi-squared statistic.
	chi2 = 0.0
	for i in range(len(data)):
		if errors[i] != 0.0:
			chi2 = chi2 + ((data[i] - back_calc_vals[i]) / errors[i])**2
		else:
			chi2 = 1e99
			continue
	return chi2
