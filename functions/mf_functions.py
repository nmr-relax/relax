from chi2 import chi2
from dchi2 import dchi2
from d2chi2 import d2chi2

from ri import Ri
from dri import dRi
from d2ri import d2Ri

from ri_prime import Ri_prime
from dri_prime import dRi_prime
from d2ri_prime import d2Ri_prime

from jw_mf import Jw
from djw_mf import dJw
from d2jw_mf import d2Jw

from temp_mf_data import data

class mf_functions(chi2, dchi2, d2chi2, Ri, dRi, d2Ri, Ri_prime, dRi_prime, d2Ri_prime, Jw, dJw, d2Jw):
	def __init__(self, mf):
		"""Class used to store all the model-free function classes.

		See the respective files for the formulae.


		The chi-sqared equation
		~~~~~~~~~~~~~~~~~~~~~~~

		File:  chi2_mf.py
		Data structure:  self.data.chi2
		Type:  Double precision floating point value.
		Dependencies:  self.data.ri
		Required by:  None
		Stored:  No


		The chi-sqared gradient
		~~~~~~~~~~~~~~~~~~~~~~~

		File:  dchi2_mf.py
		Data structure:  self.data.dchi2
		Dimension:  1D, (model-free parameters)
		Type:  Numeric array, Float64
		Dependencies:  self.data.ri, self.data.dri
		Required by:  None
		Stored:  No


		The chi-sqared hessian
		~~~~~~~~~~~~~~~~~~~~~~

		File:  d2chi2_mf.py
		Data structure:  self.data.d2chi2
		Dimension:  2D, (model-free parameters, model-free parameters)
		Type:  Numeric array, Float64
		Dependencies:  self.data.ri, self.data.dri, self.data.d2ri
		Required by:  None
		Stored:  No


		The relaxation equations
		~~~~~~~~~~~~~~~~~~~~~~~~

		File:  ri_mf.py
		Data structure:  self.data.ri
		Dimension:  1D, (relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.data.jw
		Required by:  self.data.chi2, self.data.dchi2, self.data.d2chi2
		Stored:  Yes


		The relaxation gradient
		~~~~~~~~~~~~~~~~~~~~~~~

		File:  dri_mf.py
		Data structure:  self.data.dri
		Dimension:  2D, (relaxation data, model-free parameters)
		Type:  Numeric matrix, Float64
		Dependencies:  self.data.ri, self.data.jw, self.data.djw
		Required by:  self.data.dchi2, self.data.d2chi2, self.data.d2ri
		Stored:  Yes


		The relaxation hessian
		~~~~~~~~~~~~~~~~~~~~~~

		File:  d2ri_mf.py
		Data structure:  self.data.d2ri
		Dimension:  3D, (relaxation data, model-free parameters, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  self.data.ri, self.data.dri, self.data.jw, self.data.djw, self.data.d2jw
		Required by:  self.data.d2chi2
		Stored:  Yes


		The spectral density equation
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		File:  jw_mf.py
		Data structure:  self.data.jw
		Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
		Type:  Numeric matrix, Float64
		Dependencies:  None
		Required by:  self.data.ri, self.data.dri, self.data.d2ri
		Stored:  Yes


		The spectral density gradient
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		File:  djw_mf.py
		Data structure:  self.data.djw
		Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  None
		Required by:  self.data.dri, self.data.d2ri
		Stored:  Yes


		The spectral density hessian
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		File:  d2jw_mf.py
		Data structure:  self.data.d2jw
		Dimension:  4D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters, model-free parameters)
		Type:  Numeric 4D matrix, Float64
		Dependencies:  None
		Required by:  self.data.d2ri
		Stored:  Yes

		"""

		self.mf = mf

		# Class containing data.
		self.data = data()


	def init_param_types(self):
		"Initialise arrays with the model-free parameter labels."

		# Relaxation parameter labels.
		if self.data.mf_model == 'm1':
			self.data.ri_param_types = ['mf']
		elif self.data.mf_model == 'm2':
			self.data.ri_param_types = ['mf', 'mf']
		elif self.data.mf_model == 'm3':
			self.data.ri_param_types = ['mf', 'rex']
		elif self.data.mf_model == 'm4':
			self.data.ri_param_types = ['mf', 'mf', 'rex']
		elif self.data.mf_model == 'm5':
			self.data.ri_param_types = ['mf', 'mf', 'mf']
		else:
			raise NameError, "Should not be here."

		# J(w) parameter labels.
		if self.data.mf_model == 'm1':
			self.data.jw_param_types = ['S2']
		elif self.data.mf_model == 'm2':
			self.data.jw_param_types = ['S2', 'te']
		elif self.data.mf_model == 'm3':
			self.data.jw_param_types = ['S2', None]
		elif self.data.mf_model == 'm4':
			self.data.jw_param_types = ['S2', 'te', None]
		elif self.data.mf_model == 'm5':
			self.data.jw_param_types = ['S2f', 'S2s', 'ts']
		else:
			raise NameError, "Should not be here."

