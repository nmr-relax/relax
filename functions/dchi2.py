from Numeric import Float64, zeros


def dchi2(data, back_calc_vals, back_calc_grad, errors):
	"""Function to create the chi-squared gradient.

	The chi-sqared gradient
	~~~~~~~~~~~~~~~~~~~~~~~
	               _n_
	 dChi2         \   /  yi - yi()      dyi()  \ 
	-------  =  -2  >  | ----------  .  ------- |
	dthetaj        /__ \ sigma_i**2     dthetaj /
	               i=1

	where:
		yi are the values of the measured data set.
		yi() are the values of the back calculated data set.
		sigma_i are the values of the error set.

	The chi-squared gradient vector is returned.

	"""

	# Initialise the chi-squared gradient.
	dchi2 = zeros((len(back_calc_grad)), Float64)

	# Calculate the chi-squared gradient.
	for i in range(len(data)):
		if errors[i] != 0.0:
			# Parameter independent terms.
			a = -2.0 * (data[i] - back_calc_vals[i]) / (errors[i]**2)
			for j in range(len(back_calc_grad)):
				dchi2[j] = dchi2[j] + a * back_calc_grad[j, i]
		else:
			for j in range(len(back_calc_grad)):
				dchi2[j] = 1e99
			break

	return dchi2
