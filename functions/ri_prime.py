def ri_prime(data, create_ri_prime_comps, create_ri_prime):
	"""Function for back calculation of the transformed relaxation values R1, R2, and sigma_noe.

	The transformed relaxation equations
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  data.ri_prime
	Dimension:  1D, (transformed relaxation data)
	Type:  Numeric array, Float64
	Dependencies:  data.jw
	Required by:  data.ri, data.dri, data.d2ri


	Formulae
	~~~~~~~~

	Components
	~~~~~~~~~~
		                   1   / mu0  \ 2  (gH.gN.h_bar)**2
		dip_const_func  =  - . | ---- |  . ----------------
		                   4   \ 4.pi /         <r**6>

		                   (wN.csa)**2
		csa_const_func  =  -----------
		                        3

		dip_Jw_R1_func  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

		csa_Jw_R1_func  =  J(wN)

		dip_Jw_R2_func  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

		csa_Jw_R2_func  =  4J(0) + 3J(wN)

		dip_Jw_sigma_noe_func  =  6J(wH+wN) - J(wH-wN)


	Relaxation equations
	~~~~~~~~~~~~~~~~~~~~

		R1()  =  dip_const_func . dip_Jw_R1_func  +  csa_const_func . csa_Jw_R1_func


		         dip_const_func                      csa_const_func
		R2()  =  -------------- . dip_Jw_R2_func  +  -------------- . csa_Jw_R2_func  +  Rex
		               2                                   6


		sigma_noe()  =  dip_const_func . dip_Jw_sigma_noe_func

	"""

	# Calculate the components of the transformed relaxation equations.
	for i in range(data.num_ri):
		create_ri_prime_comps[i](data, i, data.remap_table[i])

	# Calculate the transformed relaxation values.
	create_ri_prime(data)


def comp_r1_prime(data, i, frq_num):
	"""Calculate the r1 components.

	R1()  =  dip_const_func . dip_Jw_R1_func  +  csa_const_func . csa_Jw_R1_func

	dip_Jw_R1_func  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

	csa_Jw_R1_func  =  J(wN)

	"""
	data.dip_comps[i] = data.dipole_const
	data.dip_jw_comps[i] = data.jw[frq_num, 2] + 3.0*data.jw[frq_num, 1] + 6.0*data.jw[frq_num, 4]
	data.csa_comps[i] = data.csa_const[frq_num]
	data.csa_jw_comps[i] = data.jw[frq_num, 1]


def comp_r2_prime(data, i, frq_num):
	"""Calculate the r2 components.

	         dip_const_func                      csa_const_func
	R2()  =  -------------- . dip_Jw_R2_func  +  -------------- . csa_Jw_R2_func
	               2                                   6

	dip_Jw_R2_func  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

	csa_Jw_R2_func  =  4J(0) + 3J(wN)

	"""

	data.dip_comps[i] = data.dipole_const / 2.0
	data.dip_jw_comps[i] = 4.0*data.jw[frq_num, 0] + data.jw[frq_num, 2] + 3.0*data.jw[frq_num, 1] + 6.0*data.jw[frq_num, 3] + 6.0*data.jw[frq_num, 4]
	data.csa_comps[i] = data.csa_const[frq_num] / 6.0
	data.csa_jw_comps[i] = 4.0*data.jw[frq_num, 0] + 3.0*data.jw[frq_num, 1]


def comp_r2_prime_rex(data, i, frq_num):
	"""Calculate the r2 components including chemical exchange.

	         dip_const_func                      csa_const_func
	R2()  =  -------------- . dip_Jw_R2_func  +  -------------- . csa_Jw_R2_func  +  Rex
	               2                                   6

	dip_Jw_R2_func  =  4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)

	csa_Jw_R2_func  =  4J(0) + 3J(wN)

	"""

	data.dip_comps[i] = data.dipole_const / 2.0
	data.dip_jw_comps[i] = 4.0*data.jw[frq_num, 0] + data.jw[frq_num, 2] + 3.0*data.jw[frq_num, 1] + 6.0*data.jw[frq_num, 3] + 6.0*data.jw[frq_num, 4]
	data.csa_comps[i] = data.csa_const[frq_num] / 6.0
	data.csa_jw_comps[i] = 4.0*data.jw[frq_num, 0] + 3.0*data.jw[frq_num, 1]
	data.rex_comps[i] = data.params[data.rex_index] * (1e-8 * data.frq[frq_num])**2


def comp_sigma_noe(data, i, frq_num):
	"""Calculate the sigma_noe components.

	sigma_noe()  =  dip_const_func . dip_Jw_sigma_noe_func

	dip_Jw_sigma_noe_func  =  6J(wH+wN) - J(wH-wN)

	"""

	data.dip_comps[i] = data.dipole_const
	data.dip_jw_comps[i] = 6.0*data.jw[frq_num, 4] - data.jw[frq_num, 2]


def func_ri_prime(data):
	"Calculate the transformed relaxation values."

	data.ri_prime = data.dip_comps * data.dip_jw_comps + data.csa_comps * data.csa_jw_comps


def func_ri_prime_rex(data):
	"Calculate the transformed relaxation values."

	data.ri_prime = data.dip_comps * data.dip_jw_comps + data.csa_comps * data.csa_jw_comps + data.rex_comps
