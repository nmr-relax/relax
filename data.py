from math import pi


class data:
	def __init__(self):
		"""Class containing all the program data.
		
		"""

		self.gh = 26.7522e7
		self.gx = -2.7126e7
		self.g_ratio = self.gh / self.gx
		self.h = 6.6260755e-34
		self.h_bar = self.h / ( 2.0*pi )
		self.mu0 = 4.0*pi * 1e-7
