class d2Jw:
	def __init__(self):
		"Function for creating the model-free spectral density hessians."


	def d2Jw(self):
		"""Function to create model-free spectral density hessians.

		The spectral density hessians
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.d2jw
		Dimension:  4D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters, model-free parameters)
		Type:  Numeric 4D matrix, Float64
		Dependencies:  None
		Required by:  self.data.d2ri


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

		# Initialise the spectral density hessians.
		self.data.d2jw = zeros((self.mf.data.num_frq, 5, len(self.data.params), len(self.data.params)), Float64)

		# Isotropic rotational diffusion.
		if match(self.data.diff_type, 'iso'):
			# Model 1 and 3 hessians are zero.
			if match('m[24]', self.data.model):
				for i in range(self.mf.data.num_frq):
					for param1 in range(len(self.data.jw_param_types)):
						for param2 in range(param1 + 1):
							if (self.data.jw_param_types[param1] == 'S2' and self.data.jw_param_types[param2] == 'te') \
								or (self.data.jw_param_types[param1] == 'te' and self.data.jw_param_types[param2] == 'S2'):
								# Calculate the S2/te partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2dte_iso_m24(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2dte_iso_m24(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2dte_iso_m24(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2dte_iso_m24(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2dte_iso_m24(i, 4)
								# Off diagonal hessian components are symmetric.
								self.data.d2jw[i, 0, param2, param1] = self.data.d2jw[i, 0, param1, param2]
								self.data.d2jw[i, 1, param2, param1] = self.data.d2jw[i, 1, param1, param2]
								self.data.d2jw[i, 2, param2, param1] = self.data.d2jw[i, 2, param1, param2]
								self.data.d2jw[i, 3, param2, param1] = self.data.d2jw[i, 3, param1, param2]
								self.data.d2jw[i, 4, param2, param1] = self.data.d2jw[i, 4, param1, param2]
							elif self.data.jw_param_types[param1] == 'te' and self.data.jw_param_types[param2] == 'te':
								# Calculate the te/te partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dte2_iso_m24(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dte2_iso_m24(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dte2_iso_m24(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dte2_iso_m24(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dte2_iso_m24(i, 4)
			elif match('m5', self.data.model):
				for i in range(self.mf.data.num_frq):
					for param1 in range(len(self.data.jw_param_types)):
						for param2 in range(param1 + 1):
							if (self.data.jw_param_types[param1] == 'S2f' and self.data.jw_param_types[param2] == 'S2s') \
								or (self.data.jw_param_types[param1] == 'S2s' and self.data.jw_param_types[param2] == 'S2f'):
								# Calculate the S2f/S2s partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 4)
								# Off diagonal hessian components are symmetric.
								self.data.d2jw[i, 0, param2, param1] = self.data.d2jw[i, 0, param1, param2]
								self.data.d2jw[i, 1, param2, param1] = self.data.d2jw[i, 1, param1, param2]
								self.data.d2jw[i, 2, param2, param1] = self.data.d2jw[i, 2, param1, param2]
								self.data.d2jw[i, 3, param2, param1] = self.data.d2jw[i, 3, param1, param2]
								self.data.d2jw[i, 4, param2, param1] = self.data.d2jw[i, 4, param1, param2]
							elif (self.data.jw_param_types[param1] == 'S2f' and self.data.jw_param_types[param2] == 'ts') \
								or (self.data.jw_param_types[param1] == 'ts' and self.data.jw_param_types[param2] == 'S2f'):
								# Calculate the S2f/ts partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2fdts_iso_m5(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2fdts_iso_m5(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2fdts_iso_m5(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2fdts_iso_m5(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2fdts_iso_m5(i, 4)
								# Off diagonal hessian components are symmetric.
								self.data.d2jw[i, 0, param2, param1] = self.data.d2jw[i, 0, param1, param2]
								self.data.d2jw[i, 1, param2, param1] = self.data.d2jw[i, 1, param1, param2]
								self.data.d2jw[i, 2, param2, param1] = self.data.d2jw[i, 2, param1, param2]
								self.data.d2jw[i, 3, param2, param1] = self.data.d2jw[i, 3, param1, param2]
								self.data.d2jw[i, 4, param2, param1] = self.data.d2jw[i, 4, param1, param2]
							elif (self.data.jw_param_types[param1] == 'S2s' and self.data.jw_param_types[param2] == 'ts') \
								or (self.data.jw_param_types[param1] == 'ts' and self.data.jw_param_types[param2] == 'S2s'):
								# Calculate the S2s/ts partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2sdts_iso_m5(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2sdts_iso_m5(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2sdts_iso_m5(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2sdts_iso_m5(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2sdts_iso_m5(i, 4)
								# Off diagonal hessian components are symmetric.
								self.data.d2jw[i, 0, param2, param1] = self.data.d2jw[i, 0, param1, param2]
								self.data.d2jw[i, 1, param2, param1] = self.data.d2jw[i, 1, param1, param2]
								self.data.d2jw[i, 2, param2, param1] = self.data.d2jw[i, 2, param1, param2]
								self.data.d2jw[i, 3, param2, param1] = self.data.d2jw[i, 3, param1, param2]
								self.data.d2jw[i, 4, param2, param1] = self.data.d2jw[i, 4, param1, param2]
							elif self.data.jw_param_types[param1] == 'ts' and self.data.jw_param_types[param2] == 'ts':
								# Calculate the ts/ts partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dts2_iso_m5(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dts2_iso_m5(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dts2_iso_m5(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dts2_iso_m5(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dts2_iso_m5(i, 4)


		# Axially symmetric rotational diffusion.
		elif match(self.data.diff_type, 'axail'):
			raise NameError, "Axially symetric diffusion not implemented yet, quitting program."

		# Anisotropic rotational diffusion.
		elif match(self.data.diff_type, 'aniso'):
			raise NameError, "Anisotropic diffusion not implemented yet, quitting program."

		else:
			raise NameError, "Function option not set correctly, quitting program."


	def calc_d2jw_dS2dte_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 S2/te partial derivative of the spectral density function for isotropic rotational diffusion."

		temp = -0.4
		return temp


	def calc_d2jw_dte2_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 te/te partial derivative of the spectral density function for isotropic rotational diffusion."

		temp = -0.8 * (1.0 - self.data.s2) * (1.0 + 1.0 / self.data.tm)
		return temp


	def calc_d2jw_dS2dte_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 S2/te partial derivative of the spectral density function for isotropic rotational diffusion."

		temp = -0.4 * (1.0 - self.data.omega_te_prime_sqrd[i, frq_index]) / ((1.0 + self.data.omega_te_prime_sqrd[i, frq_index])**2) * self.data.fact_a**2
		return temp


	def calc_d2jw_dte2_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 te/te partial derivative of the spectral density function for isotropic rotational diffusion."

		a = 1.0 / ((1.0 + self.data.omega_te_prime_sqrd[i, frq_index])**3)
		b = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.te_prime * (3.0 - self.data.omega_te_prime_sqrd[i, frq_index])
		c = (1.0 - self.data.omega_te_prime_sqrd[i, frq_index]**2) * (self.data.te + self.data.tm) * self.data.tm**-2

		temp = -0.8 * (1.0 - self.data.s2) * self.data.fact_a**4 * a * (b + c)
		return temp


	def calc_d2jw_dS2fdS2s_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f/S2s partial derivative of the spectral density function for isotropic rotational diffusion."

		temp = 0.4 * (self.data.tm / (1.0 + self.data.omega_tm_sqrd[i, frq_index]) - self.data.ts_prime / (1.0 + self.data.omega_ts_prime_sqrd[i, frq_index]))
		return temp


	def calc_d2jw_dS2fdts_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f/ts partial derivative of the spectral density function for isotropic rotational diffusion."

		temp = 0.4 * (1.0 - self.data.s2s) * ((1.0 - self.data.omega_ts_prime_sqrd[i, frq_index]) / ((1.0 + self.data.omega_ts_prime_sqrd[i, frq_index])**2)) * self.data.fact_a**2
		return temp


	def calc_d2jw_dS2sdts_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2s/ts partial derivative of the spectral density function for isotropic rotational diffusion."

		temp = -0.4 * self.data.s2f * ((1.0 - self.data.omega_ts_prime_sqrd[i, frq_index]) / ((1.0 + self.data.omega_ts_prime_sqrd[i, frq_index])**2)) * self.data.fact_a**2
		return temp


	def calc_d2jw_dts2_iso_m5(self, i, frq_index):
		"Calculate the model 5 ts/ts partial derivative of the spectral density function for isotropic rotational diffusion."

		a = 1.0 / ((1.0 + self.data.omega_ts_prime_sqrd[i, frq_index])**3)
		b = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.ts_prime * (3.0 - self.data.omega_ts_prime_sqrd[i, frq_index])
		c = (1.0 - self.data.omega_ts_prime_sqrd[i, frq_index]**2) * (self.data.ts + self.data.tm) * self.data.tm**-2

		temp = -0.8 * (self.data.s2f - self.data.s2) * self.data.fact_a**4 * a * (b + c)
		return temp
