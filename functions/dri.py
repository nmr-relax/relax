from Numeric import Float64, copy, zeros

class dRi:
	def __init__(self):
		"An additional layer of equations to simplify the relaxation equations, gradients, and hessians."
		


	def dRi(self):
		"""An additional layer of equations to simplify the relaxation equations, gradients, and hessians.

		The R1 and R2 equations are left alone, while the NOE is decomposed into the cross relaxation rate equation and the R1 equation.


		The relaxation gradients
		~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.dri
		Dimension:  1D, (relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.data.ri_prime, self.data.dri_prime
		Required by:  self.data.dchi2, self.data.d2chi2
		Stored:  Yes


		Formulae
		~~~~~~~~

			dR1()     dR1'()
			-----  =  ------
			 dmf       dmf


			dR2()     dR2'()
			-----  =  ------
			 dmf       dmf


			dNOE()    gH      1      /        dsigma_noe()                   dR1() \ 
			------  = -- . ------- . | R1() . ------------  -  sigma_noe() . ----- |
			 dmf      gN   R1()**2   \            dmf                         dmf  /


		"""

		# Calculate the transformed relaxation gradients.
		self.dRi_prime()

		# Initialise the relaxation gradients.
		self.data.dri = copy.deepcopy(self.data.dri_prime)

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			for param in range(len(self.data.ri_param_types)):
				if self.mf.data.data_types[i] == 'NOE':
					self.data.dri[i] = self.calc_dnoe_dmf(i, param)


	def calc_dnoe_dmf(self, i):
		"Calculate the derivative of the NOE value."

		if self.mf.data.noe_r1_table[i] == None:
			raise NameError, "Incomplete code, need to somehow calculate the r1 value."

		if self.data.ri_prime[self.mf.data.noe_r1_table[i]] == 0.0:
			dnoe = 1e99
		else:
			dnoe = (self.mf.data.gh/self.mf.data.gx) * (1.0 / self.data.ri_prime[self.mf.data.noe_r1_table[i]]**2) * (self.data.ri_prime[self.mf.data.noe_r1_table[i]] * self.data.dri_prime[i] - self.data.ri_prime[i] * self.data.dri[self.mf.data.noe_r1_table[i], param])
		return dnoe
