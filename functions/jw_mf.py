from Numeric import Float64, zeros

from jw_mf_new import *

def create_jw_struct(data, calc_jw):
	"""Function to create the model-free spectral density values.

	The spectral density equation
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  data.jw
	Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
	Type:  Numeric matrix, Float64
	Dependencies:  None
	Required by:  data.ri, data.dri, data.d2ri


	Formulae
	~~~~~~~~

	Original
	~~~~~~~~

		         2 /    S2 . tm        (1 - S2) . te' \ 
		J(w)  =  - | -------------  +  -------------- |
		         5 \ 1 + (w.tm)**2     1 + (w.te')**2 /


	Extended
	~~~~~~~~

		         2 /    S2 . tm        (1 - S2f) . tf'     (S2f - S2) . ts' \ 
		J(w)  =  - | -------------  +  ---------------  +  ---------------- |
		         5 \ 1 + (w.tm)**2     1 + (w.tf')**2       1 + (w.ts')**2  /

	"""

	for i in range(data.num_frq):
		data.jw[i, 0] = calc_jw(i, 0, data)
		data.jw[i, 1] = calc_jw(i, 1, data)
		data.jw[i, 2] = calc_jw(i, 2, data)
		data.jw[i, 3] = calc_jw(i, 3, data)
		data.jw[i, 4] = calc_jw(i, 4, data)


def calc_iso_s2_jw(i, frq_index, data):
	"""Calculate the isotropic spectral density value for the original model-free formula with the single parameter S2.

	The formula is:

		         2 /    S2 . tm    \ 
		J(w)  =  - | ------------- |
		         5 \ 1 + (w.tm)**2 /

	"""

	return c_calc_iso_s2_jw(data.s2_tm, data.omega_tm_sqrd[i, frq_index])
	#return 0.4 * (data.s2_tm / (1.0 + data.omega_tm_sqrd[i, frq_index]))


def calc_iso_s2_jw_comps(data):
	"Calculate some data used in the calculation of values, gradients, and hessians."

	data.tm_sqrd = data.diff_params[0] ** 2
	data.s2_tm = data.params[data.s2_index] * data.diff_params[0]

	data.omega_tm_sqrd = zeros((data.num_frq, 5), Float64)
	for i in range(data.num_frq):
		for frq_index in range(5):
			data.omega_tm_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.tm_sqrd


def calc_iso_s2_te_jw(i, frq_index, data):
	"""Calculate the isotropic spectral density value for the original model-free formula with the parameters S2 and te.

	The formula is:

		         2 /    S2 . tm        (1 - S2) . te' \ 
		J(w)  =  - | -------------  +  -------------- |
		         5 \ 1 + (w.tm)**2     1 + (w.te')**2 /

	"""

	return 0.4 * (data.s2_tm / (1.0 + data.omega_tm_sqrd[i, frq_index]) + (1.0 - data.params[data.s2_index]) * data.te_prime / (1.0 + data.omega_te_prime_sqrd[i, frq_index]))


def calc_iso_s2_te_jw_comps(data):
	"Calculate some data used in the calculation of values, gradients, and hessians."

	data.tm_sqrd = data.diff_params[0] ** 2
	data.fact_a = data.diff_params[0] / (data.params[data.te_index] + data.diff_params[0])
	data.te_prime = data.params[data.te_index] * data.fact_a
	data.te_prime_sqrd = data.te_prime ** 2
	data.s2_tm = data.params[data.s2_index] * data.diff_params[0]

	data.omega_tm_sqrd = zeros((data.num_frq, 5), Float64)
	data.omega_te_prime_sqrd = zeros((data.num_frq, 5), Float64)
	for i in range(data.num_frq):
		for frq_index in range(5):
			data.omega_tm_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.tm_sqrd
			data.omega_te_prime_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.te_prime_sqrd


def calc_iso_s2f_s2s_ts_jw(i, frq_index, data):
	"""Calculate the isotropic spectral density value for the extended model-free formula with the parameters S2f, S2s, and ts.

	The formula is:

		         2 /    S2 . tm        (S2f - S2) . ts' \ 
		J(w)  =  - | -------------  +  ---------------- |
		         5 \ 1 + (w.tm)**2      1 + (w.ts')**2  /

	"""

	return c_calc_iso_s2f_s2s_ts_jw(data.params[data.s2f_index], data.s2s_tm, data.omega_tm_sqrd[i, frq_index], data.params[data.s2s_index], data.ts_prime, data.omega_ts_prime_sqrd[i, frq_index])
	#return 0.4 * data.params[data.s2f_index] * (data.s2s_tm / (1.0 + data.omega_tm_sqrd[i, frq_index]) + (1.0 - data.params[data.s2s_index]) * data.ts_prime / (1.0 + data.omega_ts_prime_sqrd[i, frq_index]))


def calc_iso_s2f_s2s_ts_jw_comps(data):
	"Calculate some data used in the calculation of values, gradients, and hessians."

	data.tm_sqrd = data.diff_params[0] ** 2

	data.s2 = data.params[data.s2f_index] * data.params[data.s2s_index]
	data.fact_a = data.diff_params[0] / (data.params[data.ts_index] + data.diff_params[0])
	data.ts_prime = data.params[data.ts_index] * data.fact_a
	data.ts_prime_sqrd = data.ts_prime ** 2
	data.s2s_tm = data.params[data.s2s_index] * data.diff_params[0]

	data.omega_tm_sqrd = zeros((data.num_frq, 5), Float64)
	data.omega_ts_prime_sqrd = zeros((data.num_frq, 5), Float64)
	for i in range(data.num_frq):
		for frq_index in range(5):
			data.omega_tm_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.tm_sqrd
			data.omega_ts_prime_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.ts_prime_sqrd


def calc_iso_s2f_tf_s2s_ts_jw(i, frq_index, data):
	"""Calculate the isotropic spectral density value for the extended model-free formula with the parameters S2f, tf, S2s, and ts.

	The formula is:

		         2 /    S2 . tm        (1 - S2f) . tf'     (S2f - S2) . ts' \ 
		J(w)  =  - | -------------  +  ---------------  +  ---------------- |
		         5 \ 1 + (w.tm)**2     1 + (w.tf')**2       1 + (w.ts')**2  /

	"""

	a = data.s2_tm / (1.0 + data.omega_tm_sqrd[i, frq_index])
	b = (1.0 - data.params[data.s2f_index]) * data.tf_prime / (1.0 + data.omega_tf_prime_sqrd[i, frq_index])
	c =  data.params[data.s2f_index] * (1.0 - data.params[data.s2s_index]) * data.ts_prime / (1.0 + data.omega_ts_prime_sqrd[i, frq_index])
	return 0.4 * (a + b + c)


def calc_iso_s2f_tf_s2s_ts_jw_comps(data):
	"Calculate some data used in the calculation of values, gradients, and hessians."

	data.tm_sqrd = data.diff_params[0] ** 2

	data.s2 = data.params[data.s2f_index] * data.params[data.s2s_index]
	data.fact_f = data.diff_params[0] / (data.params[data.tf_index] + data.diff_params[0])
	data.fact_s = data.diff_params[0] / (data.params[data.ts_index] + data.diff_params[0])
	data.tf_prime = data.params[data.tf_index] * data.fact_f
	data.ts_prime = data.params[data.ts_index] * data.fact_s
	data.tf_prime_sqrd = data.tf_prime ** 2
	data.ts_prime_sqrd = data.ts_prime ** 2
	data.s2s_tm = data.params[data.s2s_index] * data.diff_params[0]
	data.s2_tm = data.s2 * data.diff_params[0]

	data.omega_tm_sqrd = zeros((data.num_frq, 5), Float64)
	data.omega_ts_prime_sqrd = zeros((data.num_frq, 5), Float64)
	for i in range(data.num_frq):
		for frq_index in range(5):
			data.omega_tm_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.tm_sqrd
			data.omega_tf_prime_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.tf_prime_sqrd
			data.omega_ts_prime_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.ts_prime_sqrd
