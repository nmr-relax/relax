from chi2_mf import chi2
from dchi2_mf import dchi2
from jw_mf import Jw
from djw_mf import dJw
from ri_mf import Ri
from dri_mf import dRi


class mf_functions:
	def __init__(self, mf):
		"""Class used to store all the model-free function classes.

		The following functions are currently implemented:
			Calculation of the chi-sqared value.
			Calculation of the chi-sqared gradient array.

			Calculation of the relaxation array.
			Calculation of the relaxation gradient matrix.

			Calculation of the spectral density matrix.
			Calculation of the spectral density gradient 3D matrix.

		For details of the formulae, see the respective files.


		The chi-sqared value
		~~~~~~~~~~~~~~~~~~~~

		File:  chi2_mf.py
		Data structure:  self.chi2
		Type:  Single double precision floating point value.
		Dependencies:  self.ri, self.jw
		Required by:  None
		Stored:  No


		The chi-sqared gradient array
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		File:  dchi2_mf.py
		Data structure:  self.dchi2
		Dimension:  1D, (model-free parameters)
		Type:  Numeric array, Float64
		Dependencies:  self.ri, self.jw, self.dri, self.djw
		Required by:  None
		Stored:  No


		The relaxation array
		~~~~~~~~~~~~~~~~~~~~

		File:  ri_mf.py
		Data structure:  self.ri
		Dimension:  1D, (relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.jw
		Required by:  self.chi2, self.dchi2
		Stored:  Yes


		The relaxation gradient matrix
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		File:  dri_mf.py
		Data structure:  self.dri
		Dimension:  2D, (relaxation data, model-free parameters)
		Type:  Numeric matrix, Float64
		Dependencies:  self.ri, self.jw, self.djw
		Required by:  self.dchi2
		Stored:  Yes


		The spectral density matrix
		~~~~~~~~~~~~~~~~~~~~~~~~~~~

		File:  jw_mf.py
		Data structure:  self.jw
		Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
		Type:  Numeric matrix, Float64
		Dependencies:  None
		Required by:  self.ri, self.dri
		Stored:  Yes


		The spectral density gradient 3D matrix
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		File:  djw_mf.py
		Data structure:  self.djw
		Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters)
		Type:  Numeric 3D matrix, Float64
		Dependencies:  None
		Required by:  self.dri
		Stored:  Yes

		"""

		self.mf = mf
		self.chi2 = chi2(self.mf)
		self.dchi2 = dchi2(self.mf)
		self.Jw = Jw(self.mf)
		self.dJw = dJw(self.mf)
		self.Ri = Ri(self.mf)
		self.dRi = dRi(self.mf)
