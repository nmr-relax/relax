import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class dJw:
	def __init__(self, mf):
		"Function for creating the spectral density gradient 3D matrix."

		self.mf = mf


	def calc(self, mf_params, diff_type, diff_params, mf_model):
		"""Function to create spectral density gradient 3D matrix.

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


		The spectral density gradient
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.djw
		Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  None
		Required by:  self.dri, self.d2ri
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

		self.mf_params = mf_params
		self.diff_type = diff_type
		self.diff_params = diff_params
		self.mf_model = mf_model

		# Calculate frequency independent terms (to increase speed)
		self.initialise_djw_values()

		# Initialise the spectral density gradient 3D matrix.
		self.djw = zeros((self.mf.data.num_frq, 5, len(self.mf_params)), Float64)

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
			if match('m[13]', self.mf_model):
				for i in range(self.mf.data.num_frq):
					for param in range(len(self.param_types)):
						if match('S2', self.param_types[param]):
							self.djw[i, 0, param] = self.calc_djw_dS2_iso_m13(i, 0)
							self.djw[i, 1, param] = self.calc_djw_dS2_iso_m13(i, 1)
							self.djw[i, 2, param] = self.calc_djw_dS2_iso_m13(i, 2)
							self.djw[i, 3, param] = self.calc_djw_dS2_iso_m13(i, 3)
							self.djw[i, 4, param] = self.calc_djw_dS2_iso_m13(i, 4)
			elif match('m[24]', self.mf_model):
				for i in range(self.mf.data.num_frq):
					for param in range(len(self.param_types)):
						if match('S2', self.param_types[param]):
							self.djw[i, 0, param] = self.calc_djw_dS2_iso_m24(i, 0)
							self.djw[i, 1, param] = self.calc_djw_dS2_iso_m24(i, 1)
							self.djw[i, 2, param] = self.calc_djw_dS2_iso_m24(i, 2)
							self.djw[i, 3, param] = self.calc_djw_dS2_iso_m24(i, 3)
							self.djw[i, 4, param] = self.calc_djw_dS2_iso_m24(i, 4)
						elif match('te', self.param_types[param]):
							self.djw[i, 0, param] = self.calc_djw_dte_iso_m24(i, 0)
							self.djw[i, 1, param] = self.calc_djw_dte_iso_m24(i, 1)
							self.djw[i, 2, param] = self.calc_djw_dte_iso_m24(i, 2)
							self.djw[i, 3, param] = self.calc_djw_dte_iso_m24(i, 3)
							self.djw[i, 4, param] = self.calc_djw_dte_iso_m24(i, 4)
			elif match('m5', self.mf_model):
				for i in range(self.mf.data.num_frq):
					for param in range(len(self.param_types)):
						if match('S2f', self.param_types[param]):
							self.djw[i, 0, param] = self.calc_djw_dS2f_iso_m5(i, 0)
							self.djw[i, 1, param] = self.calc_djw_dS2f_iso_m5(i, 1)
							self.djw[i, 2, param] = self.calc_djw_dS2f_iso_m5(i, 2)
							self.djw[i, 3, param] = self.calc_djw_dS2f_iso_m5(i, 3)
							self.djw[i, 4, param] = self.calc_djw_dS2f_iso_m5(i, 4)
						if match('S2s', self.param_types[param]):
							self.djw[i, 0, param] = self.calc_djw_dS2s_iso_m5(i, 0)
							self.djw[i, 1, param] = self.calc_djw_dS2s_iso_m5(i, 1)
							self.djw[i, 2, param] = self.calc_djw_dS2s_iso_m5(i, 2)
							self.djw[i, 3, param] = self.calc_djw_dS2s_iso_m5(i, 3)
							self.djw[i, 4, param] = self.calc_djw_dS2s_iso_m5(i, 4)
						if match('ts', self.param_types[param]):
							self.djw[i, 0, param] = self.calc_djw_dts_iso_m5(i, 0)
							self.djw[i, 1, param] = self.calc_djw_dts_iso_m5(i, 1)
							self.djw[i, 2, param] = self.calc_djw_dts_iso_m5(i, 2)
							self.djw[i, 3, param] = self.calc_djw_dts_iso_m5(i, 3)
							self.djw[i, 4, param] = self.calc_djw_dts_iso_m5(i, 4)

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

		# Store the spectral density gradient 3D matrix.
		self.mf.data.mf_data.djw = copy.deepcopy(self.djw)


	def calc_djw_dS2_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 S2 derivative of the spectral density function for isotropic rotational diffusion."

		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.tm_sqrd
		djw_dS2 = 0.4 * self.tm / (1.0 + omega_tm_sqrd)
		return djw_dS2


	def calc_djw_dS2_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 S2 derivative of the spectral density function for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.te_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.tm_sqrd
		djw_dS2 = 0.4 * (self.tm / (1.0 + omega_tm_sqrd) - self.te_prime / (1.0 + omega_te_prime_sqrd))
		return djw_dS2


	def calc_djw_dS2f_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.ts_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.tm_sqrd
		djw_dS2f = 0.4 * (self.s2s * self.tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2s) * self.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return djw_dS2f


	def calc_djw_dS2s_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.ts_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.tm_sqrd
		djw_dS2s = 0.4 * self.s2f * (self.tm / (1.0 + omega_tm_sqrd) - self.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return djw_dS2s


	def calc_djw_dte_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 te derivative of the spectral density function for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.te_prime_sqrd
		djw_dte = 0.4 * (1.0 - self.s2) * ((1.0 - omega_te_prime_sqrd) / ((1.0 + omega_te_prime_sqrd)**2)) * ((self.tm / (self.tm + self.te))**2)
		return djw_dte


	def calc_djw_dts_iso_m5(self, i, frq_index):
		"Calculate the model 5 ts derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.ts_prime_sqrd
		djw_dts = 0.4 * self.s2f * (1.0 - self.s2s) * ((1.0 - omega_ts_prime_sqrd) / ((1.0 + omega_ts_prime_sqrd)**2)) * ((self.tm / (self.tm + self.ts))**2)
		return djw_dts


	def initialise_djw_values(self):
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
			self.te_prime = (self.te * self.tm) / (self.te + self.tm)
			self.te_prime_sqrd = self.te_prime ** 2
			self.s2_tm = self.s2 * self.tm
		elif match('m5', self.mf_model):
			self.s2f = self.mf_params[0]
			self.s2s = self.mf_params[1]
			self.ts = self.mf_params[2]
			self.ts_prime = (self.ts * self.tm) / (self.ts + self.tm)
			self.ts_prime_sqrd = self.ts_prime ** 2
			self.s2s_tm = self.s2s * self.tm
