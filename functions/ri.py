from Numeric import array

from data import data
from ri_prime import func_ri_prime
data_class = data


def ri(data, create_ri, get_r1):
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
		if create_ri[i]:
			create_ri[i](data, i, data.remap_table[i], get_r1)


def calc_noe(data, i, frq_num, get_r1):
	"""Calculate the NOE value.

	Half this code needs to be shifted into the function initialisation code.
	"""

	# Get the r1 value either from data.ri_prime or by calculation if the value is not in data.ri_prime
	data.r1[i] = get_r1[i](data, i, frq_num)

	# Calculate the NOE.
	if data.r1[i] == 0.0:
		data.ri[i] = 1e99
	else:
		data.ri[i] = 1.0 + data.g_ratio*(data.ri_prime[i] / data.r1[i])


def calc_r1(data, i, frq_num):
	"""Calculate the R1 value if there is no R1 data corresponding to the NOE data.

	R1()  =  d . J_R1_d  +  c . J_R1_c

	J_R1_d  =  J(wH-wN) + 3J(wN) + 6J(wH+wN)

	J_R1_c  =  J(wN)

	"""

	temp_data = data_class()
	temp_data.dipole_const = data.dipole_const
	temp_data.csa_const = data.csa_const
	temp_data.jw = data.jw
	temp_data.dip_comps = array([0.0])
	temp_data.dip_jw_comps = array([0.0])
	temp_data.csa_comps = array([0.0])
	temp_data.csa_jw_comps = array([0.0])

	comp_r1_prime(temp_data, 0, frq_num)
	func_ri_prime(temp_data)

	return temp_data.ri_prime[0]


def extract_r1(data, i, frq_num):
	"Get the R1 value from data.ri_prime"

	return data.ri_prime[data.noe_r1_table[i]]
