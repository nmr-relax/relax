import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class dJw:
	def __init__(self):
		"Function for creating the spectral density gradient 3D matrix."


	def dJw(self):
		"""Function to create spectral density gradient 3D matrix.

		The spectral density gradient
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.djw
		Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  None
		Required by:  self.data.dri, self.data.d2ri
		Stored:  Yes


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

		# Calculate frequency independent terms (to increase speed)
		self.initialise_djw_values()

		# Initialise the spectral density gradient 3D matrix.
		self.data.djw = zeros((self.mf.data.num_frq, 5, len(self.data.mf_params)), Float64)

		# Isotropic rotational diffusion.
		# (possibly switch the for loops to speed up calculations?)
		if match(self.data.diff_type, 'iso'):
			if match('m[13]', self.data.mf_model):
				for i in range(self.mf.data.num_frq):
					for param in range(len(self.data.jw_param_types)):
						if self.data.jw_param_types[param] == 'S2':
							self.data.djw[i, 0, param] = self.calc_djw_dS2_iso_m13(i, 0)
							self.data.djw[i, 1, param] = self.calc_djw_dS2_iso_m13(i, 1)
							self.data.djw[i, 2, param] = self.calc_djw_dS2_iso_m13(i, 2)
							self.data.djw[i, 3, param] = self.calc_djw_dS2_iso_m13(i, 3)
							self.data.djw[i, 4, param] = self.calc_djw_dS2_iso_m13(i, 4)
			elif match('m[24]', self.data.mf_model):
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
			elif match('m5', self.data.mf_model):
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
			print "Axially symetric diffusion not implemented yet, quitting program."
			sys.exit()

		# Anisotropic rotational diffusion.
		elif match(self.data.diff_type, 'aniso'):
			print "Anisotropic diffusion not implemented yet, quitting program."
			sys.exit()

		else:
			raise NameError, "Function option not set correctly, quitting program."


	def calc_djw_dS2_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 S2 derivative of the spectral density function for isotropic rotational diffusion."

		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.tm_sqrd
		djw_dS2 = 0.4 * self.data.tm / (1.0 + omega_tm_sqrd)
		return djw_dS2


	def calc_djw_dS2_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 S2 derivative of the spectral density function for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.te_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.tm_sqrd
		djw_dS2 = 0.4 * (self.data.tm / (1.0 + omega_tm_sqrd) - self.data.te_prime / (1.0 + omega_te_prime_sqrd))
		return djw_dS2


	def calc_djw_dS2f_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.ts_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.tm_sqrd
		djw_dS2f = 0.4 * (self.data.s2s * self.data.tm / (1.0 + omega_tm_sqrd) + (1.0 - self.data.s2s) * self.data.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return djw_dS2f


	def calc_djw_dS2s_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.ts_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.tm_sqrd
		djw_dS2s = 0.4 * self.data.s2f * (self.data.tm / (1.0 + omega_tm_sqrd) - self.data.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return djw_dS2s


	def calc_djw_dte_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 te derivative of the spectral density function for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.te_prime_sqrd
		djw_dte = 0.4 * (1.0 - self.data.s2) * ((1.0 - omega_te_prime_sqrd) / ((1.0 + omega_te_prime_sqrd)**2)) * ((self.data.tm / (self.data.tm + self.data.te))**2)
		return djw_dte


	def calc_djw_dts_iso_m5(self, i, frq_index):
		"Calculate the model 5 ts derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.ts_prime_sqrd
		djw_dts = 0.4 * self.data.s2f * (1.0 - self.data.s2s) * ((1.0 - omega_ts_prime_sqrd) / ((1.0 + omega_ts_prime_sqrd)**2)) * ((self.data.tm / (self.data.tm + self.data.ts))**2)
		return djw_dts


	def initialise_djw_values(self):
		"Remap the parameters in self.data.mf_params"

		# Isotropic dependent values.
		if match(self.data.diff_type, 'iso'):
			self.data.tm = self.data.diff_params
			self.data.tm_sqrd = self.data.tm ** 2

		# Diffusion independent values.
		if match('m[13]', self.data.mf_model):
			self.data.s2 = self.data.mf_params[0]
			self.data.s2_tm = self.data.s2 * self.data.tm
		elif match('m[24]', self.data.mf_model):
			self.data.s2 = self.data.mf_params[0]
			self.data.te = self.data.mf_params[1]
			self.data.te_prime = (self.data.te * self.data.tm) / (self.data.te + self.data.tm)
			self.data.te_prime_sqrd = self.data.te_prime ** 2
			self.data.s2_tm = self.data.s2 * self.data.tm
		elif match('m5', self.data.mf_model):
			self.data.s2f = self.data.mf_params[0]
			self.data.s2s = self.data.mf_params[1]
			self.data.ts = self.data.mf_params[2]
			self.data.ts_prime = (self.data.ts * self.data.tm) / (self.data.ts + self.data.tm)
			self.data.ts_prime_sqrd = self.data.ts_prime ** 2
			self.data.s2s_tm = self.data.s2s * self.data.tm
