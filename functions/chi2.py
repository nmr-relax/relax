from Numeric import Float64, zeros


# Chi-squared value.
####################

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


# Chi-squared gradient.
#######################

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

	# Count the number of parameters in the model.
	num_params = len(back_calc_grad[0])

	# Initialise the chi-squared gradient.
	dchi2 = zeros((num_params), Float64)

	# Calculate the chi-squared gradient.
	for i in range(len(data)):
		if errors[i] != 0.0:
			# Parameter independent terms.
			a = -2.0 * (data[i] - back_calc_vals[i]) / (errors[i]**2)
			for j in range(num_params):
				dchi2[j] = dchi2[j] + a * back_calc_grad[i, j]
		else:
			for j in range(num_params):
				dchi2[j] = 1e99
			break

	return dchi2


# Chi-squared hessian.
######################

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

	# Count the number of parameters in the model.
	num_params = len(back_calc_grad[0])

	# Initialise the chi-squared hessian.
	d2chi2 = zeros((num_params, num_params), Float64)

	# Calculate the chi-squared hessian.
	for i in range(len(data)):
		if errors[i] != 0.0:
			# Parameter independent terms.
			a = 2.0 / (errors[i]**2)
			b = data[i] - back_calc_vals[i]

			# Loop over the parameters.
			for j in range(num_params):
				# Loop over the parameters from 1 to k.
				for k in range(j + 1):
					d2chi2[j, k] = d2chi2[j, k] + a * (back_calc_grad[i, j] * back_calc_grad[i, k] - b * back_calc_hess[i, j, k])

					# Make the hessian symmetric.
					if j != k:
						d2chi2[k, j] = d2chi2[j, k]
		else:
			# Loop over the parameters.
			for j in range(num_params):
				# Loop over the parameters from 1 to k.
				for k in range(j + 1):
					d2chi2[j, k] = 1e99

					# Make the hessian symmetric.
					if j != k:
						d2chi2[k, j] = 1e99
			break

	return d2chi2
