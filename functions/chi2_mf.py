from Numeric import equal

class chi2:
	def __init__(self, mf):
		"Function to calculate the chi-squared value."

		self.mf = mf


	def calc(self, mf_params, diff_type, diff_params, mf_model, relax_data, errors):
		"""Function to calculate the chi-squared value.

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


		The chi-sqared value/statistic
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.chi2
		Type:  Single double precision floating point value.
		Dependencies:  self.ri, self.jw
		Required by:  None
		Stored:  No
		Formula:
			        _n_
			        \    / (Ri - R(xi)) \ 2
			Chi2  =  >   | ------------ |
			        /__  \   sigma_i    /
			        i=1

		Returned is the chi-squared value.
		"""

		self.mf_params = mf_params
		self.diff_type = diff_type
		self.diff_params = diff_params
		self.mf_model = mf_model
		self.relax_data = relax_data
		self.errors = errors

		# debug.
		#print "\n< chi2 >"
		#print "Mf params: " + `self.mf_params`

		# Test to see if relaxation array and spectral density matrix have previously been calculated for the current parameter values,
		# ie, if the derivative is calculated before the function evaluation!
		# If not, calculate the relaxation array which will then calculate the spectral density matrix, and store the current data and parameter
		# values in self.mf.data.mf_data.relax_test.
		test = [ self.relax_data[:], self.errors[:], self.mf_params.tolist(), self.mf_model ]
		if test != self.mf.data.mf_data.relax_test:
			self.mf.mf_functions.Ri.calc(self.mf_params, self.diff_type, self.diff_params, self.mf_model)
			self.mf.data.mf_data.relax_test = test[:]

		# Initialise the chi-squared statistic.
		self.chi2 = 0.0

		# Calculate the chi-squared statistic.
		for i in range(len(self.relax_data)):
			if self.errors[i] != 0.0:
				self.chi2 = self.chi2 + ((self.relax_data[i] - self.mf.data.mf_data.ri[i]) / self.errors[i])**2
			else:
				self.chi2 = 1e99
				continue

		# debug.
		#print "J(w): " + `self.mf.data.mf_data.jw`
		#print "Ri: " + `self.mf.data.mf_data.ri`
		#print "chi2: " + `self.chi2`
		#print "\n"

		return self.chi2
