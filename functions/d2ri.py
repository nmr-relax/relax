from Numeric import copy

class d2Ri:
	def __init__(self):
		"An additional layer of equations to simplify the relaxation equations, gradients, and hessians."
		


	def d2Ri(self):
		"""An additional layer of equations to simplify the relaxation equations, gradients, and hessians.

		The R1 and R2 equations are left alone, while the NOE is decomposed into the cross relaxation rate equation and the R1 equation.


		The relaxation hessians
		~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.d2ri
		Dimension:  3D, (parameters, parameters, relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.data.ri_prime, self.data.dri_prime, self.data.d2ri_prime
		Required by:  self.data.d2chi2


		Formulae
		~~~~~~~~

			     d2R1()             d2R1'()
			---------------  =  ---------------
			dthetaj.dthetak     dthetaj.dthetak


			     d2R2()             d2R2'()
			---------------  =  ---------------
			dthetaj.dthetak     dthetaj.dthetak


			    d2NOE()         gH      1      /               /      dR1()     dR1()                  d2R1()     \            / dsigma_noe()    dR1()       dR1()    dsigma_noe()             d2sigma_noe()  \ \ 
			---------------  =  -- . ------- . | sigma_noe() . | 2 . ------- . -------  -  R1() . --------------- |  -  R1() . | ------------ . -------  +  ------- . ------------  -  R1() . --------------- | |
			dthetaj.dthetak     gN   R1()**3   \               \     dthetaj   dthetak            dthetaj.dthetak /            \   dthetaj      dthetak     dthetaj     dthetak               dthetaj.dthetak / /

		"""

		# Calculate the transformed relaxation hessians (the transformed relaxation values and gradients have been previously calculated by the d2Chi2 function).
		self.d2Ri_prime()

		# Copy the relaxation hessians from self.data.d2ri_prime
		self.data.d2ri = copy.deepcopy(self.data.d2ri_prime)

		# Loop over the relaxation values and modify the NOE hessians.
		for i in range(self.mf.data.num_ri):
			if self.mf.data.data_types[i] == 'NOE':
				r1 = self.data.ri_prime[self.mf.data.noe_r1_table[i]]
				if r1 == None:
					raise NameError, "Incomplete code, need to somehow calculate the r1 value."
				for param1 in range(len(self.data.ri_param_types)):
					for param2 in range(param1 + 1):
						if r1 == 0:
							self.data.d2ri[param1, param2, i] = 1e99
						else:
							a = self.data.ri_prime[i] * (2.0 * self.data.dri_prime[param1, self.mf.data.noe_r1_table[i]] * self.data.dri_prime[param2, self.mf.data.noe_r1_table[i]] - r1 * self.data.d2ri_prime[param1, param2, self.mf.data.noe_r1_table[i]])
							b = r1 * (self.data.dri_prime[param1, i] * self.data.dri_prime[param2, self.mf.data.noe_r1_table[i]] + self.data.dri_prime[param1, i] * self.data.dri_prime[param2, self.mf.data.noe_r1_table[i]] - r1 * self.data.d2ri_prime[param1, param2, i])
							self.data.d2ri[param1, param2, i] = (self.mf.data.gh/self.mf.data.gx) * (1.0 / r1**3) * (a - b)
						if param1 != param2:
							self.data.d2ri[param2, param1, i] = self.data.d2ri[param1, param2, i]
