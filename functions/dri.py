from ri import calc_r1


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


def calc_dnoe(data, i, frq_num, get_dr1):
	"""Calculate the derivative of the NOE value.

	Half this code needs to be shifted into the function initialisation code.
	"""

	# Calculate the NOE derivative.
	for k in range(len(data.params)):
		data.dr1[i, k] = get_dr1[i](data, i, frq_num, k)
		if data.r1[i] == 0.0:
			data.dri[i, k] = 1e99
		else:
			data.dri[i, k] = data.g_ratio * (1.0 / data.r1[i]**2) * (data.r1[i] * data.dri_prime[i, k] - data.ri_prime[i] * data.dr1[i, k])


def calc_dr1(data, i, frq_num, k):
	"""Calculate the R1 value if there is no R1 data corresponding to the NOE data.

	"""

	raise NameError, "Incomplete code, need to calculate the dr1 value!"


def extract_dr1(data, i, frq_num, k):
	"Get the dR1 value from data.dri_prime"

	return data.dri_prime[data.noe_r1_table[i], k]
