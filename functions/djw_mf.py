class dJw:
	def __init__(self):
		"Function for creating the model-free spectral density gradients."


	def dJw(self):
		"""Function to create model-free spectral density gradients.

		The spectral density gradients
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.djw
		Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  None
		Required by:  self.data.dri, self.data.d2ri


		Formulae
		~~~~~~~~

		Original
		~~~~~~~~

			dJ(w)     2 /       tm                te'      \ 
			-----  =  - | -------------  -  -------------- |
			 dS2      5 \ 1 + (w.tm)**2     1 + (w.te')**2 /


			dJ(w)     2                1 - (w.te')**2      /   tm    \ 2
			-----  =  - . (1 - S2) . ------------------- . | ------- |
			 dte      5              (1 + (w.te')**2)**2   \ te + tm /


			dJ(w)
			-----  =  0
			dRex


			dJ(w)
			-----  =  0
			dcsa


			dJ(w)
			-----  =  0
			 dr


		Extended
		~~~~~~~~

			dJ(w)     2 /    S2s.tm               tf'          (1 - S2s).ts' \ 
			-----  =  - | -------------  -  -------------- +  -------------- |
			dS2f      5 \ 1 + (w.tm)**2     1 + (w.tf')**2    1 + (w.ts')**2 /


			dJ(w)     2.S2f   /       tm                ts'      \ 
			-----  =  ----- . | -------------  -  -------------- |
			dS2s        5     \ 1 + (w.tm)**2     1 + (w.ts')**2 /


			dJ(w)     2                 1 - (w.tf')**2      /   tm    \ 2
			-----  =  - . (1 - S2f) . ------------------- . | ------- |
			 dtf      5               (1 + (w.tf')**2)**2   \ tf + tm /


			dJ(w)     2.S2f                 1 - (w.ts')**2      /   tm    \ 2
			-----  =  ----- . (1 - S2s) . ------------------- . | ------- |
			 dts        5                 (1 + (w.ts')**2)**2   \ ts + tm /


			dJ(w)
			-----  =  0
			dRex


			dJ(w)
			-----  =  0
			dcsa


			dJ(w)
			-----  =  0
			 dr
		"""

		# Initialise the spectral density gradients.
		self.data.djw = zeros((self.mf.data.num_frq, 5, len(self.data.params)), Float64)

		# Isotropic rotational diffusion.
		if match(self.data.diff_type, 'iso'):
			if match('m[13]', self.data.model):
				for i in range(self.mf.data.num_frq):
					for param in range(len(self.data.jw_param_types)):
						if self.data.jw_param_types[param] == 'S2':
							self.data.djw[i, 0, param] = self.calc_djw_dS2_iso_m13(i, 0)
							self.data.djw[i, 1, param] = self.calc_djw_dS2_iso_m13(i, 1)
							self.data.djw[i, 2, param] = self.calc_djw_dS2_iso_m13(i, 2)
							self.data.djw[i, 3, param] = self.calc_djw_dS2_iso_m13(i, 3)
							self.data.djw[i, 4, param] = self.calc_djw_dS2_iso_m13(i, 4)
			elif match('m[24]', self.data.model):
				for i in range(self.mf.data.num_frq):
					for param in range(len(self.data.jw_param_types)):
						if self.data.jw_param_types[param] == 'S2':
							self.data.djw[i, 0, param] = self.calc_djw_dS2_iso_m24(i, 0)
							self.data.djw[i, 1, param] = self.calc_djw_dS2_iso_m24(i, 1)
							self.data.djw[i, 2, param] = self.calc_djw_dS2_iso_m24(i, 2)
							self.data.djw[i, 3, param] = self.calc_djw_dS2_iso_m24(i, 3)
							self.data.djw[i, 4, param] = self.calc_djw_dS2_iso_m24(i, 4)
						elif self.data.jw_param_types[param] == 'te':
							self.data.djw[i, 0, param] = self.calc_djw_dte_iso_m24(i, 0)
							self.data.djw[i, 1, param] = self.calc_djw_dte_iso_m24(i, 1)
							self.data.djw[i, 2, param] = self.calc_djw_dte_iso_m24(i, 2)
							self.data.djw[i, 3, param] = self.calc_djw_dte_iso_m24(i, 3)
							self.data.djw[i, 4, param] = self.calc_djw_dte_iso_m24(i, 4)
			elif match('m5', self.data.model):
				for i in range(self.mf.data.num_frq):
					for param in range(len(self.data.jw_param_types)):
						if self.data.jw_param_types[param] == 'S2f':
							self.data.djw[i, 0, param] = self.calc_djw_dS2f_iso_m5(i, 0)
							self.data.djw[i, 1, param] = self.calc_djw_dS2f_iso_m5(i, 1)
							self.data.djw[i, 2, param] = self.calc_djw_dS2f_iso_m5(i, 2)
							self.data.djw[i, 3, param] = self.calc_djw_dS2f_iso_m5(i, 3)
							self.data.djw[i, 4, param] = self.calc_djw_dS2f_iso_m5(i, 4)
						if self.data.jw_param_types[param] == 'S2s':
							self.data.djw[i, 0, param] = self.calc_djw_dS2s_iso_m5(i, 0)
							self.data.djw[i, 1, param] = self.calc_djw_dS2s_iso_m5(i, 1)
							self.data.djw[i, 2, param] = self.calc_djw_dS2s_iso_m5(i, 2)
							self.data.djw[i, 3, param] = self.calc_djw_dS2s_iso_m5(i, 3)
							self.data.djw[i, 4, param] = self.calc_djw_dS2s_iso_m5(i, 4)
						if self.data.jw_param_types[param] == 'ts':
							self.data.djw[i, 0, param] = self.calc_djw_dts_iso_m5(i, 0)
							self.data.djw[i, 1, param] = self.calc_djw_dts_iso_m5(i, 1)
							self.data.djw[i, 2, param] = self.calc_djw_dts_iso_m5(i, 2)
							self.data.djw[i, 3, param] = self.calc_djw_dts_iso_m5(i, 3)
							self.data.djw[i, 4, param] = self.calc_djw_dts_iso_m5(i, 4)

		# Axially symmetric rotational diffusion.
		elif match(self.data.diff_type, 'axail'):
			raise NameError, "Axially symetric diffusion not implemented yet, quitting program."

		# Anisotropic rotational diffusion.
		elif match(self.data.diff_type, 'aniso'):
			raise NameError, "Anisotropic diffusion not implemented yet, quitting program."

		else:
			raise NameError, "Function option not set correctly, quitting program."


	def calc_djw_dS2_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 S2 derivative of the spectral density function for isotropic rotational diffusion."

		temp = 0.4 * self.data.tm / (1.0 + self.data.omega_tm_sqrd[i, frq_index])
		return temp


	def calc_djw_dS2_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 S2 derivative of the spectral density function for isotropic rotational diffusion."

		temp = 0.4 * (self.data.tm / (1.0 + self.data.omega_tm_sqrd[i, frq_index]) - self.data.te_prime / (1.0 + self.data.omega_te_prime_sqrd[i, frq_index]))
		return temp


	def calc_djw_dS2f_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

		temp = 0.4 * (self.data.s2s * self.data.tm / (1.0 + self.data.omega_tm_sqrd[i, frq_index]) + (1.0 - self.data.s2s) * self.data.ts_prime / (1.0 + self.data.omega_ts_prime_sqrd[i, frq_index]))
		return temp


	def calc_djw_dS2s_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

		temp = 0.4 * self.data.s2f * (self.data.tm / (1.0 + self.data.omega_tm_sqrd[i, frq_index]) - self.data.ts_prime / (1.0 + self.data.omega_ts_prime_sqrd[i, frq_index]))
		return temp


	def calc_djw_dte_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 te derivative of the spectral density function for isotropic rotational diffusion."

		temp = 0.4 * (1.0 - self.data.s2) * ((1.0 - self.data.omega_te_prime_sqrd[i, frq_index]) / ((1.0 + self.data.omega_te_prime_sqrd[i, frq_index])**2)) * self.data.fact_a**2
		return temp


	def calc_djw_dts_iso_m5(self, i, frq_index):
		"Calculate the model 5 ts derivative of the spectral density function for isotropic rotational diffusion."

		temp = 0.4 * self.data.s2f * (1.0 - self.data.s2s) * ((1.0 - self.data.omega_ts_prime_sqrd[i, frq_index]) / ((1.0 + self.data.omega_ts_prime_sqrd[i, frq_index])**2)) * self.data.fact_a**2
		return temp
