from Numeric import equal

class chi2:
	def __init__(self):
		"Function to calculate the chi-squared value."


	def chi2(self, mf_params, diff_type, diff_params, mf_model, relax_data, errors):
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


		The chi-sqared equation
		~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.chi2
		Type:  Double precision floating point value.
		Dependencies:  self.data.ri
		Required by:  None
		Stored:  No


		Formula
		~~~~~~~
		        _n_
		        \    (Ri - Ri()) ** 2
		Chi2  =  >   ----------------
		        /__    sigma_i ** 2
		        i=1

		where:
			Ri are the values of the measured relaxation data set.
			Ri() are the values of the back calculated relaxation data set.
			sigma_i are the values of the error set.

		Returned is the chi-squared value.
		"""

		# debug.
		if self.mf.min_debug == 2:
			print "\n< chi2 >"
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
		# values in self.data.relax_test.
		test = [ self.data.relax_data[:], self.data.errors[:], self.data.mf_params.tolist(), self.data.mf_model ]
		if test != self.data.relax_test:
			self.Ri()
			self.data.relax_test = test[:]

		# Initialise the chi-squared statistic.
		self.data.chi2 = 0.0

		# Calculate the chi-squared statistic.
		for i in range(len(self.data.relax_data)):
			if self.data.errors[i] != 0.0:
				self.data.chi2 = self.data.chi2 + ((self.data.relax_data[i] - self.data.ri[i]) / self.data.errors[i])**2
			else:
				self.data.chi2 = 1e99
				continue

		# debug.
		if self.mf.min_debug == 2:
			print "J(w): " + `self.data.jw`
			print "Ri: " + `self.data.ri`
			print "chi2: " + `self.data.chi2`
			print "\n"

		return self.data.chi2
