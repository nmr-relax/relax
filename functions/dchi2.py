from Numeric import Float64, equal, zeros

class dchi2:
	def __init__(self):
		"Function to create the chi-squared gradient vector."


	def dchi2(self, mf_params, diff_type, diff_params, mf_model, relax_data, errors):
		"""Function to create the chi-squared gradient vector.

		Function arguments
		~~~~~~~~~~~~~~~~~~

		1:  mf_params - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}
		2:  diff_type - string.  The diffusion tensor, ie 'iso', 'axial', 'aniso'
		3:  diff_params - array.  An array with the diffusion parameters
		4:  mf_model - string.  The model-free model
		5:  relax_data - array.  An array containing the experimental relaxation values.
		6:  errors - array.  An array containing the experimental errors.


		The chi-sqared gradient
		~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.dchi2
		Dimension:  1D, (model-free parameters)
		Type:  Numeric array, Float64
		Dependencies:  self.data.ri, self.data.dri
		Required by:  None
		Stored:  No


		Formula
		~~~~~~~
		              _n_
		d Chi2        \   /  Ri - Ri()     d Ri() \ 
		------  =  -2  >  | ----------  .  ------ |
		 d mf         /__ \ sigma_i**2      d mf  /
		              i=1

		where:
			Ri are the values of the measured relaxation data set.
			Ri() are the values of the back calculated relaxation data set.
			sigma_i are the values of the error set.

		Returned is the chi-squared gradient array.
		"""

		# debug.
		if self.mf.min_debug == 2:
			print "\n< dchi2 >"
			print "Mf params: " + `mf_params`

		self.data.mf_params = mf_params
		self.data.diff_type = diff_type
		self.data.diff_params = diff_params
		self.data.mf_model = mf_model
		self.data.relax_data = relax_data
		self.data.errors = errors

		# Test to see if relaxation array and spectral density matrix have previously been calculated for the current parameter values,
		# ie, if the derivative is calculated before the function evaluation!
		# If not, calculate the relaxation array which will then calculate the spectral density matrix, and store the current data and parameter
		# values in self.mf.data.mf_data.relax_test.
		test = [ self.data.relax_data[:], self.data.errors[:], self.data.mf_params.tolist(), self.data.mf_model ]
		if test != self.data.relax_test:
			self.Ri()
			self.data.relax_test = test[:]
			self.init_param_types()

		# Calculate the relaxation gradient matrix (important that the relaxation array has previously been calculated
		# as the function dRi assumes this to be the case).
		self.dRi()
		self.data.gradient_test = test[:]

		# Initialise the chi-squared gradient vector.
		self.data.dchi2 = zeros((len(self.data.mf_params)), Float64)

		# Calculate the chi-squared gradient vector.
		for i in range(len(self.data.relax_data)):
			if self.data.errors[i] != 0.0:
				# Model-free parameter independent terms.
				a = -2.0 * (self.data.relax_data[i] - self.data.ri[i]) / (self.data.errors[i]**2)
				for mf_param in range(len(self.data.mf_params)):
					self.data.dchi2[mf_param] = self.data.dchi2[mf_param] + a * self.data.dri[i, mf_param]
			else:
				for mf_param in range(len(self.mf_params)):
					self.data.dchi2[mf_param] = 1e99
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
