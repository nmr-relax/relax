class dRi_prime:
	def __init__(self):
		"Function for the calculation of the transformed relaxation gradients."


	def dRi_prime(self):
		"""Function for the calculation of the transformed relaxation gradients.

		The transformed relaxation gradients
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.dri_prime
		Dimension:  2D, (parameters, transformed relaxation data)
		Type:  Numeric matrix, Float64
		Dependencies:  self.data.jw, self.data.djw
		Required by:  self.data.dri, self.data.d2ri


		Formulae
		~~~~~~~~

		Components
		~~~~~~~~~~

			Dipolar
			~~~~~~~
				      1   / mu0  \ 2  (gH.gN.h_bar)**2
				d  =  - . | ---- |  . ----------------
				      4   \ 4.pi /         <r**6>


				         3   / mu0  \ 2  (gH.gN.h_bar)**2
				d'  =  - - . | ---- |  . ----------------
				         2   \ 4.pi /         <r**7>


			CSA
			~~~
				      (wN.csa)**2
				c  =  -----------
				           3

				       2.wN**2.csa
				c'  =  -----------
				            3


			R1()
			~~~~
				J_R1_d  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

				                 dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
				J_R1_d_prime  =  ---------  +  3 . ------  +  6 . ---------
				                    dmf             dmf              dmf


				J_R1_c  =  J(wN)

				                 dJ(wN)
				J_R1_c_prime  =  ------
				                  dmf



			R2()
			~~~~
				J_R2_d  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

				                     dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN)
				J_R2_d_prime  =  4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . ---------
				                      dmf         dmf             dmf            dmf             dmf


				J_R2_c  =  4J(0) + 3J(wN)

				                     dJ(0)         dJ(wN)
				J_R2_c_prime  =  4 . -----  +  3 . ------
				                      dmf           dmf


			sigma_noe()
			~~~~~~~~~~~
				J_sigma_noe  =  6J(wH+wN) - J(wH-wN)

				                          dJ(wH+wN)     dJ(wH-wN)
				J_sigma_noe_prime  =  6 . ---------  -  ---------
				                             dmf           dmf


		Spectral density parameter
		~~~~~~~~~~~~~~~~~~~~~~~~~~

			dR1()
			-----  =  d . J_R1_d_prime  +  c . J_R1_c_prime
			 dJj


			dR2()     d                    c
			-----  =  - . J_R2_d_prime  +  - . J_R2_c_prime
			 dJj      2                    6


			dsigma_noe()
			------------  = d . J_sigma_noe_prime
			    dJj


		Chemical exchange
		~~~~~~~~~~~~~~~~~

			dR1()
			-----  =  0
			dRex


			dR2()
			-----  =  1
			dRex


			 dR2()
			------  =  (2.pi.wH)**2
			drhoex


			dsigma_noe()
			------------  =  0
			   dRex


		CSA
		~~~

			dR1()
			-----  =  c' . J_R1_c
			dcsa


			dR2()     c'
			-----  =  - . J_R2_c
			dcsa      6


			dsigma_noe()
			------------  =  0
			    dcsa


		Bond length
		~~~~~~~~~~~

			dR1()
			-----  =  d' . J_R1_d
			 dr


			dR2()     d'
			-----  =  - . J_R2_d
			 dr       2


			dsigma_noe()
			------------  =  d' . J_sigma_noe
			     dr

		"""

		# Calculate the spectral density gradients.
		self.dJw()

		# Initialise the components of the transformed relaxation equations.
		self.data.j_dip_comps_prime = zeros((self.mf.data.num_ri), Float64)
		self.data.j_csa_comps_prime = zeros((self.mf.data.num_ri), Float64)
		if match('m[34]', self.data.model):
			self.data.rex_comps_prime = zeros((self.mf.data.num_ri), Float64)
		if match('m6', self.data.model):
			self.data.dip_comps_prime = zeros((self.mf.data.num_ri), Float64)
			self.data.csa_comps_prime = zeros((self.mf.data.num_ri), Float64)

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			frq_num = self.mf.data.remap_table[i]

			# R1 components.
			if self.mf.data.data_types[i]  == 'R1':
				self.data.j_dip_comps_prime[i] = self.data.djw[frq_num, 2] + 3.0*self.data.djw[frq_num, 1] + 6.0*self.data.djw[frq_num, 4]
				self.data.j_csa_comps_prime[i] = self.data.djw[frq_num, 1]
				if match('m6', self.data.model):
					self.data.dip_comps_prime[i] = self.mf.data.dipole_prime
					self.data.csa_comps_prime[i] = self.mf.data.csa_prime[frq_num]

			# R2 components.
			elif self.mf.data.data_types[i] == 'R2':
				self.data.j_dip_comps_prime[i] = 4.0*self.data.djw[frq_num, 0] + self.data.djw[frq_num, 2] + 3.0*self.data.djw[frq_num, 1] + 6.0*self.data.djw[frq_num, 3] + 6.0*self.data.djw[frq_num, 4]
				self.data.j_csa_comps_prime[i] = 4.0*self.data.djw[frq_num, 0] + 3.0*self.data.djw[frq_num, 1]
				if match('m[34]', self.data.model):
					self.data.rex_comps_prime = (1e-8 * self.mf.data.frq[frq_num])**2
				if match('m6', self.data.model):
					self.data.dip_comps_prime[i] = self.mf.data.dipole_prime / 2.0
					self.data.csa_comps_prime[i] = self.mf.data.csa_prime[frq_num] / 6.0

			# sigma_noe components.
			elif self.mf.data.data_types[i] == 'NOE':
				self.data.j_dip_comps_prime[i] = 6.0*self.data.djw[frq_num, 4] - self.data.djw[frq_num, 2]
				if match('m6', self.data.model):
					self.data.dip_comps_prime[i] = self.mf.data.dipole_prime

		# Initialise the transformed relaxation gradients.
		self.data.dri_prime = zeros((len(self.data.params), self.mf.data.num_ri), Float64)

		# Calculate the transformed relaxation gradients.
		for param in range(len(self.data.ri_param_types)):
			# Spectral density parameter derivatives.
			if self.data.ri_param_types[param] == 'Jj':
				self.data.dri_prime[param] = self.data.dip_comps * self.data.j_dip_comps_prime + self.data.csa_comps * self.data.j_csa_comps_prime

			# Chemical exchange derivatives.
			elif self.data.ri_param_types[param] == 'Rex':
				self.data.dri_prime[param] = self.data.rex_comps_prime

			# CSA derivatives.
			elif self.data.ri_param_types[param] == 'CSA':
				self.data.dri_prime[param] = self.data.csa_comps_prime * self.data.j_csa_comps

			# Bond length derivatives.
			elif self.data.ri_param_types[param] == 'r':
				self.data.dri_prime[param] = self.data.dip_comps_prime * self.data.j_dip_comps
