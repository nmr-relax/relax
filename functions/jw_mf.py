import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class Jw:
	def __init__(self):
		"Function for creating the spectral density matrix."


	def Jw(self):
		"""Function to create the spectral density matrix."

		The spectral density equation
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.jw
		Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
		Type:  Numeric matrix, Float64
		Dependencies:  None
		Required by:  self.data.ri, self.data.dri, self.data.d2ri
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

		# Calculate frequency independent terms (to increase speed)
		self.initialise_jw_values()

		# Initialise the spectral density matrix.
		self.data.jw = zeros((self.mf.data.num_frq, 5), Float64)

		# Isotropic rotational diffusion.
		if match(self.data.diff_type, 'iso'):
			if match('m[13]', self.data.mf_model):
				for i in range(self.mf.data.num_frq):
					self.data.jw[i, 0] = self.calc_jw_iso_m13(i, 0)
					self.data.jw[i, 1] = self.calc_jw_iso_m13(i, 1)
					self.data.jw[i, 2] = self.calc_jw_iso_m13(i, 2)
					self.data.jw[i, 3] = self.calc_jw_iso_m13(i, 3)
					self.data.jw[i, 4] = self.calc_jw_iso_m13(i, 4)
			elif match('m[24]', self.data.mf_model):
				for i in range(self.mf.data.num_frq):
					self.data.jw[i, 0] = self.calc_jw_iso_m24(i, 0)
					self.data.jw[i, 1] = self.calc_jw_iso_m24(i, 1)
					self.data.jw[i, 2] = self.calc_jw_iso_m24(i, 2)
					self.data.jw[i, 3] = self.calc_jw_iso_m24(i, 3)
					self.data.jw[i, 4] = self.calc_jw_iso_m24(i, 4)
			elif match('m5', self.data.mf_model):
				for i in range(self.mf.data.num_frq):
					self.data.jw[i, 0] = self.calc_jw_iso_m5(i, 0)
					self.data.jw[i, 1] = self.calc_jw_iso_m5(i, 1)
					self.data.jw[i, 2] = self.calc_jw_iso_m5(i, 2)
					self.data.jw[i, 3] = self.calc_jw_iso_m5(i, 3)
					self.data.jw[i, 4] = self.calc_jw_iso_m5(i, 4)

		# Axially symmetric rotational diffusion.
		elif match(self.data.diff_type, 'axail'):
			print "Axially symetric diffusion not implemented yet, quitting program."
			sys.exit()

		# Anisotropic rotational diffusion.
		elif match(self.data.diff_type, 'aniso'):
			print "Anisotropic diffusion not implemented yet, quitting program."
			sys.exit()

		else:
			raise NameError, "Diffusion type set incorrectly, quitting program."


	def calc_jw_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 spectral density values for isotropic rotational diffusion."

		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.tm_sqrd
		jw = 0.4 * (self.data.s2_tm / (1.0 + omega_tm_sqrd))
		return jw


	def calc_jw_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 spectral density values for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.te_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.tm_sqrd
		jw = 0.4 * (self.data.s2_tm / (1.0 + omega_tm_sqrd) + (1.0 - self.data.s2) * self.data.te_prime / (1.0 + omega_te_prime_sqrd))
		return jw


	def calc_jw_iso_m5(self, i, frq_index):
		"Calculate the model 5 spectral density values for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.ts_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[i][frq_index] * self.data.tm_sqrd
		jw = 0.4 * self.data.s2f * (self.data.s2s_tm / (1.0 + omega_tm_sqrd) + (1.0 - self.data.s2s) * self.data.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return jw


	def initialise_jw_values(self):
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
