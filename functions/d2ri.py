from Numeric import Float64, copy, zeros

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

		# Debugging code.
		#print "<<< Ri >>>"

		# Initialise the relaxation array.
		self.data.ri = copy.deepcopy(self.data.ri_prime)

		# Calculate the transformed relaxation values.
		self.Ri_prime()

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			if self.mf.data.data_types[i] == 'NOE':
				self.data.ri[i] = self.calc_noe(i)


	def calc_noe(self, i):
		"Calculate the NOE value."

		if self.mf.data.noe_r1_table[i] == None:
			raise NameError, "Incomplete code, need to somehow calculate the r1 value."

		if self.data.ri_prime[self.mf.data.noe_r1_table[i]] == 0:
			noe = 1e99
		else:
			noe = 1.0 + (self.mf.data.gh/self.mf.data.gx) * (self.data.ri_prime[i] / self.data.ri_prime[self.mf.data.noe_r1_table[i]])
		return noe
