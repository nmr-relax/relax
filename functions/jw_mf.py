import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class Jw:
	def __init__(self, mf):
		"Function for creating the spectral density matrix."

		self.mf = mf


	def calc(self, mf_params, diff_type, diff_params, mf_model):
		"""Function to create the spectral density matrix."

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


		The spectral density equation
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.jw
		Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
		Type:  Numeric matrix, Float64
		Dependencies:  None
		Required by:  self.ri, self.dri, self.d2ri
		Stored:  Yes


		Formulae
		~~~~~~~~

		Original
		~~~~~~~~

			         2 /    S2 . tm        (1 - S2) . te' \ 
			J(w)  =  - | -------------  +  -------------- |
			         5 \ 1 + (w.tm)**2     1 + (w.te')**2 /


		Extended
		~~~~~~~~

			         2 /    S2 . tm        (1 - Sf2) . tf'     (S2f - S2) . ts' \ 
			J(w)  =  - | -------------  +  ---------------  +  ---------------- |
			         5 \ 1 + (w.tm)**2     1 + (w.tf')**2       1 + (w.ts')**2  /

		"""

		self.mf_params = mf_params
		self.diff_type = diff_type
		self.diff_params = diff_params
		self.mf_model = mf_model

		# Calculate frequency independent terms (to increase speed)
		self.initialise_jw_values()

		# Initialise the spectral density matrix.
		self.jw = zeros((self.mf.data.num_frq, 5), Float64)

		# Isotropic rotational diffusion.
		if match(self.diff_type, 'iso'):
			if match('m[13]', self.mf_model):
				for i in range(self.mf.data.num_frq):
					self.jw[i, 0] = self.calc_jw_iso_m13(i, 0)
					self.jw[i, 1] = self.calc_jw_iso_m13(i, 1)
					self.jw[i, 2] = self.calc_jw_iso_m13(i, 2)
					self.jw[i, 3] = self.calc_jw_iso_m13(i, 3)
					self.jw[i, 4] = self.calc_jw_iso_m13(i, 4)
			elif match('m[24]', self.mf_model):
				for i in range(self.mf.data.num_frq):
					self.jw[i, 0] = self.calc_jw_iso_m24(i, 0)
					self.jw[i, 1] = self.calc_jw_iso_m24(i, 1)
					self.jw[i, 2] = self.calc_jw_iso_m24(i, 2)
					self.jw[i, 3] = self.calc_jw_iso_m24(i, 3)
					self.jw[i, 4] = self.calc_jw_iso_m24(i, 4)
			elif match('m5', self.mf_model):
				for i in range(self.mf.data.num_frq):
					self.jw[i, 0] = self.calc_jw_iso_m5(i, 0)
					self.jw[i, 1] = self.calc_jw_iso_m5(i, 1)
					self.jw[i, 2] = self.calc_jw_iso_m5(i, 2)
					self.jw[i, 3] = self.calc_jw_iso_m5(i, 3)
					self.jw[i, 4] = self.calc_jw_iso_m5(i, 4)

		# Axially symmetric rotational diffusion.
		elif match(self.diff_type, 'axail'):
			print "Axially symetric diffusion not implemented yet, quitting program."
			sys.exit()

		# Anisotropic rotational diffusion.
		elif match(self.diff_type, 'aniso'):
			print "Anisotropic diffusion not implemented yet, quitting program."
			sys.exit()

		else:
			raise NameError, "Diffusion type set incorrectly, quitting program."

		# Store the spectral density matrix.
		self.mf.data.mf_data.jw = copy.deepcopy(self.jw)


	def calc_jw_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 spectral density values for isotropic rotational diffusion."

		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.tm_sqrd
		jw = 0.4 * (self.s2_tm / (1.0 + omega_tm_sqrd))
		return jw


	def calc_jw_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 spectral density values for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.te_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.tm_sqrd
		jw = 0.4 * (self.s2_tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2) * self.te_prime / (1.0 + omega_te_prime_sqrd))
		return jw


	def calc_jw_iso_m5(self, i, frq_index):
		"Calculate the model 5 spectral density values for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.ts_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.tm_sqrd
		jw = 0.4 * self.s2f * (self.s2s_tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2s) * self.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return jw


	def initialise_jw_values(self):
		"""Remap the parameters in self.mf_params, and make sure they are of the type float.

		Rex is not needed (not part of the spectral density)!
		"""

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
