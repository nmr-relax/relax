from math import pi
from Numeric import Float64, zeros
from re import match


def calc_ri_prime(data, ri_funcs):
	"""Function for back calculation of the transformed relaxation values R1, R2, and sigma_noe.

	The transformed relaxation equations
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  self.data.ri_prime
	Dimension:  1D, (transformed relaxation data)
	Type:  Numeric array, Float64
	Dependencies:  self.data.jw
	Required by:  self.data.ri, self.data.dri, self.data.d2ri


	Formulae
	~~~~~~~~

	Components
	~~~~~~~~~~
		      1   / mu0  \ 2  (gH.gN.h_bar)**2
		d  =  - . | ---- |  . ----------------
		      4   \ 4.pi /         <r**6>

		      (wN.csa)**2
		c  =  -----------
		           3

		J_R1_d  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

		J_R1_c  =  J(wN)

		J_R2_d  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

		J_R2_c  =  4J(0) + 3J(wN)

		J_sigma_noe  =  6J(wH+wN) - J(wH-wN)


	Relaxation equations
	~~~~~~~~~~~~~~~~~~~~

		R1()  =  d . J_R1_d  +  c . J_R1_c


		         d              c
		R2()  =  - . J_R2_d  +  - . J_R2_c  +  Rex
		         2              6


		sigma_noe()  =  d . J_sigma_noe

	"""

	# Calculate the components of the transformed relaxation equations.
	for i in range(data.num_ri):
		frq_num = data.remap_table[i]
		ri_funcs[i](data, i, frq_num)

	# Calculate the transformed relaxation values.
	data.ri_prime = data.dip_comps * data.j_dip_comps + data.csa_comps * data.j_csa_comps + data.rex_comps


def calc_r1_prime(data, i, frq_num):
	data.dip_comps[i] = data.dipole_const
	data.j_dip_comps[i] = data.jw[frq_num, 2] + 3.0*data.jw[frq_num, 1] + 6.0*data.jw[frq_num, 4]
	data.csa_comps[i] = data.csa_const[frq_num]
	data.j_csa_comps[i] = data.jw[frq_num, 1]


def calc_r2_prime(data, i, frq_num):
	data.dip_comps[i] = data.dipole_const / 2.0
	data.j_dip_comps[i] = 4.0*data.jw[frq_num, 0] + data.jw[frq_num, 2] + 3.0*data.jw[frq_num, 1] + 6.0*data.jw[frq_num, 3] + 6.0*data.jw[frq_num, 4]
	data.csa_comps[i] = data.csa_const[frq_num] / 6.0
	data.j_csa_comps[i] = 4.0*data.jw[frq_num, 0] + 3.0*data.jw[frq_num, 1]


def calc_r2_rex_prime(data, i, frq_num):
	data.dip_comps[i] = data.dipole_const / 2.0
	data.j_dip_comps[i] = 4.0*data.jw[frq_num, 0] + data.jw[frq_num, 2] + 3.0*data.jw[frq_num, 1] + 6.0*data.jw[frq_num, 3] + 6.0*data.jw[frq_num, 4]
	data.csa_comps[i] = data.csa_const[frq_num] / 6.0
	data.j_csa_comps[i] = 4.0*data.jw[frq_num, 0] + 3.0*data.jw[frq_num, 1]
	data.rex_comps[i] = data.params[1] * (1e-8 * data.frq[frq_num])**2


def calc_sigma_noe(data, i, frq_num):
	data.dip_comps[i] = data.dipole_const
	data.j_dip_comps[i] = 6.0*data.jw[frq_num, 4] - data.jw[frq_num, 2]


def calc_ri_constants(data):
	"""Calculate the dipolar and CSA constants.

	Dipolar constants
	~~~~~~~~~~~~~~~~~
		      1   / mu0  \ 2  (gH.gN.h_bar)**2
		d  =  - . | ---- |  . ----------------
		      4   \ 4.pi /         <r**6>


		         3   / mu0  \ 2  (gH.gN.h_bar)**2
		d'  =  - - . | ---- |  . ----------------
		         2   \ 4.pi /         <r**7>


		       21   / mu0  \ 2  (gH.gN.h_bar)**2
		d"  =  -- . | ---- |  . ----------------
		       2    \ 4.pi /         <r**8>


	CSA constants
	~~~~~~~~~~~~~
		      (wN.csa)**2
		c  =  -----------
		           3


		       2.wN**2.csa
		c'  =  -----------
		            3


		       2.wN**2
		c"  =  -------
		          3

	"""

	# Dipolar constants.
	data.dip_temp = ((data.mu0 / (4.0*pi)) * data.h_bar * data.gh * data.gx) ** 2
	data.dipole_const = 0.25 * data.dip_temp * data.bond_length**-6
	data.dipole_prime = -1.5 * data.dip_temp * data.bond_length**-7
	data.dipole_2prime = 10.5 * data.dip_temp * data.bond_length**-8

	# CSA constants.
	data.csa_const = zeros(data.num_frq, Float64)
	data.csa_prime = zeros(data.num_frq, Float64)
	data.csa_2prime = zeros(data.num_frq, Float64)
	data.csa_temp = []
	for i in range(data.num_frq):
		data.csa_temp.append(data.frq_sqrd_list[i, 1] / 3.0)
		data.csa_const[i] = data.csa_temp[i] * data.csa**2
		data.csa_prime[i] = 2.0 * data.csa_temp[i] * data.csa
		data.csa_2prime[i] = 2.0 * data.csa_temp[i]
