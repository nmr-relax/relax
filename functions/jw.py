import sys
from math import pi
from re import match


class jw:
	def __init__(self):
		""" Functions for calculating the spectral density and its derivative.

		J() - Calculate the spectral density value for the model-free model, parameter values, and frequency.
			A single spectral density value is returned.

		dJ() - Calculate the derivative of the spectral density function for the model-free model, parameter values, and frequency.
			The derivative of the spectral density function is returned.

		Large repetition of code is to increase the speed of the function.
		"""


	def J(self, options, frequency, mf_values):
		"""Function to calculate the spectral density.

		The arguments are:
		1: options - an array with:
			[0] - the diffusion tensor, ie 'iso', 'axial', 'aniso'
			[1] - an array with the diffusion parameters
			[2] - the model-free model
		2: frequency - the frequency in MHz to calculate the spectral density at.
		3: mf_values - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}

		Returned is the single spectral density value.
		"""

		self.options = options
		self.frequency = frequency
		self.mf_values = mf_values

		self.initialise_mf_values()

		# Isotropic rotational diffusion.
		if match(self.options[0], 'iso'):
			self.tm = float(self.options[1][0])
			if match('m1', self.options[2]) or match('m3', self.options[2]):
				self.calc_jw_iso_m13()
			elif match('m2', self.options[2]) or match('m4', self.options[2]):
				self.calc_jw_iso_m24()
			elif match('m5', self.options[2]):
				self.calc_jw_iso_m5()

		# Axially symmetric rotational diffusion.
		elif match(self.options[0], 'axail'):
			print "Axially symetric diffusion not implemented yet, quitting program."
			sys.exit()

		# Anisotropic rotational diffusion.
		elif match(self.options[0], 'aniso'):
			print "Anisotropic diffusion not implemented yet, quitting program."
			sys.exit()

		else:
			print "Function option not set correctly, quitting program."
			sys.exit()

		return self.jw


	def dJ(self, options, frequency, mf_values, param_type):
		"""Function to calculate the derivative of the spectral density function.

		The arguments are:
		1: options - an array with:
			[0] - the diffusion tensor, ie 'iso', 'axial', 'aniso'
			[1] - an array with the diffusion parameters
			[2] - the model-free model
		2: frequency - the frequency in MHz to calculate the spectral density at.
		3: mf_values - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}

		Returned is the derivative of the spectral density function.


		For order parameters, the following derivative are used:
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


		For correlation times, the following derivative are used:
			Normal model-free equation (S2 and te):

				d J(w)     2                1 - (w.t')**2      /   tm    \ 
				------  =  - . (1 - S2) . ------------------ . | ------- |**2
				 dte       5              (1 + (w.t')**2)**2   \ tm + te /

			Extended model-free equation (S2f, S2s, and ts):

				d J(w)     2                       1 - (w.t')**2      /   tm    \ 
				------  =  - . S2f . (1 - S2s) . ------------------ . | ------- |**2
				 dte       5                     (1 + (w.t')**2)**2   \ tm + ts /


		For chemical exchange, the following derivative are used:

				d J(w)
				------  =  0
				 dRex

		"""

		self.options = options
		self.frequency = frequency
		self.mf_values = mf_values

		self.initialise_mf_values()

		# Isotropic rotational diffusion.
		if match(self.options[0], 'iso'):
			self.tm = float(self.options[1][0])
			if match('m1', self.options[2]) or match('m3', self.options[2]):
				if match('S2', param_type):
					self.djw = self.calc_djw_dS2_iso_m13()
				elif match('Rex', param_type):
					self.djw = 0.0
			elif match('m2', self.options[2]) or match('m4', self.options[2]):
				if match('S2', param_type):
					self.djw = self.calc_djw_dS2_iso_m24()
				elif match('te', param_type):
					self.djw = self.calc_djw_dte_iso_m24()
				elif match('Rex', param_type):
					self.djw = 0.0
			elif match('m5', self.options[2]):
				if match('S2f', param_type):
					self.djw = self.calc_djw_dS2f_iso_m5()
				if match('S2s', param_type):
					self.djw = self.calc_djw_dS2s_iso_m5()
				if match('ts', param_type):
					self.djw = self.calc_djw_dts_iso_m5()

		# Axially symmetric rotational diffusion.
		elif match(self.options[0], 'axail'):
			print "Axially symetric diffusion not implemented yet, quitting program."
			sys.exit()

		# Anisotropic rotational diffusion.
		elif match(self.options[0], 'aniso'):
			print "Anisotropic diffusion not implemented yet, quitting program."
			sys.exit()

		else:
			print "Function option not set correctly, quitting program."
			sys.exit()

		return self.djw


	def calc_jw_iso_m13(self):
		"Calculate the model 1 and 3 spectral density values for isotropic rotational diffusion."

		s2_tm = self.s2 * self.tm
		omega_tm_sqrd = (self.frequency * self.tm) ** 2

		self.jw = 0.4 * (s2_tm / (1.0 + omega_tm_sqrd))


	def calc_jw_iso_m24(self):
		"Calculate the model 2 and 4 spectral density values for isotropic rotational diffusion."

		s2_tm = self.s2 * self.tm
		tprime = (self.te * self.tm) / (self.te + self.tm)
		omega_tprime_sqrd = (self.frequency * tprime) ** 2
		omega_tm_sqrd = (self.frequency * self.tm) ** 2

		self.jw = 0.4 * (s2_tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2) * tprime / (1.0 + omega_tprime_sqrd))


	def calc_jw_iso_m5(self):
		"Calculate the model 5 spectral density values for isotropic rotational diffusion."

		s2s_tm = self.s2s * self.tm
		tprime = (self.ts * self.tm) / (self.ts + self.tm)
		omega_tprime_sqrd = (self.frequency * tprime) ** 2
		omega_tm_sqrd = (self.frequency * self.tm) ** 2

		self.jw = 0.4 * self.s2f * (s2s_tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2s) * tprime / (1.0 + omega_tprime_sqrd))


	def calc_djw_dS2_iso_m13(self):
		"Calculate the model 1 and 3 S2 derivative of the spectral density function for isotropic rotational diffusion."

		omega_tm_sqrd = (self.frequency * self.tm) ** 2

		djw_dS2 = 0.4 * (self.tm / (1.0 + omega_tm_sqrd))

		return djw_dS2


	def calc_djw_dS2_iso_m24(self):
		"Calculate the model 2 and 4 S2 derivative of the spectral density function for isotropic rotational diffusion."

		tprime = (self.te * self.tm) / (self.te + self.tm)
		omega_tprime_sqrd = (self.frequency * tprime) ** 2
		omega_tm_sqrd = (self.frequency * self.tm) ** 2

		djw_dS2 = 0.4 * (self.tm / (1.0 + omega_tm_sqrd) - tprime / (1.0 + omega_tprime_sqrd))

		return djw_dS2


	def calc_djw_dS2f_iso_m5(self):
		"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

		tprime = (self.ts * self.tm) / (self.ts + self.tm)
		omega_tprime_sqrd = (self.frequency * tprime) ** 2
		omega_tm_sqrd = (self.frequency * self.tm) ** 2

		djw_dS2f = 0.4 * (self.s2s * self.tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2s) * tprime / (1.0 + omega_tprime_sqrd))

		return djw_dS2f


	def calc_djw_dS2s_iso_m5(self):
		"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

		tprime = (self.ts * self.tm) / (self.ts + self.tm)
		omega_tprime_sqrd = (self.frequency * tprime) ** 2
		omega_tm_sqrd = (self.frequency * self.tm) ** 2

		djw_dS2s = 0.4 * self.s2f * (self.tm / (1.0 + omega_tm_sqrd) - tprime / (1.0 + omega_tprime_sqrd))

		return djw_dS2s


	def calc_djw_dte_iso_m13(self):
		"Calculate the model 1 and 3 te derivative of the spectral density function for isotropic rotational diffusion."

		djw_te = 0.4 * (1.0 - self.s2)

		return djw_dte


	def calc_djw_dte_iso_m24(self):
		"Calculate the model 2 and 4 te derivative of the spectral density function for isotropic rotational diffusion."

		tprime = (self.te * self.tm) / (self.te + self.tm)
		omega_tprime_sqrd = (self.frequency * tprime) ** 2

		djw_te = 0.4 * (1.0 - self.s2) * ((1.0 - omega_tprime_sqrd) / (1.0 + omega_tprime_sqrd)**2) * (self.tm / (self.te + self.tm))**2

		return djw_dte


	def calc_djw_dts_iso_m5(self):
		"Calculate the model 5 ts derivative of the spectral density function for isotropic rotational diffusion."

		tprime = (self.ts * self.tm) / (self.ts + self.tm)
		omega_tprime_sqrd = (self.frequency * tprime) ** 2

		djw_ts = 0.4 * self.s2f * (1.0 - self.s2s) * ((1.0 - omega_tprime_sqrd) / (1.0 + omega_tprime_sqrd)**2) * (self.tm / (self.ts + self.tm))**2

		return djw_dts


	def initialise_mf_values(self):
		"""Remap the parameters in self.mf_values, and make sure they are of the type float.

		Rex is not needed (not part of the spectral density)!

		To increase efficiency, remove this section after cleaning program code so that
		self.mf_values are always of type float!
		"""
		if match('m1', self.options[2]) or match('m3', self.options[2]):
			self.s2  = float(self.mf_values[0])
		elif match('m2', self.options[2] or match('m4', self.options[2])):
			self.s2  = float(self.mf_values[0])
			self.te  = float(self.mf_values[1]) * 1e-12
		elif match('m5', self.options[2]):
			self.s2f = float(self.mf_values[0])
			self.s2s = float(self.mf_values[1])
			self.ts  = float(self.mf_values[2]) * 1e-12
		else:
			print "Model-free model " + `self.options[2]` + " not implemented yet, quitting program."
			sys.exit()
