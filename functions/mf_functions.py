from chi2_mf import chi2
from dchi2_mf import dchi2
from d2chi2_mf import d2chi2

from jw_mf import Jw
from djw_mf import dJw
from d2jw_mf import d2Jw

from ri_mf import Ri
from dri_mf import dRi
from d2ri_mf import d2Ri


class mf_functions:
	def __init__(self, mf):
		"""Class used to store all the model-free function classes.

		See the respective files for the formulae.


		The chi-sqared equation
		~~~~~~~~~~~~~~~~~~~~~~~

		File:  chi2_mf.py
		Data structure:  self.chi2
		Type:  Double precision floating point value.
		Dependencies:  self.ri
		Required by:  None
		Stored:  No


		The chi-sqared gradient
		~~~~~~~~~~~~~~~~~~~~~~~

		File:  dchi2_mf.py
		Data structure:  self.dchi2
		Dimension:  1D, (model-free parameters)
		Type:  Numeric array, Float64
		Dependencies:  self.ri, self.dri
		Required by:  None
		Stored:  No


		The chi-sqared hessian
		~~~~~~~~~~~~~~~~~~~~~~

		File:  d2chi2_mf.py
		Data structure:  self.d2chi2
		Dimension:  2D, (model-free parameters, model-free parameters)
		Type:  Numeric array, Float64
		Dependencies:  self.ri, self.dri, self.d2ri
		Required by:  None
		Stored:  No


		The relaxation equations
		~~~~~~~~~~~~~~~~~~~~~~~~

		File:  ri_mf.py
		Data structure:  self.ri
		Dimension:  1D, (relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.jw
		Required by:  self.chi2, self.dchi2, self.d2chi2
		Stored:  Yes


		The relaxation gradient
		~~~~~~~~~~~~~~~~~~~~~~~

		File:  dri_mf.py
		Data structure:  self.dri
		Dimension:  2D, (relaxation data, model-free parameters)
		Type:  Numeric matrix, Float64
		Dependencies:  self.ri, self.jw, self.djw
		Required by:  self.dchi2, self.d2chi2, self.d2ri
		Stored:  Yes


		The relaxation hessian
		~~~~~~~~~~~~~~~~~~~~~~

		File:  d2ri_mf.py
		Data structure:  self.d2ri
		Dimension:  3D, (relaxation data, model-free parameters, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  self.ri, self.dri, self.jw, self.djw, self.d2jw
		Required by:  self.d2chi2
		Stored:  Yes


		The spectral density equation
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		File:  jw_mf.py
		Data structure:  self.jw
		Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
		Type:  Numeric matrix, Float64
		Dependencies:  None
		Required by:  self.ri, self.dri, self.d2ri
		Stored:  Yes


		The spectral density gradient
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		File:  djw_mf.py
		Data structure:  self.djw
		Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  None
		Required by:  self.dri, self.d2ri
		Stored:  Yes


		The spectral density hessian
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		File:  d2jw_mf.py
		Data structure:  self.d2jw
		Dimension:  4D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters, model-free parameters)
		Type:  Numeric 4D matrix, Float64
		Dependencies:  None
		Required by:  self.d2ri
		Stored:  Yes

		"""

		self.mf = mf

		# Class containing data.
		self.data = data()

		self.chi2 = chi2(self.mf)
		self.dchi2 = dchi2(self.mf)
		self.d2chi2 = d2chi2(self.mf)

		self.Jw = Jw(self.mf)
		self.dJw = dJw(self.mf)
		self.d2Jw = d2Jw(self.mf)

		self.Ri = Ri(self.mf)
		self.dRi = dRi(self.mf)
		self.d2Ri = d2Ri(self.mf)


class data:
	def __init__(self):
		print "data"
