import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class dRi_prime:
	def __init__(self):
		"Function for the calculation of the transformed relaxation gradient."


	def dRi_prime(self):
		"""Function for the calculation of the transformed relaxation gradient.

		The transformed relaxation gradient
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.dri_prime
		Dimension:  2D, (transformed relaxation data, model-free parameters)
		Type:  Numeric matrix, Float64
		Dependencies:  self.data.jw, self.data.djw
		Required by:  self.data.dri, self.data.d2ri
		Stored:  Yes


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


		Model-free parameter
		~~~~~~~~~~~~~~~~~~~~

			dR1()
			-----  =  d . J_R1_d_prime  +  c . J_R1_c_prime
			 dmf


			dR2()     d                    c
			-----  =  - . J_R2_d_prime  +  - . J_R2_c_prime
			 dmf      2                    6


			dsigma_noe()
			------------  = d . J_sigma_noe_prime
			    dmf


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

		# Debugging code.
		#print "<<< dRi >>>"

		# Calculate the spectral density derivatives.
		self.dJw()

		# Initialise the relaxation gradient matrix.
		self.data.dri = zeros((self.mf.data.num_ri, len(self.data.mf_params)), Float64)

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			frq_num = self.mf.data.remap_table[i]

			for param in range(len(self.data.ri_param_types)):
				# Model-free parameter derivatives.
				if self.mf.data.data_types[i]  == 'R1' and self.data.ri_param_types[param] == 'mf':
					self.data.dri[i, param] = self.calc_dr1_dmf(param, frq_num)
				elif self.mf.data.data_types[i] == 'R2' and self.data.ri_param_types[param] == 'mf':
					self.data.dri[i, param] = self.calc_dr2_dmf(param, frq_num)
				elif self.mf.data.data_types[i] == 'NOE' and self.data.ri_param_types[param] == 'mf':
					self.data.dri[i, param] = self.calc_dnoe_dmf(i, param, frq_num)

				# Chemical exchange derivatives (matrix already filled with zeros).
				elif self.mf.data.data_types[i] == 'R2' and self.data.ri_param_types[param] == 'rex':
					self.data.dri[i, param] = (1e-8 * self.mf.data.frq[frq_num])**2


	def calc_dr1_dmf(self, param, frq_num):
		"Calculate the derivative of the R1 value."

		dr1_dipole = self.mf.data.dipole_const * (self.data.djw[frq_num, 2, param] + 3.0*self.data.djw[frq_num, 1, param] + 6.0*self.data.djw[frq_num, 4, param])
		dr1_csa = self.mf.data.csa_const[frq_num] * self.data.djw[frq_num, 1, param]
		dr1 = dr1_dipole + dr1_csa
		return dr1


	def calc_dr2_dmf(self, param, frq_num):
		"Calculate the derivative of the R2 value."

		dr2_dipole = (self.mf.data.dipole_const/2.0) * (4.0*self.data.djw[frq_num, 0, param] + self.data.djw[frq_num, 2, param] + 3.0*self.data.djw[frq_num, 1, param] + 6.0*self.data.djw[frq_num, 3, param] + 6.0*self.data.djw[frq_num, 4, param])
		dr2_csa = (self.mf.data.csa_const[frq_num]/6.0) * (4.0*self.data.djw[frq_num, 0, param] + 3.0*self.data.djw[frq_num, 1, param])
		dr2 = dr2_dipole + dr2_csa
		return dr2


	def calc_dnoe_dmf(self, i, param, frq_num):
		"Calculate the derivative of the NOE value."

		if self.mf.data.noe_r1_table[i] == None:
			raise NameError, "Incomplete code, need to somehow calculate the r1 value (R1 of this NOE frq is missing in original set)."

		r1 = self.data.ri[self.mf.data.noe_r1_table[i]]
		dr1 = self.data.dri[self.mf.data.noe_r1_table[i], param]

		if r1 == 0.0:
			print "R1 is zero, this should not occur."
			dnoe = 1e99
		elif dr1 == 0.0:
			dnoe = (self.mf.data.dipole_const / r1) * (self.mf.data.gh/self.mf.data.gx) * (6.0*self.data.djw[frq_num, 4, param] - self.data.djw[frq_num, 2, param])
		else:
			dnoe = - (self.mf.data.dipole_const / r1**2) * (self.mf.data.gh/self.mf.data.gx) * ((6.0*self.data.jw[frq_num, 4] - self.data.jw[frq_num, 2]) * dr1  -  (6.0*self.data.djw[frq_num, 4, param] - self.data.djw[frq_num, 2, param]) * r1)
		return dnoe
