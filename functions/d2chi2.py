from Numeric import Float64, zeros

class d2chi2:
	def __init__(self):
		"Function to create the chi-squared hessian."


	def d2chi2(self, params, diff_type, diff_params, model, relax_data, errors):
		"""Function to create the chi-squared hessian.

		Function arguments
		~~~~~~~~~~~~~~~~~~

		1:  params - a list containing the parameter values specific for the given model.
		The order of parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}
		2:  diff_type - string.  The diffusion tensor, ie 'iso', 'axial', 'aniso'
		3:  diff_params - array.  An array with the diffusion parameters
		4:  model - string.  The model
		5:  relax_data - array.  An array containing the experimental relaxation values.
		6:  errors - array.  An array containing the experimental errors.


		The chi-sqared hessian
		~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.d2chi2
		Dimension:  2D, (parameters, parameters)
		Type:  Numeric array, Float64
		Dependencies:  self.data.ri, self.data.dri, self.data.d2ri
		Required by:  None


		Formula
		~~~~~~~
			                      _n_
			     d2chi2           \       1      /  dRi()     dRi()                         d2Ri()     \ 
			---------------  =  2  >  ---------- | ------- . -------  -  (Ri - Ri()) . --------------- |
			dthetaj.dthetak       /__ sigma_i**2 \ dthetaj   dthetak                   dthetaj.dthetak / 
			                      i=1
		"""

		# debug.
		if self.mf.min_debug == 2:
			print "\n< d2chi2 >"
			print "Params: " + `params`

		self.data.params = params
		self.data.diff_type = diff_type
		self.data.diff_params = diff_params
		self.data.model = model
		self.data.relax_data = relax_data
		self.data.errors = errors

		# Test to see if relaxation values and spectral density values have previously been calculated for the current parameter values,
		# If not, calculate the relaxation values which will then calculate the spectral density values, and store the current data and parameter
		# values in self.data.relax_test and self.data.gradient_test.
		test = [ self.data.relax_data[:], self.data.errors[:], self.data.params.tolist(), self.data.model ]
		if test != self.data.relax_test:
			self.init_param_types()
			self.Ri()
			self.data.relax_test = test[:]
		if test != self.data.gradient_test:
			self.init_param_types()
			self.dRi()
			self.data.gradient_test = test[:]

		# Calculate the relaxation hessians.
		self.d2Ri()

		# Initialise the chi-squared hessian.
		self.data.d2chi2 = zeros((len(self.data.params), len(self.data.params)), Float64)

		# Calculate the chi-squared hessian.
		for i in range(len(self.data.relax_data)):
			if self.data.errors[i] != 0.0:
				# Parameter independent terms.
				a = 2.0 / (self.data.errors[i]**2)
				b = self.data.relax_data[i] - self.data.ri[i]

				# Loop over the parameters.
				for param_j in range(len(self.data.params)):
					# Loop over the parameters from 1 to param_k.
					for param_k in range(param_j + 1):
						self.data.d2chi2[param_j, param_k] = self.data.d2chi2[param_j, param_k] + a * (self.data.dri[param_j, i] * self.data.dri[param_k, i] - b * self.data.d2ri[param_j, param_k, i])
						if param_j != param_k:
							self.data.d2chi2[param_k, param_j] = self.data.d2chi2[param_j, param_k]
			else:
				# Loop over the parameters.
				for param_k in range(len(self.data.params)):
					# Loop over the parameters from 1 to param_k.
					for param_j in range(param_k + 1):
						self.data.d2chi2[param_j, param_j] = 1e99
						if param_j != param_k:
							self.data.d2chi2[param_k, param_j] = 1e99
				break

		# debug.
		if self.mf.min_debug == 2:
			print "J(w):   " + `self.data.jw`
			print "dJ(w):  " + `self.data.djw`
			print "d2J(w): " + `self.data.d2jw`
			print "Ri:     " + `self.data.ri`
			print "dRi:    " + `self.data.dri`
			print "d2Ri:   " + `self.data.d2ri`
			print "d2chi2: " + `self.data.d2chi2`
			print "\n"

		return self.data.d2chi2
