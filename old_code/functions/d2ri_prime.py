from Numeric import Float64, zeros
from re import match

class d2Ri_prime:
	def __init__(self):
		"Function for the calculation of the trasformed relaxation hessians."


	def d2Ri_prime(self):
		"""Function for the calculation of the trasformed relaxation hessians.

		The trasformed relaxation hessians
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.d2ri_prime
		Dimension:  3D, (parameters, parameters, relaxation data)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  self.data.jw, self.data.djw, self.data.d2jw
		Required by:  self.data.d2ri


		Formulae (a hessian matrix is symmetric)
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


				       21   / mu0  \ 2  (gH.gN.h_bar)**2
				d"  =  -- . | ---- |  . ----------------
				       2    \ 4.pi /         <r**8>


			CSA
			~~~
				      (wN.csa)**2
				c  =  -----------
				           3

				       2.wN**2.csa
				c'  =  -----------
				            3

				       2.wN**2
				c"  =  -------
				          3


			R1()
			~~~~
				J_R1_d  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

				                 dJ(wH-wN)         dJ(wN)         dJ(wH+wN)
				J_R1_d_prime  =  ---------  +  3 . ------  +  6 . ---------
				                    dJj             dJj              dJj

				                  d2J(wH-wN)         d2J(wN)         d2J(wH+wN)
				J_R1_d_2prime  =  ----------  +  3 . -------  +  6 . ----------
				                   dJj.dJk           dJj.dJk          dJj.dJk


				J_R1_c  =  J(wN)

				                 dJ(wN)
				J_R1_c_prime  =  ------
				                  dJj

				                  d2J(wN)
				J_R1_c_2prime  =  -------
				                  dJj.dJk


			R2()
			~~~~
				J_R2_d  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

				                     dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN)
				J_R2_d_prime  =  4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . ---------
				                      dJj         dJj             dJj            dJj             dJj

				                       d2J(0)     d2J(wH-wN)         d2J(wN)         d2J(wH)         d2J(wH+wN)
				J_R2_d_2prime  =  4 . -------  +  ----------  +  3 . -------  +  6 . -------  +  6 . ----------
				                      dJj.dJk      dJj.dJk           dJj.dJk         dJj.dJk          dJj.dJk


				J_R2_c  =  4J(0) + 3J(wN)

				                     dJ(0)         dJ(wN)
				J_R2_c_prime  =  4 . -----  +  3 . ------
				                      dJj           dJj

				                       d2J(0)         d2J(wN)
				J_R2_c_2prime  =  4 . -------  +  3 . -------
				                      dJj.dJk         dJj.dJk


			sigma_noe()
			~~~~~~~~~~~
				J_sigma_noe  =  6J(wH+wN) - J(wH-wN)

				                          dJ(wH+wN)     dJ(wH-wN)
				J_sigma_noe_prime  =  6 . ---------  -  ---------
				                             dJj           dJj

				                           d2J(wH+wN)     d2J(wH-wN)
				J_sigma_noe_2prime  =  6 . ----------  -  ----------
				                            dJj.dJk        dJj.dJk


		Spectral density parameter - Spectral density parameter
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2R1()
			-------  =  d . J_R1_d_2prime  +  c . J_R1_c_2prime
			dJj.dJk


			 d2R2()     d                     c
			-------  =  - . J_R2_d_2prime  +  - . J_R2_c_2prime
			dJj.dJk     2                     6


			d2sigma_noe()      
			-------------  =  d . J_sigma_noe_2prime
			   dJj.dJk     


		Spectral density parameter - Chemical exchange
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2R1()               d2R2()              d2sigma_noe()
			--------  =  0   ,   --------  =  0   ,   -------------  =  0
			dJj.dRex             dJj.dRex               dJj.dRex


		Spectral density parameter - CSA
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2R1()
			--------  =  c'. J_R1_c_prime
			dJj.dcsa


			 d2R2()      c'
			--------  =  - . J_R2_c_prime
			dJj.dcsa     6


			d2sigma_noe()
			-------------  =  0
			  dJj.dcsa


		Spectral density parameter - Bond length
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			d2R1()
			------  =  d'. J_R1_d_prime
			dJj.dr


			d2R2()     d'
			------  =  - . J_R2_d_prime
			dJj.dr     2


			d2sigma_noe()
			-------------  =  d' . J_sigma_noe_prime
			   dJj.dr


		Chemical exchange - Chemical exchange
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2R1()              d2R2()             d2sigma_noe()
			-------  =  0   ,   -------  =  0   ,   -------------  =  0
			dRex**2             dRex**2                dRex**2


		Chemical exchange - CSA
		~~~~~~~~~~~~~~~~~~~~~~~

			  d2R1()                d2R2()              d2sigma_noe()
			---------  =  0   ,   ---------  =  0   ,   -------------  =  0
			dRex.dcsa             dRex.dcsa               dRex.dcsa


		Chemical exchange - Bond length
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2R1()              d2R2()             d2sigma_noe()
			-------  =  0   ,   -------  =  0   ,   -------------  =  0
			dRex.dr             dRex.dr                dRex.dr


		CSA - CSA
		~~~~~~~~~

			 d2R1()
			-------  =  c" . J_R1_c
			dcsa**2


			 d2R2()     c"
			-------  =  - . J_R2_c
			dcsa**2     6


			d2sigma_noe()
			-------------  =  0
			   dcsa**2


		CSA - Bond length
		~~~~~~~~~~~~~~~~~

			 d2R1()              d2R2()             d2sigma_noe()
			-------  =  0   ,   -------  =  0   ,   -------------  =  0
			dcsa.dr             dcsa.dr                dcsa.dr


		Bond length - Bond length
		~~~~~~~~~~~~~~~~~~~~~~~~~

			d2R1()
			------  =  d" . J_R1_d
			dr**2


			d2R2()     d"
			------  =  - . J_R2_d
			dr**2      2


			d2sigma_noe()
			-------------  =  d" . J_sigma_noe
			    dr**2

		"""

		# Calculate the spectral density hessians.
		self.d2Jw()

		# Initialise the components of the transformed relaxation equations.
		self.data.j_dip_comps_2prime = zeros((len(self.data.params), len(self.data.params), self.relax.data.num_ri), Float64)
		self.data.j_csa_comps_2prime = zeros((len(self.data.params), len(self.data.params), self.relax.data.num_ri), Float64)
		if match('m6', self.data.model):
			self.data.dip_comps_2prime = zeros((len(self.data.params), len(self.data.params), self.relax.data.num_ri), Float64)
			self.data.csa_comps_2prime = zeros((len(self.data.params), len(self.data.params), self.relax.data.num_ri), Float64)

		# Loop over the relaxation values.
		for i in range(self.relax.data.num_ri):
			frq_num = self.relax.data.remap_table[i]

			# R1 components.
			if self.relax.data.data_types[i]  == 'R1':
				self.data.j_dip_comps_2prime[:, :, i] = self.data.d2jw[frq_num, 2] + 3.0*self.data.d2jw[frq_num, 1] + 6.0*self.data.d2jw[frq_num, 4]
				self.data.j_csa_comps_2prime[:, :, i] = self.data.d2jw[frq_num, 1]
				if match('m6', self.data.model):
					self.data.dip_comps_2prime[:, :, i] = self.relax.data.dipole_prime
					self.data.csa_comps_2prime[:, :, i] = self.relax.data.csa_prime[frq_num]

			# R2 components.
			elif self.relax.data.data_types[i] == 'R2':
				self.data.j_dip_comps_2prime[:, :, i] = 4.0*self.data.d2jw[frq_num, 0] + self.data.d2jw[frq_num, 2] + 3.0*self.data.d2jw[frq_num, 1] + 6.0*self.data.d2jw[frq_num, 3] + 6.0*self.data.d2jw[frq_num, 4]
				self.data.j_csa_comps_2prime[:, :, i] = 4.0*self.data.d2jw[frq_num, 0] + 3.0*self.data.d2jw[frq_num, 1]
				if match('m6', self.data.model):
					self.data.dip_comps_2prime[:, :, i] = self.relax.data.dipole_2prime / 2.0
					self.data.csa_comps_2prime[:, :, i] = self.relax.data.csa_2prime[frq_num] / 6.0

			# sigma_noe components.
			elif self.relax.data.data_types[i] == 'NOE':
				self.data.j_dip_comps_2prime[:, :, i] = 6.0*self.data.d2jw[frq_num, 4] - self.data.d2jw[frq_num, 2]
				if match('m6', self.data.model):
					self.data.dip_comps_2prime[:, :, i] = self.relax.data.dipole_2prime

		# Initialise the transformed relaxation hessians.
		self.data.d2ri_prime = zeros((len(self.data.params), len(self.data.params), self.relax.data.num_ri), Float64)

		# Calculate the transformed relaxation hessians.
		for param1 in range(len(self.data.ri_param_types)):
			for param2 in range(param1 + 1):
				# Spectral density parameter - Spectral density parameter.
				if self.data.ri_param_types[param1] == 'Jj' and self.data.ri_param_types[param2] == 'Jj':
					self.data.d2ri_prime[param1, param2] = self.data.dip_comps * self.data.j_dip_comps_2prime[param1, param2] + self.data.csa_comps * self.data.j_csa_comps_2prime[param1, param2]

				# Spectral density parameter - CSA.
				elif (self.data.ri_param_types[param1] == 'Jj' and self.data.ri_param_types[param2] == 'CSA') \
					or (self.data.ri_param_types[param1] == 'CSA' and self.data.ri_param_types[param2] == 'Jj'):

					self.data.d2ri_prime[param1, param2] = self.data.csa_comps_prime * self.data.j_csa_comps_prime

				# Spectral density parameter - Bond length.
				elif (self.data.ri_param_types[param1] == 'Jj' and self.data.ri_param_types[param2] == 'r') \
					or (self.data.ri_param_types[param1] == 'r' and self.data.ri_param_types[param2] == 'Jj'):

					self.data.d2ri_prime[param1, param2] = self.data.dip_comps_prime * self.data.j_dip_comps_prime

				# CSA - CSA.
				elif self.data.ri_param_types[param1] == 'CSA' and self.data.ri_param_types[param2] == 'CSA':
					self.data.d2ri_prime[param1, param2] = self.data.csa_comps_2prime * self.data.j_csa_comps

				# Bond length - Bond length.
				elif self.data.ri_param_types[param1] == 'r' and self.data.ri_param_types[param2] == 'r':
					self.data.d2ri_prime[param1, param2] = self.data.csa_comps_2prime * self.data.j_csa_comps

				# Others.
				else:
					continue

				# Make the hessian symmetric.
				if param1 != param2:
					self.data.d2ri_prime[param2, param1] = self.data.d2ri_prime[param1, param2]
