from re import match

class d2Jw:
	def __init__(self):
		"Function for creating the SRLS spectral density hessians."


	def d2Jw(self):
		"""Function to create SRLS spectral density hessians.

		The spectral density hessians
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.d2jw
		Dimension:  4D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters, model-free parameters)
		Type:  Numeric 4D matrix, Float64
		Dependencies:  None
		Required by:  self.data.d2ri


		Formulae
		~~~~~~~~

		"""

		# Initialise the spectral density hessians.
		self.data.d2jw = zeros((self.mf.data.num_frq, 5, len(self.data.params), len(self.data.params)), Float64)

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
