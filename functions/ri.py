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


def dri(data, create_dri, get_dr1):
	"""An additional layer of equations to simplify the relaxation equations, gradients, and hessians.

	The R1 and R2 equations are left alone, while the NOE is decomposed into the cross relaxation rate equation and the R1 equation.


	The relaxation gradients
	~~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  data.dri
	Dimension:  2D, (parameters, relaxation data)
	Type:  Numeric array, Float64
	Dependencies:  data.ri_prime, data.dri_prime
	Required by:  data.dchi2, data.d2chi2


	Formulae
	~~~~~~~~

		 dR1()       dR1'()
		-------  =  -------
		dthetaj     dthetaj


		 dR2()       dR2'()
		-------  =  -------
		dthetaj     dthetaj


		 dNOE()     gH      1      /        dsigma_noe()                    dR1()  \ 
		-------  =  -- . ------- . | R1() . ------------  -  sigma_noe() . ------- |
		dthetaj     gN   R1()**2   \          dthetaj                      dthetaj /


	"""

	# Loop over the relaxation values and modify the NOE gradients.
	for i in range(data.num_ri):
		if create_dri[i]:
			create_dri[i](data, i, data.remap_table[i], get_dr1)


def d2ri(data, create_d2ri, get_d2r1):
	"""An additional layer of equations to simplify the relaxation equations, gradients, and hessians.

	The R1 and R2 equations are left alone, while the NOE is decomposed into the cross relaxation rate equation and the R1 equation.


	The relaxation hessians
	~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  data.d2ri
	Dimension:  3D, (parameters, parameters, relaxation data)
	Type:  Numeric array, Float64
	Dependencies:  data.ri_prime, data.dri_prime, data.d2ri_prime
	Required by:  data.d2chi2


	Formulae
	~~~~~~~~

		     d2R1()             d2R1'()
		---------------  =  ---------------
		dthetai.dthetaj     dthetai.dthetaj


		     d2R2()             d2R2'()
		---------------  =  ---------------
		dthetai.dthetaj     dthetai.dthetaj


		    d2NOE()         gH      1      /               /      dR1()     dR1()                  d2R1()     \ 
		---------------  =  -- . ------- . | sigma_noe() . | 2 . ------- . -------  -  R1() . --------------- |
		dthetai.dthetaj     gN   R1()**3   \               \     dthetai   dthetaj            dthetai.dthetaj /

			          / dsigma_noe()    dR1()       dR1()    dsigma_noe()             d2sigma_noe()  \ \ 
			-  R1() . | ------------ . -------  +  ------- . ------------  -  R1() . --------------- | |
			          \   dthetai      dthetaj     dthetai     dthetaj               dthetai.dthetaj / /
	"""

	# Loop over the relaxation values and modify the NOE hessians.
	for i in range(data.num_ri):
		if create_d2ri[i]:
			create_d2ri[i](data, i, data.remap_table[i], get_d2r1)



# Calculate the NOE value.
##########################

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


def calc_dnoe(data, i, frq_num, get_dr1):
	"""Calculate the derivative of the NOE value.

	Half this code needs to be shifted into the function initialisation code.
	"""

	# Calculate the NOE derivative.
	data.dr1[i] = get_dr1[i](data, i, frq_num)
	if data.r1[i] == 0.0:
		data.dri[i] = 1e99
	else:
		data.dri[i] = data.g_ratio * (1.0 / data.r1[i]**2) * (data.r1[i] * data.dri_prime[i] - data.ri_prime[i] * data.dr1[i])


def calc_d2noe(data, i, frq_num, get_d2r1):
	"""Calculate the second partial derivative of the NOE value.

	Half this code needs to be shifted into the function initialisation code.
	"""

	# Calculate the NOE second derivative.
	data.d2r1[i] = get_d2r1[i](data, i, frq_num)
	if data.r1[i] == 0.0:
		data.d2ri[i] = 1e99
	else:
		for j in range(len(data.params)):
			a = data.ri_prime[i] * (2.0 * data.dr1[i, j] * data.dr1[i] - data.r1[i] * data.d2r1[i, j])
			b = data.r1[i] * (data.dri_prime[i, j] * data.dr1[i] + data.dr1[i, j] * data.dri_prime[i] - data.r1[i] * data.d2ri_prime[i, j])
			data.d2ri[i, j] = data.g_ratio * (1.0 / data.r1[i]**3) * (a - b)



# Calculate the R1 value.
#########################

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


def calc_dr1(data, i, frq_num):
	"""Calculate the R1 value if there is no R1 data corresponding to the NOE data.

	"""

	raise NameError, "Incomplete code, need to calculate the dr1 value!"


def calc_d2r1(data, k, frq_num):
	"""Calculate the R1 value if there is no R1 data corresponding to the NOE data.

	"""

	raise NameError, "Incomplete code, need to calculate the d2r1 value!"



# Extract the R1 value.
#######################

def extract_r1(data, i, frq_num):
	"Get the R1 value from data.ri_prime"

	return data.ri_prime[data.noe_r1_table[i]]


def extract_dr1(data, i, frq_num):
	"Get the dR1 value from data.dri_prime"

	return data.dri_prime[data.noe_r1_table[i]]


def extract_d2r1(data, i, frq_num):
	"Get the d2R1 value from data.d2ri_prime"

	return data.d2ri_prime[data.noe_r1_table[i]]
