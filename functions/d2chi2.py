from Numeric import Float64, zeros


def d2chi2(data, back_calc_vals, back_calc_grad, back_calc_hess, errors):
	"""Function to create the chi-squared hessian.

	The chi-squared hessian
	~~~~~~~~~~~~~~~~~~~~~~~
	                      _n_
	     d2chi2           \       1      /  dRi()     dRi()                         d2Ri()     \ 
	---------------  =  2  >  ---------- | ------- . -------  -  (Ri - Ri()) . --------------- |
	dthetaj.dthetak       /__ sigma_i**2 \ dthetaj   dthetak                   dthetaj.dthetak / 
		                      i=1

     	where:
		Ri are the values of the measured relaxation data set.
		Ri() are the values of the back calculated relaxation data set.
		sigma_i are the values of the error set.

	"""

	# Initialise the chi-squared hessian.
	d2chi2 = zeros((len(back_calc_grad), len(back_calc_grad)), Float64)

	# Calculate the chi-squared hessian.
	for i in range(len(data)):
		if errors[i] != 0.0:
			# Parameter independent terms.
			a = 2.0 / (errors[i]**2)
			b = data[i] - back_calc_vals[i]

			# Loop over the parameters.
			for j in range(len(back_calc_grad)):
				# Loop over the parameters from 1 to k.
				for k in range(j + 1):
					d2chi2[j, k] = d2chi2[j, k] + a * (back_calc_grad[j, i] * back_calc_grad[k, i] - b * back_calc_hess[j, k, i])

					# Make the hessian symmetric.
					if j != k:
						d2chi2[k, j] = d2chi2[j, k]
		else:
			# Loop over the parameters.
			for j in range(len(params)):
				# Loop over the parameters from 1 to k.
				for k in range(j + 1):
					d2chi2[j, k] = 1e99

					# Make the hessian symmetric.
					if j != k:
						d2chi2[k, j] = 1e99
			break

	return d2chi2
