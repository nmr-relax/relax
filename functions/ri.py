from Numeric import copy

class Ri:
	def __init__(self):
		"An additional layer of equations to simplify the relaxation equations, gradients, and hessians."
		


	def Ri(self):
		"""An additional layer of equations to simplify the relaxation equations, gradients, and hessians.

		The R1 and R2 equations are left alone, while the NOE is decomposed into the cross relaxation rate equation and the R1 equation.


		The relaxation equations
		~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.ri
		Dimension:  1D, (relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.data.ri_prime
		Required by:  self.data.chi2, self.data.dchi2, self.data.d2chi2


		Formulae
		~~~~~~~~

			R1()  =  R1'()


			R2()  =  R2'()

			               gH   sigma_noe()
			NOE()  =  1 +  -- . -----------
			               gN      R1()

		"""

		# Calculate the transformed relaxation values.
		self.Ri_prime()

		# Initialise the relaxation values.
		self.data.ri = copy.deepcopy(self.data.ri_prime)

		# Calculate the NOE values.
		for i in range(self.mf.data.num_ri):
			if self.mf.data.data_types[i] == 'NOE':
				if self.mf.data.noe_r1_table[i] == None:
					raise NameError, "Incomplete code, need to somehow calculate the r1 value."

				if self.data.ri_prime[self.mf.data.noe_r1_table[i]] == 0:
					self.data.ri[i] = 1e99
				else:
					self.data.ri[i] = 1.0 + (self.mf.data.gh/self.mf.data.gx) * (self.data.ri_prime[i] / self.data.ri_prime[self.mf.data.noe_r1_table[i]])

