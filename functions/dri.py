class dRi:
	def __init__(self):
		"An additional layer of equations to simplify the relaxation equations, gradients, and hessians."
		


	def dRi(self):
		"""An additional layer of equations to simplify the relaxation equations, gradients, and hessians.

		The R1 and R2 equations are left alone, while the NOE is decomposed into the cross relaxation rate equation and the R1 equation.


		The relaxation gradients
		~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.dri
		Dimension:  2D, (parameters, relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.data.ri_prime, self.data.dri_prime
		Required by:  self.data.dchi2, self.data.d2chi2


		Formulae
		~~~~~~~~

			 dR1()       dR1'()
			-------  =  -------
			dthetaj     dthetaj


			 dR2()       dR2'()
			-------  =  -------
			dthetaj     dthetaj


			 dNOE()     gH      1      /        dsigma_noe()                    dR1()  \ 
			-------  =  -- . ------- . | R1() . ------------  -  sigma_noe() . ------- |
			dthetaj     gN   R1()**2   \          dthetaj                      dthetaj /


		"""

		# Calculate the transformed relaxation gradients (the transformed relaxation values have been previously calculated by the dChi2 function).
		self.dRi_prime()

		# Copy the relaxation gradients from self.data.dri_prime
		self.data.dri = copy.deepcopy(self.data.dri_prime)

		# Loop over the relaxation values and modify the NOE gradients.
		for i in range(self.mf.data.num_ri):
			if self.mf.data.data_types[i] == 'NOE':
				r1 = self.data.ri_prime[self.mf.data.noe_r1_table[i]]
				if r1 == None:
					raise NameError, "Incomplete code, need to somehow calculate the r1 value."
				for param in range(len(self.data.ri_param_types)):
					if r1 == 0.0:
						self.data.dri[param, i] = 1e99
					else:
						self.data.dri[param, i] = (self.mf.data.gh/self.mf.data.gx) * (1.0 / r1**2) * (r1 * self.data.dri_prime[param, i] - self.data.ri_prime[i] * self.data.dri_prime[param, self.mf.data.noe_r1_table[i]])
