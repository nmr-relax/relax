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
	for k in range(data.num_ri):
		if create_d2ri[k]:
			create_d2ri[k](data, k, data.remap_table[k], get_d2r1)


def calc_d2noe(data, k, frq_num, get_d2r1):
	"""Calculate the second partial derivative of the NOE value.

	Half this code needs to be shifted into the function initialisation code.
	"""

	# Calculate the NOE second derivative.
	for i in range(len(data.params)):
		for j in range(i + 1):
			data.d2r1[i, j, k] = get_d2r1[k](data, k, frq_num, i, j)
			if data.r1[k] == 0.0:
				data.d2ri[i, j, k] = 1e99
			else:
				a = data.ri_prime[k] * (2.0 * data.dr1[i, k] * data.dr1[j, k] - data.r1[k] * data.d2r1[i, j, k])
				b = data.r1[k] * (data.dri_prime[i, k] * data.dr1[j, k] + data.dr1[i, k] * data.dri_prime[j, k] - data.r1[k] * data.d2ri_prime[i, j, k])
				# Old buggy code!
				#b = data.r1[k] * (data.dri_prime[i, k] * data.dr1[j, k] + data.dr1[j, k] * data.dri_prime[i, k] - data.r1[k] * data.d2ri_prime[i, j, k])
				data.d2ri[i, j, k] = data.g_ratio * (1.0 / data.r1[k]**3) * (a - b)

			# Make the hessian symmetric.
			if i != j:
				data.d2r1[j, i, k] = data.d2r1[i, j, k]
				data.d2ri[j, i, k] = data.d2ri[i, j, k]


def extract_d2r1(data, k, frq_num, i, j):
	"Get the dR1 value from data.dri_prime"

	return data.d2ri_prime[i, j, data.noe_r1_table[k]]
