import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class d2Ri:
	def __init__(self, mf):
		"Function for the calculation of the relaxation hessian matrix."

		self.mf = mf


	def calc(self, mf_params, diff_type, diff_params, mf_model):
		"""Function for the calculation of the relaxation hessian matrix.

		Function arguments
		~~~~~~~~~~~~~~~~~~

		1:  mf_params - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}
		2:  diff_type - string.  The diffusion tensor, ie 'iso', 'axial', 'aniso'
		3:  diff_params - array.  An array with the diffusion parameters
		4:  mf_model - string.  The model-free model


		The relaxation hessian
		~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.d2ri
		Dimension:  3D, (relaxation data, model-free parameters, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  self.ri, self.dri, self.jw, self.djw, self.d2jw
		Required by:  self.d2chi2
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

		self.mf_params = mf_params
		self.diff_type = diff_type
		self.diff_params = diff_params
		self.mf_model = mf_model

		# Debugging code.
		#print "<<< dRi >>>"

		# Calculate the spectral density derivatives.
		self.mf.mf_functions.d2Jw.calc(self.mf_params, self.diff_type, self.diff_params, self.mf_model)

		# Initialise the relaxation gradient matrix.
		self.d2ri = zeros((self.mf.data.num_ri, len(self.mf_params), len(self.mf_params)), Float64)

		# Initialise an array with the model-free parameter labels.
		if match('m1', self.mf_model):
			self.param_types = ['mf']
		elif match('m2', self.mf_model):
			self.param_types = ['mf', 'mf']
		elif match('m3', self.mf_model):
			self.param_types = ['mf', 'rex']
		elif match('m4', self.mf_model):
			self.param_types = ['mf', 'mf', 'rex']
		elif match('m5', self.mf_model):
			self.param_types = ['mf', 'mf', 'mf']
		else:
			raise NameError, "Should not be here."

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			self.frq_num = self.mf.data.remap_table[i]

			for param1 in range(len(self.param_types)):
				for param2 in range(param1 + 1):
					# Model-free parameter - Model-free parameter.
					if self.mf.data.data_types[i] == 'R1' and self.param_types[param1] == 'mf' and self.param_types[param2] == 'mf':
						self.d2ri[i, param1, param2] = self.calc_d2r1_dmf2(param1, param2)
						if param1 != param2:
							self.d2ri[i, param2, param1] = self.d2ri[i, param1, param2]
					elif self.mf.data.data_types[i] == 'R2' and self.param_types[param1] == 'mf' and self.param_types[param2] == 'mf':
						self.d2ri[i, param1, param2] = self.calc_d2r2_dmf2(param1, param2)
						if param1 != param2:
							self.d2ri[i, param2, param1] = self.d2ri[i, param1, param2]
					elif self.mf.data.data_types[i] == 'NOE' and self.param_types[param1] == 'mf' and self.param_types[param2] == 'mf':
						self.d2ri[i, param1, param2] = self.calc_d2noe_dmf2(i, param1, param2)
						if param1 != param2:
							self.d2ri[i, param2, param1] = self.d2ri[i, param1, param2]

		# Store the relaxation gradient matrix.
		self.mf.data.mf_data.d2ri = copy.deepcopy(self.d2ri)


	def calc_d2r1_dmf2(self, param1, param2):
		"Calculate the mf/mf partial derivative of the R1 relaxation equation."

		a = self.mf.data.dipole_const * (self.mf.data.mf_data.d2jw[self.frq_num, 2, param1, param2] + 3.0*self.mf.data.mf_data.d2jw[self.frq_num, 1, param1, param2] + 6.0*self.mf.data.mf_data.d2jw[self.frq_num, 4, param1, param2])
		b = self.mf.data.csa_const[self.frq_num] * self.mf.data.mf_data.d2jw[self.frq_num, 1, param1, param2]

		temp = a + b
		return temp


	def calc_d2r2_dmf2(self, param1, param2):
		"Calculate the mf/mf partial derivative of the R2 relaxation equation."

		a = (self.mf.data.dipole_const/2.0) * (4.0*self.mf.data.mf_data.d2jw[self.frq_num, 0, param1, param2] + self.mf.data.mf_data.d2jw[self.frq_num, 2, param1, param2] + 3.0*self.mf.data.mf_data.d2jw[self.frq_num, 1, param1, param2] + 6.0*self.mf.data.mf_data.d2jw[self.frq_num, 3, param1, param2] + 6.0*self.mf.data.mf_data.d2jw[self.frq_num, 4, param1, param2])
		b = (self.mf.data.csa_const[self.frq_num]/6.0) * (4.0*self.mf.data.mf_data.d2jw[self.frq_num, 0, param1, param2] + 3.0*self.mf.data.mf_data.d2jw[self.frq_num, 1, param1, param2])

		temp = a + b
		return temp


	def calc_d2noe_dmf2(self, i, param1, param2):
		"Calculate the derivative of the NOE value."

		if self.mf.data.noe_r1_table[i] == None:
			d2r1_dmf2 = self.calc_d2r1_dmf2(param1, param2)
			raise NameError, "Incomplete code, need to somehow calculate the r1 value."
		else:
			r1 = self.mf.data.mf_data.ri[self.mf.data.noe_r1_table[i]]
			dr1_dmfj = self.mf.data.mf_data.dri[self.mf.data.noe_r1_table[i], param1]
			dr1_dmfk = self.mf.data.mf_data.dri[self.mf.data.noe_r1_table[i], param2]
			d2r1_dmf2 = self.d2ri[self.mf.data.noe_r1_table[i], param1, param2]

		if r1 == 0.0:
			print "R1 is zero, this should not occur."
			temp = 1e99
		else:
			a = (self.mf.data.dipole_const / r1**3) * (self.mf.data.gh / self.mf.data.gx)
			b = (6.0*self.mf.data.mf_data.jw[self.frq_num, 4] - self.mf.data.mf_data.jw[self.frq_num, 2]) * ( 2.0 * dr1_dmfj * dr1_dmfk - r1 * d2r1_dmf2)
			c = (6.0*self.mf.data.mf_data.djw[self.frq_num, 4, param1] - self.mf.data.mf_data.djw[self.frq_num, 2, param1]) * r1 * dr1_dmfk
			d = (6.0*self.mf.data.mf_data.djw[self.frq_num, 4, param2] - self.mf.data.mf_data.djw[self.frq_num, 2, param2]) * r1 * dr1_dmfj
			e = (6.0*self.mf.data.mf_data.d2jw[self.frq_num, 4, param1, param2] - self.mf.data.mf_data.d2jw[self.frq_num, 2, param1, param2]) * r1**2
			temp = a * (b - c - d + e)

		return temp
