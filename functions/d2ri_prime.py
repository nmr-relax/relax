import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class d2Ri_prime:
	def __init__(self):
		"Function for the calculation of the relaxation hessian matrix."


	def d2Ri_prime(self):
		"""Function for the calculation of the relaxation hessian matrix.

		The relaxation hessian
		~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.d2ri
		Dimension:  3D, (relaxation data, model-free parameters, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  self.data.ri, self.data.dri, self.data.jw, self.data.djw, self.data.d2jw
		Required by:  self.data.d2chi2
		Stored:  Yes


		Formulae (the hessian matrix is symmetric)
		~~~~~~~~


		Model-free parameter - Model-free parameter
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			  d2R1()          / d2J(wH-wN)          d2J(wN)          d2J(wH+wN) \        /  d2J(wN)  \ 
			---------  =  d . | ----------  +  3 . ---------  +  6 . ---------- |  + c . | --------- |
			dmfj.dmfk         \ dmfj.dmfk          dmfj.dmfk         dmfj.dmfk  /        \ dmfj.dmfk /


			  d2R2()      d   /       d2J(0)      d2J(wH-wN)          d2J(wN)           d2J(wH)          d2J(wH+wN) \     c   /       d2J(0)           d2J(wN)  \ 
			---------  =  - . | 4 . ---------  +  ----------  +  3 . ---------  +  6 . ---------  +  6 . ---------- |  +  - . | 4 . ---------  +  3 . --------- |
			dmfj.dmfk     2   \     dmfj.dmfk     dmfj.dmfk          dmfj.dmfk         dmfj.dmfk         dmfj.dmfk  /     6   \     dmfj.dmfk         dmfj.dmfk /


			 d2NOE()         d      gH   /                          /     dR1()   dR1()              d2R1()  \ 
			---------  =  ------- . -- . | [6J(wH+wN) - J(wH-wN)] . | 2 . ----- . -----  -  R1() . --------- |
			dmfj.dmfk     R1()**3   gN   \                          \     dmfj    dmfk             dmfj.dmfk /

			                                 /     dJ(wH+wN)     dJ(wH-wN) \          dR1()
			                               - | 6 . ---------  -  --------- | . R1() . -----
			                                 \       dmfj          dmfj    /          dmfk

			                                 /     dJ(wH+wN)     dJ(wH-wN) \          dR1()
			                               - | 6 . ---------  -  --------- | . R1() . -----
			                                 \       dmfk          dmfk    /          dmfj

			                                 /     d2J(wH+wN)     d2J(wH-wN) \           \ 
			                               + | 6 . ----------  -  ---------- | . R1()**2 |
			                                 \     dmfj.dmfk      dmfj.dmfk  /           /


		Model-free parameter - Chemical exchange
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2R1()               d2R2()               d2NOE()
			--------  =  0   ,   --------  =  0   ,   --------  =  0
			dmf.dRex             dmf.dRex             dmf.dRex


		Model-free parameter - CSA
		~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2R1()          / dJ(wN) \ 
			--------  =  c'. | ------ |
			dmf.dcsa         \  dmf   /


			 d2R2()      c'  /     dJ(0)         dJ(wN) \ 
			--------  =  - . | 4 . -----  +  3 . ------ |
			dmf.dcsa     6   \      dmf           dmf   /


			 d2NOE()        d      gH   /                          /     dR1()   dR1()             d2R1()  \ 
			--------  =  ------- . -- . | [6J(wH+wN) - J(wH-wN)] . | 2 . ----- . -----  -  R1() . -------- |
			dmf.dcsa     R1()**3   gN   \                          \      dmf    dcsa             dmf.dcsa /

			                                 /     dJ(wH+wN)     dJ(wH-wN) \          dR1() \ 
			                               - | 6 . ---------  -  --------- | . R1() . ----- |
			                                 \        dmf           dmf    /          dcsa  /


		Model-free parameter - Bond length
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			d2R1()         / dJ(wH-wN)         dJ(wN)         dJ(wH+wN) \ 
			------  =  d'. | ---------  +  3 . ------  +  6 . --------- |
			dmf.dr         \    dmf             dmf              dmf    /


			d2R2()     d'  /     dJ(0)     dJ(wH-wN)         dJ(wN)         dJ(wH)         dJ(wH+wN) \ 
			------  =  - . | 4 . -----  +  ---------  +  3 . ------  +  6 . ------  +  6 . --------- |
			dmf.dr     2   \      dmf         dmf             dmf            dmf             dmf     /


			d2NOE()        1      gH   /                          /       dR1()     2.d    dR1()   dR1()         d2R1() \ 
			-------  =  ------- . -- . | [6J(wH+wN) - J(wH-wN)] . | - d'. -----  +  ---- . ----- . -----  -  d . ------ |
			dmf.dr      R1()**2   gN   \                          \        dmf      R1()    dmf     dr           dmf.dr /

			                                 /     dJ(wH+wN)     dJ(wH-wN) \ /                    dR1() \ \ 
			                               - | 6 . ---------  -  --------- |.| - d'. R1()  +  d . ----- | |
			                                 \        dmf           dmf    / \                     dr   / /


		Chemical exchange - Chemical exchange
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2R1()              d2R2()             d2NOE()
			-------  =  0   ,   -------  =  0   ,   -------  =  0
			dRex**2             dRex**2             dRex**2


		Chemical exchange - CSA
		~~~~~~~~~~~~~~~~~~~~~~~

			  d2R1()                d2R2()               d2NOE()
			---------  =  0   ,   ---------  =  0   ,   ---------  =  0
			dRex.dcsa             dRex.dcsa             dRex.dcsa


		Chemical exchange - Bond length
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2R1()              d2R2()             d2NOE()
			-------  =  0   ,   -------  =  0   ,   -------  =  0
			dRex.dr             dRex.dr             dRex.dr


		CSA - CSA
		~~~~~~~~~

			 d2R1()
			-------  =  c" . J(wN)
			dcsa**2


			 d2R2()     c"
			-------  =  - . [4J(0) + 3J(wN)]
			dcsa**2     6


			d2NOE()        d      gH                            /     dR1()   dR1()             d2R1() \ 
			-------  =  ------- . -- . [6J(wH+wN) - J(wH-wN)] . | 2 . ----- . -----  -  R1() . ------- |
			dcsa**2     R1()**3   gN                            \     dcsa    dcsa             dcsa**2 /


		CSA - Bond length
		~~~~~~~~~~~~~~~~~

			 d2R1()
			-------  =  0
			dcsa.dr


			 d2R2()
			-------  =  0
			dcsa.dr


			d2NOE()       gH      1                               /            dR1()         /     dR1()   dR1()             d2R1() \ \ 
			-------  =  - -- . ------- . [6J(wH+wN) - J(wH-wN)] . | d'. R1() . -----  -  d . | 2 . ----- . -----  -  R1() . ------- | |
			dcsa.dr       gN   R1()**3                            \            dcsa          \     dcsa     dr              dcsa.dr / /


		Bond length - Bond length
		~~~~~~~~~~~~~~~~~~~~~~~~~

			d2R1()
			------  =  d" . [J(wH-wN) + 3J(wN) + 6J(wH+wN)]
			dr**2


			d2R2()     d"
			------  =  - . [4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)]
			dr**2      2


			d2NOE()     gH      1                               /     /     dR1()   dR1()            d2R1() \                    dR1()                 \ 
			-------  =  -- . ------- . [6J(wH+wN) - J(wH-wN)] . | d . | 2 . ----- . -----  -  R1() . ------ |  -  2 . d'. R1() . -----  +  d". R1()**2 |
			 dr**2      gN   R1()**3                            \     \      dr      dr              dr**2  /                     dr                   /


		Constants
		~~~~~~~~~
			      1   / mu0  \ 2  (gH.gN.h_bar)**2
			d  =  - . | ---- |  . ----------------
			      4   \ 4.pi /         <r**6>


			         3   / mu0  \ 2  (gH.gN.h_bar)**2
			d'  =  - - . | ---- |  . ----------------
			         2   \ 4.pi /         <r**7>


			       21   / mu0  \ 2  (gH.gN.h_bar)**2
			d"  =  -- . | ---- |  . ----------------
			       2    \ 4.pi /         <r**8>


			      (wN.csa)**2
			c  =  -----------
			           3


			       2.wN**2.csa
			c'  =  -----------
			            3


			       2.wN**2
			c"  =  -------
			          3



		It is assumed that this function is being called by the dchi2 function, and that the relaxation array and spectral density matrix
		have been previously calculated!
		"""

		# Debugging code.
		#print "<<< dRi >>>"

		# Calculate the spectral density derivatives.
		self.d2Jw()

		# Initialise the relaxation gradient matrix.
		self.data.d2ri = zeros((self.mf.data.num_ri, len(self.data.mf_params), len(self.data.mf_params)), Float64)

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			frq_num = self.mf.data.remap_table[i]

			for param1 in range(len(self.data.ri_param_types)):
				for param2 in range(param1 + 1):
					# Model-free parameter - Model-free parameter.
					if self.mf.data.data_types[i] == 'R1' and self.data.ri_param_types[param1] == 'mf' and self.data.ri_param_types[param2] == 'mf':
						self.data.d2ri[i, param1, param2] = self.calc_d2r1_dmf2(param1, param2, frq_num)
						if param1 != param2:
							self.data.d2ri[i, param2, param1] = self.data.d2ri[i, param1, param2]
					elif self.mf.data.data_types[i] == 'R2' and self.data.ri_param_types[param1] == 'mf' and self.data.ri_param_types[param2] == 'mf':
						self.data.d2ri[i, param1, param2] = self.calc_d2r2_dmf2(param1, param2, frq_num)
						if param1 != param2:
							self.data.d2ri[i, param2, param1] = self.data.d2ri[i, param1, param2]
					elif self.mf.data.data_types[i] == 'NOE' and self.data.ri_param_types[param1] == 'mf' and self.data.ri_param_types[param2] == 'mf':
						self.data.d2ri[i, param1, param2] = self.calc_d2noe_dmf2(i, param1, param2, frq_num)
						if param1 != param2:
							self.data.d2ri[i, param2, param1] = self.data.d2ri[i, param1, param2]


	def calc_d2r1_dmf2(self, param1, param2, frq_num):
		"Calculate the mf/mf partial derivative of the R1 relaxation equation."

		a = self.mf.data.dipole_const * (self.data.d2jw[frq_num, 2, param1, param2] + 3.0*self.data.d2jw[frq_num, 1, param1, param2] + 6.0*self.data.d2jw[frq_num, 4, param1, param2])
		b = self.mf.data.csa_const[frq_num] * self.data.d2jw[frq_num, 1, param1, param2]

		temp = a + b
		return temp


	def calc_d2r2_dmf2(self, param1, param2, frq_num):
		"Calculate the mf/mf partial derivative of the R2 relaxation equation."

		a = (self.mf.data.dipole_const/2.0) * (4.0*self.data.d2jw[frq_num, 0, param1, param2] + self.data.d2jw[frq_num, 2, param1, param2] + 3.0*self.data.d2jw[frq_num, 1, param1, param2] + 6.0*self.data.d2jw[frq_num, 3, param1, param2] + 6.0*self.data.d2jw[frq_num, 4, param1, param2])
		b = (self.mf.data.csa_const[frq_num]/6.0) * (4.0*self.data.d2jw[frq_num, 0, param1, param2] + 3.0*self.data.d2jw[frq_num, 1, param1, param2])

		temp = a + b
		return temp


	def calc_d2noe_dmf2(self, i, param1, param2, frq_num):
		"Calculate the derivative of the NOE value."

		if self.mf.data.noe_r1_table[i] == None:
			d2r1_dmf2 = self.calc_d2r1_dmf2(param1, param2, frq_num)
			raise NameError, "Incomplete code, need to somehow calculate the r1 value."
		else:
			r1 = self.data.ri[self.mf.data.noe_r1_table[i]]
			dr1_dmfj = self.data.dri[self.mf.data.noe_r1_table[i], param1]
			dr1_dmfk = self.data.dri[self.mf.data.noe_r1_table[i], param2]
			d2r1_dmf2 = self.data.d2ri[self.mf.data.noe_r1_table[i], param1, param2]

		if r1 == 0.0:
			print "R1 is zero, this should not occur."
			temp = 1e99
		else:
			a = (self.mf.data.dipole_const / r1**3) * (self.mf.data.gh / self.mf.data.gx)
			b = (6.0*self.data.jw[frq_num, 4] - self.data.jw[frq_num, 2]) * ( 2.0 * dr1_dmfj * dr1_dmfk - r1 * d2r1_dmf2)
			c = (6.0*self.data.djw[frq_num, 4, param1] - self.data.djw[frq_num, 2, param1]) * r1 * dr1_dmfk
			d = (6.0*self.data.djw[frq_num, 4, param2] - self.data.djw[frq_num, 2, param2]) * r1 * dr1_dmfj
			e = (6.0*self.data.d2jw[frq_num, 4, param1, param2] - self.data.d2jw[frq_num, 2, param1, param2]) * r1**2
			temp = a * (b - c - d + e)

		return temp
