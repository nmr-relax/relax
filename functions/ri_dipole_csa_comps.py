from math import pi
from Numeric import Float64, zeros
from re import match


def calc_fixed_csa(data):
	"""Calculate the fixed component of the CSA constants.

	            wN**2
	c_fixed  =  -----
	              3

	"""

	data.csa_fixed = zeros(data.num_frq, Float64)
	for i in range(data.num_frq):
		data.csa_fixed[i] = data.frq_sqrd_list[i, 1] / 3.0


def calc_fixed_dip(data):
	"""Calculate the fixed component of the dipolar constant.

	            1   / mu0  \ 2
	d_fixed  =  - . | ---- |  . (gH.gN.h_bar)**2
	            4   \ 4.pi /

	"""

	data.dip_fixed = ((data.mu0 / (4.0*pi)) * data.h_bar * data.gh * data.gx) ** 2


def comp_csa_const_func(data):
	"""Calculate the CSA constant.

	CSA constant
	~~~~~~~~~~~~

		      (wN.csa)**2
		c  =  -----------
		           3

	"""

	data.csa_const = data.csa_fixed * data.csa**2


def comp_csa_const_grad(data):
	"""Calculate the derivative of the CSA constant.

	CSA constant prime
	~~~~~~~~~~~~~~~~~~

		       2.wN**2.csa
		c'  =  -----------
		            3

	"""

	data.csa_prime = 2.0 * data.csa_fixed * data.csa


def comp_csa_const_hess(data):
	"""Calculate the second derivative of the CSA constant.

	CSA constant double prime
	~~~~~~~~~~~~~~~~~~~~~~~~~

		       2.wN**2
		c"  =  -------
		          3

	"""

	data.csa_2prime = 2.0 * data.csa_fixed


def comp_dip_const_func(data):
	"""Calculate the dipolar constant.

	Dipolar constant
	~~~~~~~~~~~~~~~~

		      1   / mu0  \ 2  (gH.gN.h_bar)**2
		d  =  - . | ---- |  . ----------------
		      4   \ 4.pi /         <r**6>

	"""

	data.dipole_const = 0.25 * data.dip_fixed * data.bond_length**-6


def comp_dip_const_grad(data):
	"""Calculate the derivative of the dipolar constant.

	Dipolar constant prime
	~~~~~~~~~~~~~~~~~~~~~~

		         3   / mu0  \ 2  (gH.gN.h_bar)**2
		d'  =  - - . | ---- |  . ----------------
		         2   \ 4.pi /         <r**7>

	"""

	return -1.5 * data.dip_fixed * data.bond_length**-7


def comp_dip_const_hess(data):
	"""Calculate the second derivative of the dipolar constant.

	Dipolar constant hessian
	~~~~~~~~~~~~~~~~~~~~~~~~

		       21   / mu0  \ 2  (gH.gN.h_bar)**2
		d"  =  -- . | ---- |  . ----------------
		       2    \ 4.pi /         <r**8>

	"""

	return 10.5 * data.dip_fixed * data.bond_length**-8
