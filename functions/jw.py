import sys
from math import pi
from re import match


class jw:
	def __init__(self, mf):
		"Functions for calculating the spectral density and its derivative."

		self.mf = mf


	def J(self, options, mf_values):
		"""Function to calculate spectral density values and their derivatives.

		The arguments are:
		1: options - an array with:
			[0] - String.  The diffusion tensor, ie 'iso', 'axial', 'aniso'
			[1] - Array.  An array with the diffusion parameters
			[2] - String.  The model-free model
			[3] - Int.  0 = no derivatives, 1 = calculate derivatives.
		2: mf_values - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}

		For order parameters derivatives, the following equations are used:
			Normal model-free equation (S2 and te):

				d J(w)     2 /       tm                t'      \ 
				------  =  - | -------------  -  ------------- |
				 dS2       5 \ 1 + (w.tm)**2     1 + (w.t')**2 /

			Extended model-free equation (S2f, S2s, and ts):

				d J(w)     2 /    S2s.tm         (1 - S2s).t'  \ 
				------  =  - | -------------  +  ------------- |
				 dS2f      5 \ 1 + (w.tm)**2     1 + (w.t')**2 /


				d J(w)     2         /       tm                t'      \ 
				------  =  - . S2f . | -------------  -  ------------- |
				 dS2s      5         \ 1 + (w.tm)**2     1 + (w.t')**2 /


		For correlation time derivatives, the following equations are used:
			Normal model-free equation (S2 and te):

				d J(w)     2                1 - (w.t')**2      /   tm    \ 
				------  =  - . (1 - S2) . ------------------ . | ------- |**2
				 dte       5              (1 + (w.t')**2)**2   \ tm + te /

			Extended model-free equation (S2f, S2s, and ts):

				d J(w)     2                       1 - (w.t')**2      /   tm    \ 
				------  =  - . S2f . (1 - S2s) . ------------------ . | ------- |**2
				 dte       5                     (1 + (w.t')**2)**2   \ tm + ts /


		For chemical exchange derivatives, the following is used:

				d J(w)
				------  =  0
				 dRex

		Returned is an array of spectral density values.

		If derivatives are asked for, an array of arrays of spectral density value derivatives where the first dimension
		corresponds to the relaxation values and the second dimension corresponds to the model-free parameters
		is also returned.
		"""

		self.options = options
		self.mf_values = mf_values

		# Calculate frequency independent terms (to increase speed)
		self.initialise_mf_values()

		last_frq = 0.0
		self.jw = []
		if self.options[3] == 1:
			self.djw = []
			# Initialise an array with the model-free parameter labels.
			if match('m1', self.options[2]):
				self.param_types = ['S2']
			elif match('m2', self.options[2]):
				self.param_types = ['S2', 'te']
			elif match('m3', self.options[2]):
				self.param_types = ['S2', 'Rex']
			elif match('m4', self.options[2]):
				self.param_types = ['S2', 'te', 'Rex']
			elif match('m5', self.options[2]):
				self.param_types = ['S2f', 'S2s', 'ts']
			else:
				raise NameError, "Should not be here."

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			if self.mf.data.frq[self.mf.data.remap_table[i]] != last_frq:
				jw = []
				for frq_index in range(5):
					# Isotropic rotational diffusion.
					if match(self.options[0], 'iso'):
						if match('m[13]', self.options[2]):
							jw.append(self.calc_jw_iso_m13(i, frq_index))
						elif match('m[24]', self.options[2]):
							jw.append(self.calc_jw_iso_m24(i, frq_index))
						elif match('m5', self.options[2]):
							jw.append(self.calc_jw_iso_m5(i, frq_index))

					# Axially symmetric rotational diffusion.
					elif match(self.options[0], 'axail'):
						print "Axially symetric diffusion not implemented yet, quitting program."
						sys.exit()

					# Anisotropic rotational diffusion.
					elif match(self.options[0], 'aniso'):
						print "Anisotropic diffusion not implemented yet, quitting program."
						sys.exit()

					else:
						raise NameError, "Diffusion type set incorrectly, quitting program."


				# Derivatives.
				if self.options[3] == 1:
					djw = []
					for param in range(len(self.param_types)):
						djw.append([])
						for frq_index in range(5):
							# Isotropic rotational diffusion.
							if match(self.options[0], 'iso'):
								if match('m[13]', self.options[2]):
									if match('S2', self.param_types[param]):
										djw[param].append(self.calc_djw_dS2_iso_m13(i, frq_index))
									elif match('Rex', self.param_types[param]):
										djw[param].append(0.0)
								elif match('m[24]', self.options[2]):
									if match('S2', self.param_types[param]):
										djw[param].append(self.calc_djw_dS2_iso_m24(i, frq_index))
									elif match('te', self.param_types[param]):
										djw[param].append(self.calc_djw_dte_iso_m24(i, frq_index))
									elif match('Rex', self.param_types[param]):
										djw[param].append(0.0)
								elif match('m5', self.options[2]):
									if match('S2f', self.param_types[param]):
										djw[param].append(self.calc_djw_dS2f_iso_m5(i, frq_index))
									if match('S2s', self.param_types[param]):
										djw[param].append(self.calc_djw_dS2s_iso_m5(i, frq_index))
									if match('ts', self.param_types[param]):
										djw[param].append(self.calc_djw_dts_iso_m5(i, frq_index))

							# Axially symmetric rotational diffusion.
							elif match(self.options[0], 'axail'):
								print "Axially symetric diffusion not implemented yet, quitting program."
								sys.exit()

							# Anisotropic rotational diffusion.
							elif match(self.options[0], 'aniso'):
								print "Anisotropic diffusion not implemented yet, quitting program."
								sys.exit()

							else:
								raise NameError, "Function option not set correctly, quitting program."

			self.jw.append(jw)
			if self.options[3] == 1:
				self.djw.append(djw)

			# Set the last frequency value.
			last_frq = self.mf.data.frq[self.mf.data.remap_table[i]]

		if self.options[3] == 0:
			return self.jw
		else:
			return self.jw, self.djw


	def calc_jw_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 spectral density values for isotropic rotational diffusion."

		omega_tm_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.tm_sqrd
		jw = 0.4 * (self.s2_tm / (1.0 + omega_tm_sqrd))
		return jw


	def calc_jw_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 spectral density values for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.te_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.tm_sqrd
		jw = 0.4 * (self.s2_tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2) * self.te_prime / (1.0 + omega_te_prime_sqrd))
		return jw


	def calc_jw_iso_m5(self, i, frq_index):
		"Calculate the model 5 spectral density values for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.ts_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.tm_sqrd
		jw = 0.4 * self.s2f * (self.s2s_tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2s) * self.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return jw


	def calc_djw_dS2_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 S2 derivative of the spectral density function for isotropic rotational diffusion."

		omega_tm_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.tm_sqrd
		djw_dS2 = self.const_djw_dS2_norm / (1.0 + omega_tm_sqrd)
		return djw_dS2


	def calc_djw_dS2_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 S2 derivative of the spectral density function for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.te_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.tm_sqrd
		djw_dS2 = 0.4 * (self.tm / (1.0 + omega_tm_sqrd) - self.te_prime / (1.0 + omega_te_prime_sqrd))
		return djw_dS2


	def calc_djw_dS2f_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.ts_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.tm_sqrd
		djw_dS2f = 0.4 * (self.s2s * self.tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2s) * self.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return djw_dS2f


	def calc_djw_dS2s_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.ts_prime_sqrd
		omega_tm_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.tm_sqrd
		djw_dS2s = 0.4 * self.s2f * (self.tm / (1.0 + omega_tm_sqrd) - self.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return djw_dS2s


	def calc_djw_dte_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 te derivative of the spectral density function for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.te_prime_sqrd
		djw_dte = self.const_djw_dte_norm * ((1.0 - omega_te_prime_sqrd) / (1.0 + omega_te_prime_sqrd)**2) * (self.tm / (self.te + self.tm))**2
		return djw_dte


	def calc_djw_dts_iso_m5(self, i, frq_index):
		"Calculate the model 5 ts derivative of the spectral density function for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.mf.data.frq_sqrd_list[self.mf.data.remap_table[i]][frq_index] * self.ts_prime_sqrd
		djw_dts = self.const_djw_dts_ext * ((1.0 - omega_ts_prime_sqrd) / (1.0 + omega_ts_prime_sqrd)**2)
		return djw_dts


	def initialise_mf_values(self):
		"""Remap the parameters in self.mf_values, and make sure they are of the type float.

		Rex is not needed (not part of the spectral density)!
		"""

		# Isotropic dependent values.
		if match(self.options[0], 'iso'):
			self.tm = self.options[1][0]
			self.tm_sqrd = self.tm ** 2

		# Diffusion independent values.
		if match('m[13]', self.options[2]):
			self.s2 = self.mf_values[0]
			self.s2_tm = self.s2 * self.tm
		elif match('m[24]', self.options[2]):
			self.s2 = self.mf_values[0]
			self.te = self.mf_values[1]
			self.te_prime = (self.te * self.tm) / (self.te + self.tm)
			self.te_prime_sqrd = self.te_prime ** 2
			self.s2_tm = self.s2 * self.tm
		elif match('m5', self.options[2]):
			self.s2f = self.mf_values[0]
			self.s2s = self.mf_values[1]
			self.ts = self.mf_values[2]
			self.ts_prime = (self.ts * self.tm) / (self.ts + self.tm)
			self.ts_prime_sqrd = self.ts_prime ** 2
			self.s2s_tm = self.s2s * self.tm

		# Terms used for derivatives.
		if self.options[3] == 1:
			if match('m[13]', self.options[2]):
				self.const_djw_dS2_norm = 0.4 * self.tm
			elif match('m[24]', self.options[2]):
				#Normal model-free equation (S2 and te):
				#	                       2              /   tm    \ 
				#	const_djw_dte_norm  =  - . (1 - S2) . | ------- |**2
				#	                       5              \ tm + te /
				self.const_djw_dte_norm = 0.4 * (1.0 - self.s2) * (self.tm / (self.tm + self.te)) ** 2

			elif match('m5', self.options[2]):
				#Extended model-free equation (S2f, S2s, and ts):
				#	                      2                     /   tm    \ 
				#	const_djw_dts_ext  =  - . S2f . (1 - S2s) . | ------- |**2
				#	                      5                     \ tm + ts /
				self.const_djw_dts_ext = 0.4 * self.s2f * (1.0 - self.s2s) * (self.tm / (self.tm + self.ts)) ** 2
