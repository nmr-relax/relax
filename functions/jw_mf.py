from Numeric import Float64, zeros
from re import match

def create_jw_struct(data, calc_jw):
	"""Function to create the model-free spectral density values.

	"""

	for i in range(data.num_frq):
		data.jw[i, 0] = calc_jw(i, 0, data)
		data.jw[i, 1] = calc_jw(i, 1, data)
		data.jw[i, 2] = calc_jw(i, 2, data)
		data.jw[i, 3] = calc_jw(i, 3, data)
		data.jw[i, 4] = calc_jw(i, 4, data)


def calc_iso_jw_s2(i, frq_index, data):
	"""Calculate the isotropic spectral density values for the single parameter S2.

	The formula is:

		         2 /    S2 . tm    \ 
		J(w)  =  - | ------------- |
		         5 \ 1 + (w.tm)**2 /

	The data structure data.mf_indecies should be an array of integers which point the model-free parameters to the relevant positions in data.params
	It has the following form:
		data.mf_indecies = [s2_index]
	"""

	return 0.4 * (data.s2_tm / (1.0 + data.omega_tm_sqrd[i, frq_index]))


def calc_iso_jw_s2_data(data):
	"Calculate some data used in the calculation of values, gradients, and hessians."

	data.tm_sqrd = data.diff_params[0] ** 2
	data.s2_tm = data.params[data.mf_indecies[0]] * data.diff_params[0]

	data.omega_tm_sqrd = zeros((data.num_frq, 5), Float64)
	for i in range(data.num_frq):
		for frq_index in range(5):
			data.omega_tm_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.tm_sqrd


def calc_iso_jw_s2_te(i, frq_index, data):
	"""Calculate the isotropic spectral density values for the parameters S2 and te.

	The formula is:

		         2 /    S2 . tm        (1 - S2) . te' \ 
		J(w)  =  - | -------------  +  -------------- |
		         5 \ 1 + (w.tm)**2     1 + (w.te')**2 /

	The data structure data.mf_indecies should be an array of integers which point the model-free parameters to the relevant positions in data.params
	It has the following form:
		data.mf_indecies = [s2_index, te_index]
	"""

	return 0.4 * (data.s2_tm / (1.0 + data.omega_tm_sqrd[i, frq_index]) + (1.0 - data.params[data.mf_indecies[0]]) * data.te_prime / (1.0 + data.omega_te_prime_sqrd[i, frq_index]))


def calc_iso_jw_s2_te_data(data):
	"Calculate some data used in the calculation of values, gradients, and hessians."

	data.tm_sqrd = data.diff_params[0] ** 2
	data.fact_a = data.diff_params[0] / (data.params[data.mf_indecies[1]] + data.diff_params[0])
	data.te_prime = data.params[data.mf_indecies[1]] * data.fact_a
	data.te_prime_sqrd = data.te_prime ** 2
	data.s2_tm = data.params[data.mf_indecies[0]] * data.diff_params[0]

	data.omega_tm_sqrd = zeros((data.num_frq, 5), Float64)
	data.omega_te_prime_sqrd = zeros((data.num_frq, 5), Float64)
	for i in range(data.num_frq):
		for frq_index in range(5):
			data.omega_tm_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.tm_sqrd
			data.omega_te_prime_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.te_prime_sqrd


def calc_iso_jw_s2f_s2s_ts(i, frq_index, data):
	"""Calculate the model 5 spectral density values for isotropic rotational diffusion.

	The formula is:

		         2 /    S2 . tm        (S2f - S2) . ts' \ 
		J(w)  =  - | -------------  +  ---------------- |
		         5 \ 1 + (w.tm)**2      1 + (w.ts')**2  /

	The data structure data.mf_indecies should be an array of integers which point the model-free parameters to the relevant positions in data.params
	It has the following form:
		data.mf_indecies = [s2f_index, s2s_index, ts_index]
	"""

	return 0.4 * data.params[data.mf_indecies[0]] * (data.s2s_tm / (1.0 + data.omega_tm_sqrd[i, frq_index]) + (1.0 - data.params[data.mf_indecies[1]]) * data.ts_prime / (1.0 + data.omega_ts_prime_sqrd[i, frq_index]))


def calc_iso_jw_s2f_s2s_ts_data(data):
	"Calculate some data used in the calculation of values, gradients, and hessians."

	data.tm_sqrd = data.diff_params[0] ** 2

	data.s2 = data.params[data.mf_indecies[0]] * data.params[mf_indecies[1]]
	data.fact_a = data.diff_params[0] / (data.params[mf_indecies[2]] + data.diff_params[0])
	data.ts_prime = data.params[mf_indecies[2]] * data.fact_a
	data.ts_prime_sqrd = data.ts_prime ** 2
	data.s2s_tm = data.params[mf_indecies[1]] * data.diff_params[0]

	data.omega_tm_sqrd = zeros((data.num_frq, 5), Float64)
	data.omega_ts_prime_sqrd = zeros((data.num_frq, 5), Float64)
	for i in range(relax.data.num_frq):
		for frq_index in range(5):
			data.omega_tm_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.tm_sqrd
			data.omega_ts_prime_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.ts_prime_sqrd


def calc_iso_jw_s2f_tf_s2s_ts(i, frq_index, data):
	"""Calculate the model 5 spectral density values for isotropic rotational diffusion.

	The formula is:

		         2 /    S2 . tm        (1 - Sf2) . tf'     (S2f - S2) . ts' \ 
		J(w)  =  - | -------------  +  ---------------  +  ---------------- |
		         5 \ 1 + (w.tm)**2     1 + (w.tf')**2       1 + (w.ts')**2  /

	The data structure data.mf_indecies should be an array of integers which point the model-free parameters to the relevant positions in data.params
	It has the following form:
		data.mf_indecies = [s2f_index, tf_index, s2s_index, ts_index]
	"""

	a = data.s2_tm / (1.0 + data.omega_tm_sqrd[i, frq_index])
	b = (1.0 - data.params[data.mf_indecies[0]]) * data.tf_prime / (1.0 + data.omega_tf_prime_sqrd[i, frq_index])
	c =  data.params[data.mf_indecies[0]] * (1.0 - data.params[data.mf_indecies[2]]) * data.ts_prime / (1.0 + data.omega_ts_prime_sqrd[i, frq_index])
	return 0.4 * (a + b + c)


def calc_iso_jw_s2f_tf_s2s_ts_data(data):
	"Calculate some data used in the calculation of values, gradients, and hessians."

	data.tm_sqrd = data.diff_params[0] ** 2

	data.s2 = data.params[data.mf_indecies[0]] * data.params[mf_indecies[2]]
	data.fact_f = data.diff_params[0] / (data.params[mf_indecies[1]] + data.diff_params[0])
	data.fact_s = data.diff_params[0] / (data.params[mf_indecies[3]] + data.diff_params[0])
	data.tf_prime = data.params[mf_indecies[1]] * data.fact_f
	data.ts_prime = data.params[mf_indecies[3]] * data.fact_s
	data.tf_prime_sqrd = data.tf_prime ** 2
	data.ts_prime_sqrd = data.ts_prime ** 2
	data.s2s_tm = data.params[mf_indecies[2]] * data.diff_params[0]
	data.s2_tm = data.s2 * data.diff_params[0]

	data.omega_tm_sqrd = zeros((data.num_frq, 5), Float64)
	data.omega_ts_prime_sqrd = zeros((data.num_frq, 5), Float64)
	for i in range(relax.data.num_frq):
		for frq_index in range(5):
			data.omega_tm_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.tm_sqrd
			data.omega_tf_prime_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.tf_prime_sqrd
			data.omega_ts_prime_sqrd[i, frq_index] = data.frq_sqrd_list[i][frq_index] * data.ts_prime_sqrd
