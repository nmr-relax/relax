from Numeric import Float64, copy, zeros
from re import match

from chi2 import chi2
from dchi2 import dchi2
from d2chi2 import d2chi2

from ri import Ri
from dri import dRi
from d2ri import d2Ri

from ri_prime import Ri_prime
from dri_prime import dRi_prime
from d2ri_prime import d2Ri_prime

from jw_srls import Jw
from djw_srls import dJw
from d2jw_srls import d2Jw

from data import data

class srls_functions(chi2, dchi2, d2chi2, Ri, dRi, d2Ri, Ri_prime, dRi_prime, d2Ri_prime, Jw, dJw, d2Jw):
	def __init__(self, mf):
		"""Class used to store all the SRLS function classes.

		See the respective files for descriptions of the functions and detials of the formulae.
		"""

		self.mf = mf

		# Class containing data.
		self.data = data()


	def init_param_types(self):
		"Initialise arrays with the SRLS parameter labels."

		# Relaxation parameter labels.
		if self.data.model == 'm1':
			self.data.ri_param_types = ['Jj']
		elif self.data.model == 'm2':
			self.data.ri_param_types = ['Jj', 'Jj']
		elif self.data.model == 'm3':
			self.data.ri_param_types = ['Jj', 'Rex']
		elif self.data.model == 'm4':
			self.data.ri_param_types = ['Jj', 'Jj', 'Rex']
		elif self.data.model == 'm5':
			self.data.ri_param_types = ['Jj', 'Jj', 'Jj']
		else:
			raise NameError, "Should not be here."
