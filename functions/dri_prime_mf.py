import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class dRi:
	def __init__(self, mf):
		"Function for the calculation of the relaxation gradient matrix."

		self.mf = mf


	def calc(self, mf_params, diff_type, diff_params, mf_model):
		"""Function for the calculation of the relaxation gradient matrix.

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


		The relaxation gradient
		~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.dri
		Dimension:  2D, (relaxation data, model-free parameters)
		Type:  Numeric matrix, Float64
		Dependencies:  self.ri, self.jw, self.djw
		Required by:  self.dchi2, self.d2chi2, self.d2ri
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

		self.mf_params = mf_params
		self.diff_type = diff_type
		self.diff_params = diff_params
		self.mf_model = mf_model

		# Debugging code.
		#print "<<< dRi >>>"

		# Calculate the spectral density derivatives.
		self.mf.mf_functions.dJw.calc(self.mf_params, self.diff_type, self.diff_params, self.mf_model)

		# Initialise the relaxation gradient matrix.
		self.dri = zeros((self.mf.data.num_ri, len(self.mf_params)), Float64)

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

			for param in range(len(self.param_types)):
				# Model-free parameter derivatives.
				if match('R1', self.mf.data.data_types[i]) and match('mf', self.param_types[param]):
					self.dri[i, param] = self.calc_dr1_dmf(param)
				elif match('R2', self.mf.data.data_types[i]) and match('mf', self.param_types[param]):
					self.dri[i, param] = self.calc_dr2_dmf(param)
				elif match('NOE', self.mf.data.data_types[i]) and match('mf', self.param_types[param]):
					self.dri[i, param] = self.calc_dnoe_dmf(i, param)

				# Chemical exchange derivatives (matrix already filled with zeros).
				elif match('R2', self.mf.data.data_types[i]) and match('rex', self.param_types[param]):
					self.dri[i, param] = (1e-8 * self.mf.data.frq[self.frq_num])**2

		# Store the relaxation gradient matrix.
		self.mf.data.mf_data.dri = copy.deepcopy(self.dri)


	def calc_dr1_dmf(self, param):
		"Calculate the derivative of the R1 value."

		dr1_dipole = self.mf.data.dipole_const * (self.mf.data.mf_data.djw[self.frq_num, 2, param] + 3.0*self.mf.data.mf_data.djw[self.frq_num, 1, param] + 6.0*self.mf.data.mf_data.djw[self.frq_num, 4, param])
		dr1_csa = self.mf.data.csa_const[self.frq_num] * self.mf.data.mf_data.djw[self.frq_num, 1, param]
		dr1 = dr1_dipole + dr1_csa
		return dr1


	def calc_dr2_dmf(self, param):
		"Calculate the derivative of the R2 value."

		dr2_dipole = (self.mf.data.dipole_const/2.0) * (4.0*self.mf.data.mf_data.djw[self.frq_num, 0, param] + self.mf.data.mf_data.djw[self.frq_num, 2, param] + 3.0*self.mf.data.mf_data.djw[self.frq_num, 1, param] + 6.0*self.mf.data.mf_data.djw[self.frq_num, 3, param] + 6.0*self.mf.data.mf_data.djw[self.frq_num, 4, param])
		dr2_csa = (self.mf.data.csa_const[self.frq_num]/6.0) * (4.0*self.mf.data.mf_data.djw[self.frq_num, 0, param] + 3.0*self.mf.data.mf_data.djw[self.frq_num, 1, param])
		dr2 = dr2_dipole + dr2_csa
		return dr2


	def calc_dnoe_dmf(self, i, param):
		"Calculate the derivative of the NOE value."

		if self.mf.data.noe_r1_table[i] == None:
			dr1 = self.calc_dr1_dmf(param)
			raise NameError, "Incomplete code, need to somehow calculate the r1 value (R1 of this NOE frq is missing in original set)."
		else:
			r1 = self.mf.data.mf_data.ri[self.mf.data.noe_r1_table[i]]
			dr1 = self.dri[self.mf.data.noe_r1_table[i], param]

		if r1 == 0.0:
			print "R1 is zero, this should not occur."
			dnoe = 1e99
		elif dr1 == 0.0:
			dnoe = (self.mf.data.dipole_const / r1) * (self.mf.data.gh/self.mf.data.gx) * (6.0*self.mf.data.mf_data.djw[self.frq_num, 4, param] - self.mf.data.mf_data.djw[self.frq_num, 2, param])
		else:
			dnoe = - (self.mf.data.dipole_const / r1**2) * (self.mf.data.gh/self.mf.data.gx) * ((6.0*self.mf.data.mf_data.jw[self.frq_num, 4] - self.mf.data.mf_data.jw[self.frq_num, 2]) * dr1  -  (6.0*self.mf.data.mf_data.djw[self.frq_num, 4, param] - self.mf.data.mf_data.djw[self.frq_num, 2, param]) * r1)
		return dnoe
