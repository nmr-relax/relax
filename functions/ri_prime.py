from Numeric import Float64, zeros
from re import match

class Ri_prime:
	def __init__(self):
		"Function for back calculating the transformed relaxation values R1, R2, and sigma_noe."


	def Ri_prime(self):
		"""Function for back calculation of the transformed relaxation values R1, R2, and sigma_noe.

		The transformed relaxation equations
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.ri_prime
		Dimension:  1D, (transformed relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.data.jw
		Required by:  self.data.ri, self.data.dri, self.data.d2ri


		Formulae
		~~~~~~~~

		Components
		~~~~~~~~~~
			      1   / mu0  \ 2  (gH.gN.h_bar)**2
			d  =  - . | ---- |  . ----------------
			      4   \ 4.pi /         <r**6>

			      (wN.csa)**2
			c  =  -----------
			           3

			J_R1_d  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

			J_R1_c  =  J(wN)

			J_R2_d  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

			J_R2_c  =  4J(0) + 3J(wN)

			J_sigma_noe  =  6J(wH+wN) - J(wH-wN)


		Relaxation equations
		~~~~~~~~~~~~~~~~~~~~

			R1()  =  d . J_R1_d  +  c . J_R1_c


			         d              c
			R2()  =  - . J_R2_d  +  - . J_R2_c  +  Rex
			         2              6


			sigma_noe()  =  d . J_sigma_noe

		"""

		# Calculate the spectral density values.
		self.Jw()

		# Initialise the components of the transformed relaxation equations.
		self.data.dip_comps = zeros((self.mf.data.num_ri), Float64)
		self.data.j_dip_comps = zeros((self.mf.data.num_ri), Float64)
		self.data.csa_comps = zeros((self.mf.data.num_ri), Float64)
		self.data.j_csa_comps = zeros((self.mf.data.num_ri), Float64)
		if match('m[34]', self.data.model):
			self.data.rex_comps = zeros((self.mf.data.num_ri), Float64)

		# Calculate the components of the transformed relaxation equations.
		for i in range(self.mf.data.num_ri):
			frq_num = self.mf.data.remap_table[i]

			# R1 components.
			if self.mf.data.data_types[i]  == 'R1':
				self.data.dip_comps[i] = self.mf.data.dipole_const
				self.data.j_dip_comps[i] = self.data.jw[frq_num, 2] + 3.0*self.data.jw[frq_num, 1] + 6.0*self.data.jw[frq_num, 4]
				self.data.csa_comps[i] = self.mf.data.csa_const[frq_num]
				self.data.j_csa_comps[i] = self.data.jw[frq_num, 1]

			# R2 components.
			elif self.mf.data.data_types[i] == 'R2':
				self.data.dip_comps[i] = self.mf.data.dipole_const / 2.0
				self.data.j_dip_comps[i] = 4.0*self.data.jw[frq_num, 0] + self.data.jw[frq_num, 2] + 3.0*self.data.jw[frq_num, 1] + 6.0*self.data.jw[frq_num, 3] + 6.0*self.data.jw[frq_num, 4]
				self.data.csa_comps[i] = self.mf.data.csa_const[frq_num] / 6.0
				self.data.j_csa_comps[i] = 4.0*self.data.jw[frq_num, 0] + 3.0*self.data.jw[frq_num, 1]
				if self.data.model == 'm3':
					self.data.rex_comps[i] = self.data.params[1] * (1e-8 * self.mf.data.frq[frq_num])**2
				elif self.data.model == 'm4':
					self.data.rex_comps[i] = self.data.params[2] * (1e-8 * self.mf.data.frq[frq_num])**2

			# sigma_noe components.
			elif self.mf.data.data_types[i] == 'NOE':
				self.data.dip_comps[i] = self.mf.data.dipole_const
				self.data.j_dip_comps[i] = 6.0*self.data.jw[frq_num, 4] - self.data.jw[frq_num, 2]

		# Initialise the transformed relaxation values.
		self.data.ri_prime = zeros((self.mf.data.num_ri), Float64)

		# Calculate the transformed relaxation values.
		if match('m[34]', self.data.model):
			self.data.ri_prime = self.data.dip_comps * self.data.j_dip_comps + self.data.csa_comps * self.data.j_csa_comps + self.data.rex_comps
		else:
			self.data.ri_prime = self.data.dip_comps * self.data.j_dip_comps + self.data.csa_comps * self.data.j_csa_comps
