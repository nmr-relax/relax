from re import match

class Jw:
	def __init__(self):
		"Function for creating the SRLS spectral density values."


	def Jw(self):
		"""Function to create the SRLS spectral density values."

		The spectral density equation
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.jw
		Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
		Type:  Numeric matrix, Float64
		Dependencies:  None
		Required by:  self.data.ri, self.data.dri, self.data.d2ri


		Formulae
		~~~~~~~~

		"""

		# Initialise the spectral density values.
		self.data.jw = zeros((self.relax.data.num_frq, 5), Float64)

		# Isotropic rotational diffusion.
		if match(self.data.diff_type, 'iso'):
			if match('m[13]', self.data.model):
				for i in range(self.relax.data.num_frq):
					self.data.jw[i, 0] = self.calc_jw_iso_m13(i, 0)
					self.data.jw[i, 1] = self.calc_jw_iso_m13(i, 1)
					self.data.jw[i, 2] = self.calc_jw_iso_m13(i, 2)
					self.data.jw[i, 3] = self.calc_jw_iso_m13(i, 3)
					self.data.jw[i, 4] = self.calc_jw_iso_m13(i, 4)
			elif match('m[24]', self.data.model):
				for i in range(self.relax.data.num_frq):
					self.data.jw[i, 0] = self.calc_jw_iso_m24(i, 0)
					self.data.jw[i, 1] = self.calc_jw_iso_m24(i, 1)
					self.data.jw[i, 2] = self.calc_jw_iso_m24(i, 2)
					self.data.jw[i, 3] = self.calc_jw_iso_m24(i, 3)
					self.data.jw[i, 4] = self.calc_jw_iso_m24(i, 4)
			elif match('m5', self.data.model):
				for i in range(self.relax.data.num_frq):
					self.data.jw[i, 0] = self.calc_jw_iso_m5(i, 0)
					self.data.jw[i, 1] = self.calc_jw_iso_m5(i, 1)
					self.data.jw[i, 2] = self.calc_jw_iso_m5(i, 2)
					self.data.jw[i, 3] = self.calc_jw_iso_m5(i, 3)
					self.data.jw[i, 4] = self.calc_jw_iso_m5(i, 4)

		# Axially symmetric rotational diffusion.
		elif match(self.data.diff_type, 'axail'):
			raise NameError, "Axially symetric diffusion not implemented yet, quitting program."

		# Anisotropic rotational diffusion.
		elif match(self.data.diff_type, 'aniso'):
			raise NameError, "Anisotropic diffusion not implemented yet, quitting program."

		else:
			raise NameError, "Diffusion type set incorrectly, quitting program."


	def calc_jw_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 spectral density values for isotropic rotational diffusion."

		temp = 0.0
		return temp


	def calc_jw_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 spectral density values for isotropic rotational diffusion."

		temp = 0.0
		return temp


	def calc_jw_iso_m5(self, i, frq_index):
		"Calculate the model 5 spectral density values for isotropic rotational diffusion."

		temp = 0.0
		return temp
