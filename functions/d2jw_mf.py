import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class d2Jw:
	def __init__(self, mf):
		"Function for creating the spectral density gradient."

		self.mf = mf


	def calc(self, mf_params, diff_type, diff_params, mf_model):
		"""Function to create spectral density gradient.

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


		The spectral density hessian
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.d2jw
		Dimension:  4D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters, model-free parameters)
		Type:  Numeric 4D matrix, Float64
		Dependencies:  None
		Required by:  self.d2ri
		Stored:  Yes


		Formulae
		~~~~~~~~

		Original:  Model-free parameter - Model-free parameter
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			d2J(w)
			------  =  0
			dS2**2


			 d2J(w)       2     1 - (w.te')**2      /   tm    \ 2
			-------  =  - - . ------------------- . | ------- |
			dS2.dte       5   (1 + (w.te')**2)**2   \ te + tm /


			d2J(w)       4              /   tm    \ 4           1            
			------  =  - - . (1 - S2) . | ------- |  . ------------------- . [w**2.te'(3 - (w.te')**2) + (1 - (w.te')**4)(te + tm).tm**-2]
			dte**2       5              \ te + tm /    (1 + (w.te')**2)**3   


		Original:  Other parameters
		~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2J(w)               d2J(w)              d2J(w)
			--------  =  0   ,   --------  =  0   ,   ------  =  0
			dS2.dRex             dS2.dcsa             dS2.dr


			 d2J(w)              d2J(w)               d2J(w)
			--------  =  0   ,  --------  =  0   ,    ------  =  0
			dte.dRex            dte.dcsa              dte.dr


			 d2J(w)              d2J(w)                d2J(w)
			-------  =  0   ,  ---------  =  0   ,    -------  =  0
			dRex**2            dRex.dcsa              dRex.dr


			 d2J(w)             d2J(w)
			-------  =  0   ,  -------  =  0
			dcsa**2            dcsa.dr


			d2J(w)
			------  =  0
			dr**2


		Extended:  Model-free parameter - Model-free parameter
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2J(w)
			-------  =  0
			dS2f**2


			  d2J(w)      2 /      tm                 ts'      \ 
			---------  =  - | -------------  -  -------------- |
			dS2f.dS2s     5 \ 1 + (w.tm)**2     1 + (w.ts')**2 /


			 d2J(w)        2     1 - (w.tf')**2      /   tm    \ 2
			--------  =  - - . ------------------- . | ------- |
			dS2f.dtf       5   (1 + (w.tf')**2)**2   \ tf + tm /


			 d2J(w)      2                 1 - (w.ts')**2      /   tm    \ 2
			--------  =  - . (1 - S2s) . ------------------- . | ------- |
			dS2f.dts     5               (1 + (w.ts')**2)**2   \ ts + tm /


			 d2J(w)              d2J(w)
			-------  =  0   ,   --------  =  0
			dS2s**2             dS2s.dtf


			 d2J(w)        2.S2f     1 - (w.ts')**2      /   tm    \ 2
			--------  =  - ----- . ------------------- . | ------- |
			dS2s.dts         5     (1 + (w.ts')**2)**2   \ ts + tm /


			 d2J(w)
			-------  =  0
			dtf.dts


			d2J(w)       4               /   tm    \ 4           1            
			------  =  - - . (1 - S2f) . | ------- |  . ------------------- . [w**2.tf'(3 - (w.tf')**2) + (1 - (w.tf')**4)(tf + tm).tm**-2]
			dtf**2       5               \ tf + tm /    (1 + (w.tf')**2)**3   


			d2J(w)       4                /   tm    \ 4           1            
			------  =  - - . (S2f - S2) . | ------- |  . ------------------- . [w**2.ts'(3 - (w.ts')**2) + (1 - (w.ts')**4)(ts + tm).tm**-2]
			dts**2       5                \ ts + tm /    (1 + (w.ts')**2)**3   


		Extended:  Other parameters
		~~~~~~~~~~~~~~~~~~~~~~~~~~~

			  d2J(w)                d2J(w)               d2J(w)
			---------  =  0   ,   ---------  =  0   ,   -------  =  0
			dS2f.dRex             dS2f.dcsa             dS2f.dr


			  d2J(w)                d2J(w)               d2J(w)
			---------  =  0   ,   ---------  =  0   ,   -------  =  0
			dS2s.dRex             dS2s.dcsa             dS2s.dr


			 d2J(w)               d2J(w)              d2J(w)
			--------  =  0   ,   --------  =  0   ,   ------  =  0
			dtf.dRex             dtf.dcsa             dtf.dr


			 d2J(w)               d2J(w)              d2J(w)
			--------  =  0   ,   --------  =  0   ,   ------  =  0
			dts.dRex             dts.dcsa             dts.dr


			 d2J(w)               d2J(w)               d2J(w)
			-------  =  0   ,   ---------  =  0   ,   -------  =  0
			dRex**2             dRex.dcsa             dRex.dr


			 d2J(w)              d2J(w)
			-------  =  0   ,   -------  =  0
			dcsa**2             dcsa.dr


			d2J(w)
			------  =  0
			dr**2



		"""

		self.mf_params = mf_params
		self.diff_type = diff_type
		self.diff_params = diff_params
		self.mf_model = mf_model

		# Calculate frequency independent terms (to increase speed)
		self.initialise_d2jw_values()

		# Initialise the spectral density hessian.
		self.d2jw = zeros((self.mf.data.num_frq, 5, len(self.mf_params), len(self.mf_params)), Float64)

		# Initialise an array with the model-free parameter labels.
		if match('m1', self.mf_model):
			self.param_types = ['S2']
		elif match('m2', self.mf_model):
			self.param_types = ['S2', 'te']
		elif match('m3', self.mf_model):
			self.param_types = ['S2', 'Rex']
		elif match('m4', self.mf_model):
			self.param_types = ['S2', 'te', 'Rex']
		elif match('m5', self.mf_model):
			self.param_types = ['S2f', 'S2s', 'ts']
		else:
			raise NameError, "Should not be here."

		# Isotropic rotational diffusion.
		# (possibly switch the for loops to speed up calculations?)
		if match(self.diff_type, 'iso'):
			# Model 1 and 3 hessians are zero.
			if match('m[24]', self.mf_model):
				for i in range(self.mf.data.num_frq):
					for param1 in range(len(self.param_types)):
						for param2 in range(param1 + 1):
							if (self.param_types[param1] == 'S2' and self.param_types[param2] == 'te') \
								or (self.param_types[param1] == 'te' and self.param_types[param2] == 'S2'):
								# Calculate the S2/te partial derivatives.
								self.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2dte_iso_m24(i, 0)
								self.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2dte_iso_m24(i, 1)
								self.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2dte_iso_m24(i, 2)
								self.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2dte_iso_m24(i, 3)
								self.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2dte_iso_m24(i, 4)
								# Off diagonal hessian components are symmetric.
								self.d2jw[i, 0, param2, param1] = self.d2jw[i, 0, param1, param2]
								self.d2jw[i, 1, param2, param1] = self.d2jw[i, 1, param1, param2]
								self.d2jw[i, 2, param2, param1] = self.d2jw[i, 2, param1, param2]
								self.d2jw[i, 3, param2, param1] = self.d2jw[i, 3, param1, param2]
								self.d2jw[i, 4, param2, param1] = self.d2jw[i, 4, param1, param2]
							elif self.param_types[param1] == 'te' and self.param_types[param2] == 'te':
								# Calculate the te/te partial derivatives.
								self.d2jw[i, 0, param1, param2] = self.calc_d2jw_dte2_iso_m24(i, 0)
								self.d2jw[i, 1, param1, param2] = self.calc_d2jw_dte2_iso_m24(i, 1)
								self.d2jw[i, 2, param1, param2] = self.calc_d2jw_dte2_iso_m24(i, 2)
								self.d2jw[i, 3, param1, param2] = self.calc_d2jw_dte2_iso_m24(i, 3)
								self.d2jw[i, 4, param1, param2] = self.calc_d2jw_dte2_iso_m24(i, 4)
			elif match('m5', self.mf_model):
				for i in range(self.mf.data.num_frq):
					for param1 in range(len(self.param_types)):
						for param2 in range(param1 + 1):
							if (self.param_types[param1] == 'S2f' and self.param_types[param2] == 'S2s') \
								or (self.param_types[param1] == 'S2s' and self.param_types[param2] == 'S2f'):
								# Calculate the S2f/S2s partial derivatives.
								self.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 0)
								self.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 1)
								self.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 2)
								self.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 3)
								self.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 4)
								# Off diagonal hessian components are symmetric.
								self.d2jw[i, 0, param2, param1] = self.d2jw[i, 0, param1, param2]
								self.d2jw[i, 1, param2, param1] = self.d2jw[i, 1, param1, param2]
								self.d2jw[i, 2, param2, param1] = self.d2jw[i, 2, param1, param2]
								self.d2jw[i, 3, param2, param1] = self.d2jw[i, 3, param1, param2]
								self.d2jw[i, 4, param2, param1] = self.d2jw[i, 4, param1, param2]
							elif (self.param_types[param1] == 'S2f' and self.param_types[param2] == 'ts') \
								or (self.param_types[param1] == 'ts' and self.param_types[param2] == 'S2f'):
								# Calculate the S2f/ts partial derivatives.
								self.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2fdts_iso_m5(i, 0)
								self.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2fdts_iso_m5(i, 1)
								self.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2fdts_iso_m5(i, 2)
								self.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2fdts_iso_m5(i, 3)
								self.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2fdts_iso_m5(i, 4)
								# Off diagonal hessian components are symmetric.
								self.d2jw[i, 0, param2, param1] = self.d2jw[i, 0, param1, param2]
								self.d2jw[i, 1, param2, param1] = self.d2jw[i, 1, param1, param2]
								self.d2jw[i, 2, param2, param1] = self.d2jw[i, 2, param1, param2]
								self.d2jw[i, 3, param2, param1] = self.d2jw[i, 3, param1, param2]
								self.d2jw[i, 4, param2, param1] = self.d2jw[i, 4, param1, param2]
							elif (self.param_types[param1] == 'S2s' and self.param_types[param2] == 'ts') \
								or (self.param_types[param1] == 'ts' and self.param_types[param2] == 'S2s'):
								# Calculate the S2s/ts partial derivatives.
								self.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2sdts_iso_m5(i, 0)
								self.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2sdts_iso_m5(i, 1)
								self.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2sdts_iso_m5(i, 2)
								self.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2sdts_iso_m5(i, 3)
								self.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2sdts_iso_m5(i, 4)
								# Off diagonal hessian components are symmetric.
								self.d2jw[i, 0, param2, param1] = self.d2jw[i, 0, param1, param2]
								self.d2jw[i, 1, param2, param1] = self.d2jw[i, 1, param1, param2]
								self.d2jw[i, 2, param2, param1] = self.d2jw[i, 2, param1, param2]
								self.d2jw[i, 3, param2, param1] = self.d2jw[i, 3, param1, param2]
								self.d2jw[i, 4, param2, param1] = self.d2jw[i, 4, param1, param2]
							elif self.param_types[param1] == 'ts' and self.param_types[param2] == 'ts':
								# Calculate the ts/ts partial derivatives.
								self.d2jw[i, 0, param1, param2] = self.calc_d2jw_dts2_iso_m5(i, 0)
								self.d2jw[i, 1, param1, param2] = self.calc_d2jw_dts2_iso_m5(i, 1)
								self.d2jw[i, 2, param1, param2] = self.calc_d2jw_dts2_iso_m5(i, 2)
								self.d2jw[i, 3, param1, param2] = self.calc_d2jw_dts2_iso_m5(i, 3)
								self.d2jw[i, 4, param1, param2] = self.calc_d2jw_dts2_iso_m5(i, 4)


		# Axially symmetric rotational diffusion.
		elif match(self.diff_type, 'axail'):
			print "Axially symetric diffusion not implemented yet, quitting program."
			sys.exit()

		# Anisotropic rotational diffusion.
		elif match(self.diff_type, 'aniso'):
			print "Anisotropic diffusion not implemented yet, quitting program."
			sys.exit()

		else:
			raise NameError, "Function option not set correctly, quitting program."

		# Store the spectral density hessian.
		self.mf.data.mf_data.d2jw = copy.deepcopy(self.d2jw)


	def calc_d2jw_dS2dte_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 S2/te partial derivative of the spectral density function for isotropic rotational diffusion."

		temp = -0.4
		return temp


	def calc_d2jw_dte2_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 te/te partial derivative of the spectral density function for isotropic rotational diffusion."

		temp = -0.8 * (1.0 - self.s2) * (1.0 + 1.0 / self.tm)
		return temp


	def calc_d2jw_dS2dte_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 S2/te partial derivative of the spectral density function for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.te_prime_sqrd

		temp = -0.4 * (1.0 - omega_te_prime_sqrd) / ((1.0 + omega_te_prime_sqrd)**2) * self.fact_a**2
		return temp


	def calc_d2jw_dte2_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 te/te partial derivative of the spectral density function for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.te_prime_sqrd

		a = 1.0 / ((1.0 + omega_te_prime_sqrd)**3)
		b = self.mf.data.frq_sqrd_list[i][frq_index] * self.te_prime * (3.0 - omega_te_prime_sqrd)
		c = (1.0 - omega_te_prime_sqrd**2) * (self.te + self.tm) * self.tm**-2

		temp = -0.8 * (1.0 - self.s2) * self.fact_a**4 * a * (b + c)
		return temp


	def calc_d2jw_dS2fdS2s_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f/S2s partial derivative of the spectral density function for isotropic rotational diffusion."

		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.tm_sqrd
		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.ts_prime_sqrd

		temp = 0.4 * (self.tm / (1.0 + omega_tm_sqrd) - self.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return temp


	def calc_d2jw_dS2fdts_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f/ts partial derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.ts_prime_sqrd

		temp = 0.4 * (1.0 - self.s2s) * ((1.0 - omega_ts_prime_sqrd) / ((1.0 + omega_ts_prime_sqrd)**2)) * self.fact_a**2
		return temp


	def calc_d2jw_dS2sdts_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2s/ts partial derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.ts_prime_sqrd

		temp = -0.4 * self.s2f * ((1.0 - omega_ts_prime_sqrd) / ((1.0 + omega_ts_prime_sqrd)**2)) * self.fact_a**2
		return temp


	def calc_d2jw_dts2_iso_m5(self, i, frq_index):
		"Calculate the model 5 ts/ts partial derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.ts_prime_sqrd

		a = 1.0 / ((1.0 + omega_ts_prime_sqrd)**3)
		b = self.mf.data.frq_sqrd_list[i][frq_index] * self.ts_prime * (3.0 - omega_ts_prime_sqrd)
		c = (1.0 - omega_ts_prime_sqrd**2) * (self.ts + self.tm) * self.tm**-2

		temp = -0.8 * (self.s2f - self.s2) * self.fact_a**4 * a * (b + c)
		return temp


	def initialise_d2jw_values(self):
		"Remap the parameters in self.mf_params, and make sure they are of the type float."

		# Isotropic dependent values.
		if match(self.diff_type, 'iso'):
			self.tm = self.diff_params
			self.tm_sqrd = self.tm ** 2

		# Diffusion independent values.
		if match('m[13]', self.mf_model):
			self.s2 = self.mf_params[0]
			self.s2_tm = self.s2 * self.tm

		elif match('m[24]', self.mf_model):
			self.s2 = self.mf_params[0]
			self.te = self.mf_params[1]
			self.fact_a = self.tm / (self.te + self.tm)
			self.te_prime = self.te * self.fact_a
			self.te_prime_sqrd = self.te_prime ** 2
			self.s2_tm = self.s2 * self.tm

		elif match('m5', self.mf_model):
			self.s2f = self.mf_params[0]
			self.s2s = self.mf_params[1]
			self.s2 = self.s2f * self.s2s
			self.ts = self.mf_params[2]
			self.fact_a = self.tm / (self.ts + self.tm)
			self.ts_prime = self.ts * self.fact_a
			self.ts_prime_sqrd = self.ts_prime ** 2
			self.s2s_tm = self.s2s * self.tm

