import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class dRi_prime:
	def __init__(self):
		"Function for the calculation of the relaxation gradient matrix."


	def dRi_prime(self):
		"""Function for the calculation of the relaxation gradient matrix.

		The relaxation gradient
		~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.dri
		Dimension:  2D, (relaxation data, model-free parameters)
		Type:  Numeric matrix, Float64
		Dependencies:  self.data.ri, self.data.jw, self.data.djw
		Required by:  self.data.dchi2, self.data.d2chi2, self.data.d2ri
		Stored:  Yes


		Formulae
		~~~~~~~~

		Model-free parameter
		~~~~~~~~~~~~~~~~~~~~

			dR1()         / dJ(wH-wN)         dJ(wN)         dJ(wH+wN) \        / dJ(wN) \ 
			-----  =  d . | ---------  +  3 . ------  +  6 . --------- |  + c . | ------ |
			 dmf          \    dmf             dmf              dmf    /        \  dmf   /


			dR2()     d   /     dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN) \     c   /     dJ(0)         dJ(wN) \ 
			-----  =  - . | 4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . --------- |  +  - . | 4 . -----  +  3 . ------ |
			 dmf      2   \      dmf         dmf             dmf            dmf             dmf     /     6   \      dmf           dmf   /


			dNOE()         d      gH   /                          dR1()     /     dJ(wH+wN)     dJ(wH-wN) \        \ 
			------  = - ------- . -- . | [6J(wH+wN) - J(wH-wN)] . -----  -  | 6 . ---------  -  --------- | . R1() |
			 dmf        R1()**2   gN   \                           dmf      \        dmf           dmf    /        /


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


			dNOE()
			------  =  0
			 dRex

		CSA
		~~~

			dR1()
			-----  =  c' . J(wN)
			dcsa


			dR2()     c'
			-----  =  - . [4J(0) + 3J(wN)]
			dcsa      6


			dNOE()          d      gH                            dR1()
			------  =  - ------- . -- . [6J(wH+wN) - J(wH-wN)] . -----
			 dcsa         R1()**2   gN                            dcsa


		Bond length
		~~~~~~~~~~~

			dR1()
			-----  =  d' . [J(wH-wN) + 3J(wN) + 6J(wH+wN)]
			 dr


			dR2()     d'
			-----  =  - . [4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)]
			 dr       2


			dNOE()     gH      1      /                   dR1() \ 
			------  =  -- . ------- . | d' . R1()  -  d . ----- | . [6J(wH+wN) - J(wH-wN)]
			  dr       gN   R1()**2   \                    dr   /


		Constants
		~~~~~~~~~
			      1   / mu0    gH.gN.h_bar \ 2
			d  =  - . | ---- . ----------- |
			      4   \ 4.pi     <r**3>    /


			         3   / mu0  \ 2  (gH.gN.h_bar)**2
			d'  =  - - . | ---- |  . ----------------
			         2   \ 4.pi /         <r**7>


			      (wN.csa)**2
			c  =  -----------
			           3


			       2.wN**2.csa
			c'  =  -----------
			            3


		It is assumed that this function is being called by the dchi2 function, and that the relaxation array and spectral density matrix
		have been previously calculated!
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
