from re import match

class dJw:
	def __init__(self):
		"Function for creating the SRLS spectral density gradients."


	def dJw(self):
		"""Function to create SRLS spectral density gradients.

		The spectral density gradients
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.djw
		Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  None
		Required by:  self.data.dri, self.data.d2ri


		Formulae
		~~~~~~~~

		"""

		# Initialise the spectral density gradients.
		self.data.djw = zeros((self.relax.data.num_frq, 5, len(self.data.params)), Float64)

		# Isotropic rotational diffusion.
		if match(self.data.diff_type, 'iso'):
			raise NameError, "No code yet."

		# Axially symmetric rotational diffusion.
		elif match(self.data.diff_type, 'axail'):
			raise NameError, "Axially symetric diffusion not implemented yet, quitting program."

		# Anisotropic rotational diffusion.
		elif match(self.data.diff_type, 'aniso'):
			raise NameError, "Anisotropic diffusion not implemented yet, quitting program."

		else:
			raise NameError, "Function option not set correctly, quitting program."
