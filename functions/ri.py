from Numeric import copy


def calc_ri(data, ri_funcs):
	"""An additional layer of equations to simplify the relaxation equations, gradients, and hessians.

	The R1 and R2 equations are left alone, while the NOE is calculated from the R1 and sigma_noe values.


	The relaxation equations
	~~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  data.ri
	Dimension:  1D, (relaxation data)
	Type:  Numeric array, Float64
	Dependencies:  data.ri_prime
	Required by:  data.chi2, data.dchi2, data.d2chi2


	Formulae
	~~~~~~~~

		R1()  =  R1'()


		R2()  =  R2'()

		               gH   sigma_noe()
		NOE()  =  1 +  -- . -----------
		               gN      R1()

	"""

	# Calculate the NOE values.
	for i in range(data.num_ri):
		if ri_funcs[i]:
			ri_funcs[i](data, i, data.remap_table[i])


def calc_noe(data, i, frq_num):
	"Calculate the NOE value."

	# Get the r1 value either from data.ri_prime or by calculation if the value is not in data.ri_prime
	if data.noe_r1_table[i] == None:
		r1 = calc_r1(data, frq_num)
	else:
		r1 = data.ri_prime[data.noe_r1_table[i]]

	# Calculate the NOE.
	if r1 == 0.0:
		data.ri[i] = 1e99
	else:
		data.ri[i] = 1.0 + data.g_ratio*(data.ri_prime[i] / r1)


def calc_r1(data, frq_num):
	"""Calculate the R1 value if there is no R1 data corresponding to the NOE data.

	R1()  =  d . J_R1_d  +  c . J_R1_c

	J_R1_d  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

	J_R1_c  =  J(wN)

	"""

	dip_comp = data.dipole_const
	j_dip_comp = data.jw[frq_num, 2] + 3.0*data.jw[frq_num, 1] + 6.0*data.jw[frq_num, 4]
	csa_comp = data.csa_const[frq_num]
	j_csa_comp = data.jw[frq_num, 1]
	return dip_comp * j_dip_comp + csa_comp * j_csa_comp
