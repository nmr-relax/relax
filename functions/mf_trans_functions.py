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

from jw_mf_trans import Jw
from djw_mf_trans import dJw
from d2jw_mf_trans import d2Jw

from data import data

class mf_trans_functions(chi2, dchi2, d2chi2, Ri, dRi, d2Ri, Ri_prime, dRi_prime, d2Ri_prime, Jw, dJw, d2Jw):
	def __init__(self, relax):
		"""Class used to store all the transformed model-free function classes.

		See the respective files for descriptions of the functions and detials of the formulae.
		"""

		self.relax = relax

		# Class containing data.
		self.data = data()


	def init_param_types(self):
		"Initialise arrays with the model-free parameter labels."

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

		# J(w) parameter labels.
		if self.data.model == 'm1':
			self.data.jw_param_types = ['S2']
		elif self.data.model == 'm2':
			self.data.jw_param_types = ['S2', 'te']
		elif self.data.model == 'm3':
			self.data.jw_param_types = ['S2', None]
		elif self.data.model == 'm4':
			self.data.jw_param_types = ['S2', 'te', None]
		elif self.data.model == 'm5':
			self.data.jw_param_types = ['S2f', 'S2s', 'ts']
		else:
			raise NameError, "Should not be here."


	def lm_dri(self):
		return self.data.dri
