from Numeric import copy

class d2Ri:
	def __init__(self):
		"An additional layer of equations to simplify the relaxation equations, gradients, and hessians."
		


	def d2Ri(self):
		"""An additional layer of equations to simplify the relaxation equations, gradients, and hessians.

		The R1 and R2 equations are left alone, while the NOE is decomposed into the cross relaxation rate equation and the R1 equation.


		The transformation equations
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.ri
		Dimension:  1D, (relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.data.ri_prime
		Required by:  self.data.chi2, self.data.dchi2, self.data.d2chi2
		Stored:  Yes


		Formulae
		~~~~~~~~

		Relaxation equations
		~~~~~~~~~~~~~~~~~~~~

			R1()  =  R1'()


			R2()  =  R2'()


			               gH   sigma_noe()
			NOE()  =  1 +  -- . -----------
			               gN      R1()

		"""

		# Calculate the transformed relaxation hessians (the transformed relaxation values and gradients have been previously calculated by the d2Chi2 function).
		self.d2Ri_prime()

		# Copy the relaxation hessians from self.data.d2ri_prime
		self.data.d2ri = copy.deepcopy(self.data.d2ri_prime)

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			if self.mf.data.data_types[i] == 'NOE':
				for param1 in range(len(self.data.ri_param_types)):
					for param2 in range(param1 + 1)):
						self.data.d2ri[i, param1, param2] = self.calc_d2noe_dmf2(i, param1, param2)
						if param1 != param2:
							self.data.d2ri[i, param2, param1] = self.data.d2ri[i, param1, param2]


	def calc_d2noe_dmf2(self, i, param1, param2):
		"Calculate the NOE value."

		if self.mf.data.noe_r1_table[i] == None:
			raise NameError, "Incomplete code, need to somehow calculate the r1 value."

		r1 = self.data.ri_prime[self.mf.data.noe_r1_table[i]]

		if r1 == 0:
			d2noe = 1e99
		else:
			a = self.data.ri_prime[i] * (2.0 * self.data.dri_prime[self.mf.data.noe_r1_table[i], param1] * self.data.dri_prime[self.mf.data.noe_r1_table[i], param2] - r1 * self.data.d2ri_prime[self.mf.data.noe_r1_table[i], param1, param2])
			b = r1 * (self.data.dri_prime[i, param1] * self.data.dri_prime[self.mf.data.noe_r1_table[i], param2] + self.data.dri_prime[i, param1] * self.data.dri_prime[self.mf.data.noe_r1_table[i], param2] - r1 * self.data.d2ri_prime[i, param1, param2])
			d2noe = (self.mf.data.gh/self.mf.data.gx) * (1.0 / r1**3) * (a - b)
		return d2noe
