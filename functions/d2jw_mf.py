from Numeric import Float64, zeros

def create_d2jw_struct(data, calc_d2jw):
	"""Function to create model-free spectral density hessians.

	The spectral density hessians
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  data.d2jw
	Dimension:  4D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters, model-free parameters)
	Type:  Numeric 4D matrix, Float64
	Dependencies:  None
	Required by:  data.d2ri


	Formulae
	~~~~~~~~

	Original:  Model-free parameter - Model-free parameter
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		d2J(w)
		------  =  0
		dS2**2


		 d2J(w)       2     1 - (w.te')**2      /   tm    \ 2
		-------  =  - - . ------------------- . | ------- |
		dS2.dte       5   (1 + (w.te')**2)**2   \ te + tm /


		d2J(w)       4              /   tm    \ 4           1            
		------  =  - - . (1 - S2) . | ------- |  . ------------------- . [w**2.te'(3 - (w.te')**2) + (1 - (w.te')**4)(te + tm).tm**-2]
		dte**2       5              \ te + tm /    (1 + (w.te')**2)**3   


	Original:  Other parameters
	~~~~~~~~~~~~~~~~~~~~~~~~~~~

		 d2J(w)               d2J(w)              d2J(w)
		--------  =  0   ,   --------  =  0   ,   ------  =  0
		dS2.dRex             dS2.dcsa             dS2.dr


		 d2J(w)              d2J(w)               d2J(w)
		--------  =  0   ,  --------  =  0   ,    ------  =  0
		dte.dRex            dte.dcsa              dte.dr


		 d2J(w)              d2J(w)                d2J(w)
		-------  =  0   ,  ---------  =  0   ,    -------  =  0
		dRex**2            dRex.dcsa              dRex.dr


		 d2J(w)             d2J(w)
		-------  =  0   ,  -------  =  0
		dcsa**2            dcsa.dr


		d2J(w)
		------  =  0
		dr**2


	Extended:  Model-free parameter - Model-free parameter
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		 d2J(w)
		-------  =  0
		dS2f**2


		  d2J(w)      2 /      tm                 ts'      \ 
		---------  =  - | -------------  -  -------------- |
		dS2f.dS2s     5 \ 1 + (w.tm)**2     1 + (w.ts')**2 /


		 d2J(w)        2     1 - (w.tf')**2      /   tm    \ 2
		--------  =  - - . ------------------- . | ------- |
		dS2f.dtf       5   (1 + (w.tf')**2)**2   \ tf + tm /


		 d2J(w)      2                 1 - (w.ts')**2      /   tm    \ 2
		--------  =  - . (1 - S2s) . ------------------- . | ------- |
		dS2f.dts     5               (1 + (w.ts')**2)**2   \ ts + tm /


		 d2J(w)              d2J(w)
		-------  =  0   ,   --------  =  0
		dS2s**2             dS2s.dtf


		 d2J(w)        2.S2f     1 - (w.ts')**2      /   tm    \ 2
		--------  =  - ----- . ------------------- . | ------- |
		dS2s.dts         5     (1 + (w.ts')**2)**2   \ ts + tm /


		 d2J(w)
		-------  =  0
		dtf.dts


		d2J(w)       4               /   tm    \ 4           1            
		------  =  - - . (1 - S2f) . | ------- |  . ------------------- . [w**2.tf'(3 - (w.tf')**2) + (1 - (w.tf')**4)(tf + tm).tm**-2]
		dtf**2       5               \ tf + tm /    (1 + (w.tf')**2)**3   


		d2J(w)       4                /   tm    \ 4           1            
		------  =  - - . (S2f - S2) . | ------- |  . ------------------- . [w**2.ts'(3 - (w.ts')**2) + (1 - (w.ts')**4)(ts + tm).tm**-2]
		dts**2       5                \ ts + tm /    (1 + (w.ts')**2)**3   


	Extended:  Other parameters
	~~~~~~~~~~~~~~~~~~~~~~~~~~~

		  d2J(w)                d2J(w)               d2J(w)
		---------  =  0   ,   ---------  =  0   ,   -------  =  0
		dS2f.dRex             dS2f.dcsa             dS2f.dr


		  d2J(w)                d2J(w)               d2J(w)
		---------  =  0   ,   ---------  =  0   ,   -------  =  0
		dS2s.dRex             dS2s.dcsa             dS2s.dr


		 d2J(w)               d2J(w)              d2J(w)
		--------  =  0   ,   --------  =  0   ,   ------  =  0
		dtf.dRex             dtf.dcsa             dtf.dr


		 d2J(w)               d2J(w)              d2J(w)
		--------  =  0   ,   --------  =  0   ,   ------  =  0
		dts.dRex             dts.dcsa             dts.dr


		 d2J(w)               d2J(w)               d2J(w)
		-------  =  0   ,   ---------  =  0   ,   -------  =  0
		dRex**2             dRex.dcsa             dRex.dr


		 d2J(w)              d2J(w)
		-------  =  0   ,   -------  =  0
		dcsa**2             dcsa.dr


		d2J(w)
		------  =  0
		dr**2



	"""

	for i in range(data.num_frq):
		for j in range(len(data.params)):
			for k in range(j + 1):
				if calc_d2jw[j][k]:
					data.d2jw[i, 0, j, k] = calc_d2jw[j][k](i, 0, data)
					data.d2jw[i, 1, j, k] = calc_d2jw[j][k](i, 1, data)
					data.d2jw[i, 2, j, k] = calc_d2jw[j][k](i, 2, data)
					data.d2jw[i, 3, j, k] = calc_d2jw[j][k](i, 3, data)
					data.d2jw[i, 4, j, k] = calc_d2jw[j][k](i, 4, data)

					# Make the hessian symmetric.
					if j != k:
						data.d2jw[i, 0, k, j] = data.d2jw[i, 0, j, k]
						data.d2jw[i, 1, k, j] = data.d2jw[i, 1, j, k]
						data.d2jw[i, 2, k, j] = data.d2jw[i, 2, j, k]
						data.d2jw[i, 3, k, j] = data.d2jw[i, 3, j, k]
						data.d2jw[i, 4, k, j] = data.d2jw[i, 4, j, k]




# Original model-free equations with parameters S2, te.
#######################################################

def calc_iso_S2_te_d2jw_dS2dte(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the S2/te double partial derivative of the original model-free formula with the parameters S2 and te.

	The formula is:

		 d2J(w)       2     1 - (w.te')**2      /   tm    \ 2
		-------  =  - - . ------------------- . | ------- |
		dS2.dte       5   (1 + (w.te')**2)**2   \ te + tm /

	"""

	return -0.4 * (1.0 - data.omega_te_prime_sqrd[i, frq_index]) / ((1.0 + data.omega_te_prime_sqrd[i, frq_index])**2) * data.fact_a**2


def calc_iso_S2_te_d2jw_dte2(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the te/te double partial derivative of the original model-free formula with the parameters S2 and te.

	The formula is:

		d2J(w)       4              /   tm    \ 4           1            
		------  =  - - . (1 - S2) . | ------- |  . ------------------- . [w**2.te'(3 - (w.te')**2) + (1 - (w.te')**4)(te + tm).tm**-2]
		dte**2       5              \ te + tm /    (1 + (w.te')**2)**3   

	"""

	a = 1.0 / ((1.0 + data.omega_te_prime_sqrd[i, frq_index])**3)
	b = data.frq_sqrd_list[i][frq_index] * data.te_prime * (3.0 - data.omega_te_prime_sqrd[i, frq_index])
	c = (1.0 - data.omega_te_prime_sqrd[i, frq_index]**2) * (data.params[data.te_index] + data.diff_params[0]) * data.diff_params[0]**-2

	return -0.8 * (1.0 - data.params[data.s2_index]) * data.fact_a**4 * a * (b + c)



# Extended model-free equations with parameters S2f, S2s, ts.
#############################################################

def calc_iso_S2f_S2s_ts_d2jw_dS2fdS2s(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the S2f/S2s double partial derivative of the extended model-free formula with the parameters S2f, S2s, and ts.

	The formula is:

		  d2J(w)      2 /      tm                 ts'      \ 
		---------  =  - | -------------  -  -------------- |
		dS2f.dS2s     5 \ 1 + (w.tm)**2     1 + (w.ts')**2 /

	"""

	return 0.4 * (data.diff_params[0] / (1.0 + data.omega_tm_sqrd[i, frq_index]) - data.ts_prime / (1.0 + data.omega_ts_prime_sqrd[i, frq_index]))


def calc_iso_S2f_S2s_ts_d2jw_dS2fdts(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the S2f/ts double partial derivative of the extended model-free formula with the parameters S2f, S2s, and ts.

	The formula is:

		 d2J(w)      2                 1 - (w.ts')**2      /   tm    \ 2
		--------  =  - . (1 - S2s) . ------------------- . | ------- |
		dS2f.dts     5               (1 + (w.ts')**2)**2   \ ts + tm /

	"""

	return 0.4 * (1.0 - data.params[data.s2s_index]) * ((1.0 - data.omega_ts_prime_sqrd[i, frq_index]) / ((1.0 + data.omega_ts_prime_sqrd[i, frq_index])**2)) * data.fact_a**2


def calc_iso_S2f_S2s_ts_d2jw_dS2sdts(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the S2s/ts double partial derivative of the extended model-free formula with the parameters S2f, S2s, and ts.

	The formula is:

		 d2J(w)        2.S2f     1 - (w.ts')**2      /   tm    \ 2
		--------  =  - ----- . ------------------- . | ------- |
		dS2s.dts         5     (1 + (w.ts')**2)**2   \ ts + tm /

	"""

	return -0.4 * data.params[data.s2f_index] * ((1.0 - data.omega_ts_prime_sqrd[i, frq_index]) / ((1.0 + data.omega_ts_prime_sqrd[i, frq_index])**2)) * data.fact_a**2


def calc_iso_S2f_S2s_ts_d2jw_dts2(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the ts/ts double partial derivative of the extended model-free formula with the parameters S2f, S2s, and ts.

	The formula is:

		d2J(w)       4                /   tm    \ 4           1            
		------  =  - - . (S2f - S2) . | ------- |  . ------------------- . [w**2.ts'(3 - (w.ts')**2) + (1 - (w.ts')**4)(ts + tm).tm**-2]
		dts**2       5                \ ts + tm /    (1 + (w.ts')**2)**3   

	"""

	a = 1.0 / ((1.0 + data.omega_ts_prime_sqrd[i, frq_index])**3)
	b = data.frq_sqrd_list[i][frq_index] * data.ts_prime * (3.0 - data.omega_ts_prime_sqrd[i, frq_index])
	c = (1.0 - data.omega_ts_prime_sqrd[i, frq_index]**2) * (data.params[data.ts_index] + data.diff_params[0]) * data.diff_params[0]**-2

	return -0.8 * (data.params[data.s2f_index] - data.s2) * data.fact_a**4 * a * (b + c)



# Extended model-free equations with parameters S2f, tf, S2s, ts.
#################################################################

def calc_iso_S2f_tf_S2s_ts_d2jw_dS2fdS2s(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the S2f/S2s double partial derivative of the extended model-free formula with the parameters S2f, tf, S2s, and ts.

	The formula is:

		  d2J(w)      2 /      tm                 ts'      \ 
		---------  =  - | -------------  -  -------------- |
		dS2f.dS2s     5 \ 1 + (w.tm)**2     1 + (w.ts')**2 /

	"""

	return 0.4 * (data.diff_params[0] / (1.0 + data.omega_tm_sqrd[i, frq_index]) - data.ts_prime / (1.0 + data.omega_ts_prime_sqrd[i, frq_index]))


def calc_iso_S2f_tf_S2s_ts_d2jw_dS2fdtf(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the S2f/ts double partial derivative of the extended model-free formula with the parameters S2f, tf, S2s, and ts.

	The formula is:

		 d2J(w)        2     1 - (w.tf')**2      /   tm    \ 2
		--------  =  - - . ------------------- . | ------- |
		dS2f.dtf       5   (1 + (w.tf')**2)**2   \ tf + tm /

	"""

	return -0.4 * ((1.0 - data.omega_tf_prime_sqrd[i, frq_index]) / ((1.0 + data.omega_tf_prime_sqrd[i, frq_index])**2)) * data.fact_f**2


def calc_iso_S2f_tf_S2s_ts_d2jw_dS2fdts(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the S2f/ts double partial derivative of the extended model-free formula with the parameters S2f, tf, S2s, and ts.

	The formula is:

		 d2J(w)      2                 1 - (w.ts')**2      /   tm    \ 2
		--------  =  - . (1 - S2s) . ------------------- . | ------- |
		dS2f.dts     5               (1 + (w.ts')**2)**2   \ ts + tm /

	"""

	return 0.4 * (1.0 - data.params[data.s2s_index]) * ((1.0 - data.omega_ts_prime_sqrd[i, frq_index]) / ((1.0 + data.omega_ts_prime_sqrd[i, frq_index])**2)) * data.fact_s**2


def calc_iso_S2f_tf_S2s_ts_d2jw_dS2sdts(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the S2s/ts double partial derivative of the extended model-free formula with the parameters S2f, tf, S2s, and ts.

	The formula is:

		 d2J(w)        2.S2f     1 - (w.ts')**2      /   tm    \ 2
		--------  =  - ----- . ------------------- . | ------- |
		dS2s.dts         5     (1 + (w.ts')**2)**2   \ ts + tm /

	"""

	return -0.4 * data.params[data.s2f_index] * ((1.0 - data.omega_ts_prime_sqrd[i, frq_index]) / ((1.0 + data.omega_ts_prime_sqrd[i, frq_index])**2)) * data.fact_s**2


def calc_iso_S2f_tf_S2s_ts_d2jw_dtf2(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the ts/ts double partial derivative of the extended model-free formula with the parameters S2f, tf, S2s, and ts.

	The formula is:

		d2J(w)       4               /   tm    \ 4           1            
		------  =  - - . (1 - S2f) . | ------- |  . ------------------- . [w**2.tf'(3 - (w.tf')**2) + (1 - (w.tf')**4)(tf + tm).tm**-2]
		dtf**2       5               \ tf + tm /    (1 + (w.tf')**2)**3   

	"""

	a = 1.0 / ((1.0 + data.omega_tf_prime_sqrd[i, frq_index])**3)
	b = data.frq_sqrd_list[i][frq_index] * data.tf_prime * (3.0 - data.omega_tf_prime_sqrd[i, frq_index])
	c = (1.0 - data.omega_tf_prime_sqrd[i, frq_index]**2) * (data.params[data.tf_index] + data.diff_params[0]) * data.diff_params[0]**-2

	return -0.8 * (1.0 - data.params[data.s2f_index]) * data.fact_f**4 * a * (b + c)


def calc_iso_S2f_tf_S2s_ts_d2jw_dts2(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the ts/ts double partial derivative of the extended model-free formula with the parameters S2f, tf, S2s, and ts.

	The formula is:

		d2J(w)       4                /   tm    \ 4           1            
		------  =  - - . (S2f - S2) . | ------- |  . ------------------- . [w**2.ts'(3 - (w.ts')**2) + (1 - (w.ts')**4)(ts + tm).tm**-2]
		dts**2       5                \ ts + tm /    (1 + (w.ts')**2)**3   

	"""

	a = 1.0 / ((1.0 + data.omega_ts_prime_sqrd[i, frq_index])**3)
	b = data.frq_sqrd_list[i][frq_index] * data.ts_prime * (3.0 - data.omega_ts_prime_sqrd[i, frq_index])
	c = (1.0 - data.omega_ts_prime_sqrd[i, frq_index]**2) * (data.params[data.ts_index] + data.diff_params[0]) * data.diff_params[0]**-2

	return -0.8 * (data.params[data.s2f_index] - data.s2) * data.fact_s**4 * a * (b + c)
