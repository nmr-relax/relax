from Numeric import Float64, zeros

class dchi2:
	def __init__(self):
		"Function to create the chi-squared gradient."


	def dchi2(self, params, diff_type, diff_params, model, relax_data, errors):
		"""Function to create the chi-squared gradient.

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


		The chi-sqared gradient
		~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.dchi2
		Dimension:  1D, (parameters)
		Type:  Numeric array, Float64
		Dependencies:  self.data.ri, self.data.dri
		Required by:  None


		Formula
		~~~~~~~
		               _n_
		 dChi2         \   /  Ri - Ri()      dRi()  \ 
		-------  =  -2  >  | ----------  .  ------- |
		dthetaj        /__ \ sigma_i**2     dthetaj /
		               i=1

		where:
			Ri are the values of the measured relaxation data set.
			Ri() are the values of the back calculated relaxation data set.
			sigma_i are the values of the error set.

		"""

		# debug.
		if self.mf.min_debug == 2:
			print "\n< dchi2 >"
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

		# Initialise the chi-squared gradient.
		self.data.dchi2 = zeros((len(self.data.params)), Float64)

		# Calculate the chi-squared gradient.
		for i in range(len(self.data.relax_data)):
			if self.data.errors[i] != 0.0:
				# Parameter independent terms.
				a = -2.0 * (self.data.relax_data[i] - self.data.ri[i]) / (self.data.errors[i]**2)
				for param in range(len(self.data.params)):
					self.data.dchi2[param] = self.data.dchi2[param] + a * self.data.dri[param, i]
			else:
				for param in range(len(self.params)):
					self.data.dchi2[param] = 1e99
				break

		# debug.
		if self.mf.min_debug == 2:
			print "J(w):  " + `self.data.jw`
			print "dJ(w): " + `self.data.djw`
			print "Ri:    " + `self.data.ri`
			print "dRi:   " + `self.data.dri`
			print "dchi2: " + `self.data.dchi2`
			print "\n"

		return self.data.dchi2
