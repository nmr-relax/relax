from Numeric import Float64, equal, zeros

class d2chi2:
	def __init__(self, mf):
		"Function to create the chi-squared hessian matrix."

		self.mf = mf


	def calc(self, mf_params, diff_type, diff_params, mf_model, relax_data, errors):
		"""Function to create the chi-squared hessian matrix.

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


		The chi-sqared hessian
		~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.d2chi2
		Dimension:  2D, (model-free parameters, model-free parameters)
		Type:  Numeric array, Float64
		Dependencies:  self.ri, self.dri, self.d2ri
		Required by:  None
		Stored:  No


		Formula
		~~~~~~~
			                _n_
			 d2chi2         \       1      / dRi()   dRi()                     d2 Ri()   \ 
			---------  =  2  >  ---------- | ----- . -----  -  (Ri - Ri()) . ----------- |
			dmfj.dmfk       /__ sigma_i**2 \ dmf_j   dmf_k                   dmfj . dmfk / 
			                i=1

		Returned is the chi-squared hessian matrix.
		"""

		self.mf_params = mf_params
		self.diff_type = diff_type
		self.diff_params = diff_params
		self.mf_model = mf_model
		self.relax_data = relax_data
		self.errors = errors

		# debug.
		if self.mf.min_debug == 2:
			print "\n< d2chi2 >"
			print "Mf params: " + `self.mf_params`

		# Test to see if relaxation array and spectral density matrix have previously been calculated for the current parameter values,
		# ie, if the derivative is calculated before the function evaluation!
		# If not, calculate the relaxation array which will then calculate the spectral density matrix, and store the current data and parameter
		# values in self.mf.data.mf_data.relax_test.
		test = [ self.relax_data[:], self.errors[:], self.mf_params.tolist(), self.mf_model ]
		if test != self.mf.data.mf_data.relax_test:
			self.mf.mf_functions.Ri.calc(self.mf_params, self.diff_type, self.diff_params, self.mf_model)
			self.mf.data.mf_data.relax_test = test[:]

		test = [ self.relax_data[:], self.errors[:], self.mf_params.tolist(), self.mf_model ]
		if test != self.mf.data.mf_data.gradient_test:
			self.mf.mf_functions.dRi.calc(self.mf_params, self.diff_type, self.diff_params, self.mf_model)
			self.mf.data.mf_data.gradient_test = test[:]

		# Calculate the relaxation hessian matrix (important that the relaxation gradient matrix has previously been calculated
		# as the function d2Ri assumes this to be the case).
		self.mf.mf_functions.d2Ri.calc(self.mf_params, self.diff_type, self.diff_params, self.mf_model)

		# Initialise the chi-squared hessian matrix.
		self.d2chi2 = zeros((len(self.mf_params), len(self.mf_params)), Float64)

		# Calculate the chi-squared hessian matrix.
		for i in range(len(self.relax_data)):
			if self.errors[i] != 0.0:
				# Model-free parameter independent terms.
				a = 2.0 / (self.errors[i]**2)
				b = self.relax_data[i] - self.mf.data.mf_data.ri[i]
				print "Relax data: " + `self.relax_data[i]`
				print "Back calc:  " + `self.mf.data.mf_data.ri[i]`
				print "Diff:       " + `self.relax_data[i] - self.mf.data.mf_data.ri[i]`
				print "a:          " + `a`

				# Loop over the model-free parameters.
				for mfj in range(len(self.mf_params)):
					print "\tmfj: " + `mfj`
					# Loop over the model-free parameters from 1 to mfk.
					for mfk in range(mfj + 1):
						print "\t\tmfk: " + `mfk`
						c = self.mf.data.mf_data.dri[i, mfj] * self.mf.data.mf_data.dri[i, mfk]
						print "\t\t\tdrij:                  " + `self.mf.data.mf_data.dri[i, mfj]`
						print "\t\t\tdrik:                  " + `self.mf.data.mf_data.dri[i, mfk]`
						print "\t\t\tdrij*drik:             " + `c`
						print "\t\t\td2ri:                  " + `self.mf.data.mf_data.d2ri[i, mfj, mfk]`
						print "\t\t\tdiff*d2ri:             " + `b * self.mf.data.mf_data.d2ri[i, mfj, mfk]`
						print "\t\t\tdrij*drik - diff*d2ri: " + `c - b * self.mf.data.mf_data.d2ri[i, mfj, mfk]`
						if mfj == mfk:
							self.d2chi2[mfj][mfj] = self.d2chi2[mfj][mfj] + a * c
							#self.d2chi2[mfj][mfj] = self.d2chi2[mfj][mfj] + a * (c - b * self.mf.data.mf_data.d2ri[i, mfj, mfj])
						else:
							self.d2chi2[mfj][mfk] = self.d2chi2[mfj][mfk] + a * c
							self.d2chi2[mfk][mfj] = self.d2chi2[mfk][mfj] + a * c
							#self.d2chi2[mfj][mfk] = self.d2chi2[mfj][mfk] + a * (c - b * self.mf.data.mf_data.d2ri[i, mfj, mfk])
							#self.d2chi2[mfk][mfj] = self.d2chi2[mfk][mfj] + a * (c - b * self.mf.data.mf_data.d2ri[i, mfk, mfj])
			else:
				# Loop over the model-free parameters.
				for mfk in range(len(self.mf_params)):
					# Loop over the model-free parameters from 1 to mfk.
					for mfj in range(mfk + 1):
						if mfj == mfk:
							self.d2chi2[mfj][mfj] = 1e99
						else:
							self.d2chi2[mfj][mfk] = 1e99
							self.d2chi2[mfk][mfj] = 1e99
				break

		# debug.
		if self.mf.min_debug == 2:
			print "J(w):   " + `self.mf.data.mf_data.jw`
			print "dJ(w):  " + `self.mf.data.mf_data.djw`
			print "d2J(w): " + `self.mf.data.mf_data.d2jw`
			print "Ri:     " + `self.mf.data.mf_data.ri`
			print "dRi:    " + `self.mf.data.mf_data.dri`
			print "d2Ri:   " + `self.mf.data.mf_data.d2ri`
			print "d2chi2: " + `self.d2chi2`
			print "\n"

		return self.d2chi2
