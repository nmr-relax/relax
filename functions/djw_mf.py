from Numeric import Float64, zeros
from re import match

def create_djw_struct(data, calc_djw):
	"""Function to create model-free spectral density gradients.

	The spectral density gradients
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	Data structure:  data.djw
	Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters)
	Type:  Numeric 3D matrix, Float64
	Dependencies:  None
	Required by:  data.dri, data.d2ri


	Formulae
	~~~~~~~~

	Original
	~~~~~~~~

		dJ(w)     2 /       tm                te'      \ 
		-----  =  - | -------------  -  -------------- |
		 dS2      5 \ 1 + (w.tm)**2     1 + (w.te')**2 /


		dJ(w)     2                1 - (w.te')**2      /   tm    \ 2
		-----  =  - . (1 - S2) . ------------------- . | ------- |
		 dte      5              (1 + (w.te')**2)**2   \ te + tm /


		dJ(w)
		-----  =  0
		dRex


		dJ(w)
		-----  =  0
		dcsa


		dJ(w)
		-----  =  0
		 dr


	Extended
	~~~~~~~~

		dJ(w)     2 /    S2s.tm               tf'          (1 - S2s).ts' \ 
		-----  =  - | -------------  -  -------------- +  -------------- |
		dS2f      5 \ 1 + (w.tm)**2     1 + (w.tf')**2    1 + (w.ts')**2 /


		dJ(w)     2.S2f   /       tm                ts'      \ 
		-----  =  ----- . | -------------  -  -------------- |
		dS2s        5     \ 1 + (w.tm)**2     1 + (w.ts')**2 /


		dJ(w)     2                 1 - (w.tf')**2      /   tm    \ 2
		-----  =  - . (1 - S2f) . ------------------- . | ------- |
		 dtf      5               (1 + (w.tf')**2)**2   \ tf + tm /


		dJ(w)     2.S2f                 1 - (w.ts')**2      /   tm    \ 2
		-----  =  ----- . (1 - S2s) . ------------------- . | ------- |
		 dts        5                 (1 + (w.ts')**2)**2   \ ts + tm /


		dJ(w)
		-----  =  0
		dRex


		dJ(w)
		-----  =  0
		dcsa


		dJ(w)
		-----  =  0
		 dr
	"""

	for i in range(data.num_frq):
		for param in range(len(calc_djw)):
			data.djw[i, 0, param] = calc_djw[param](i, 0, data)
			data.djw[i, 1, param] = calc_djw[param](i, 1, data)
			data.djw[i, 2, param] = calc_djw[param](i, 2, data)
			data.djw[i, 3, param] = calc_djw[param](i, 3, data)
			data.djw[i, 4, param] = calc_djw[param](i, 4, data)


def calc_iso_djw_dS2_S2(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the S2 partial derivative of the original model-free formula with the single parameter S2.

	The formula is:

		dJ(w)     2 /       tm      \ 
		-----  =  - | ------------- |
		 dS2      5 \ 1 + (w.tm)**2 /

	"""

	return 0.4 * data.tm / (1.0 + data.omega_tm_sqrd[i, frq_index])


def calc_iso_djw_dS2_S2_te(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the S2 partial derivative of the original model-free formula with the parameters S2 and te.

	The formula is:

		dJ(w)     2 /       tm                te'      \ 
		-----  =  - | -------------  -  -------------- |
		 dS2      5 \ 1 + (w.tm)**2     1 + (w.te')**2 /

	"""

	return 0.4 * (data.tm / (1.0 + data.omega_tm_sqrd[i, frq_index]) - data.te_prime / (1.0 + data.omega_te_prime_sqrd[i, frq_index]))


def calc_iso_djw_dte_S2_te(i, frq_index, data):
	"""Calculate the isotropic spectral desity value for the te partial derivative of the original model-free formula with the parameters S2 and te.

	The formula is:

		dJ(w)     2                1 - (w.te')**2      /   tm    \ 2
		-----  =  - . (1 - S2) . ------------------- . | ------- |
		 dte      5              (1 + (w.te')**2)**2   \ te + tm /

	"""

	return 0.4 * (1.0 - data.s2) * ((1.0 - data.omega_te_prime_sqrd[i, frq_index]) / ((1.0 + data.omega_te_prime_sqrd[i, frq_index])**2)) * data.fact_a**2


def calc_djw_dS2f_iso_m5(self, i, frq_index):
	"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

	temp = 0.4 * (self.data.s2s * self.data.tm / (1.0 + self.data.omega_tm_sqrd[i, frq_index]) + (1.0 - self.data.s2s) * self.data.ts_prime / (1.0 + self.data.omega_ts_prime_sqrd[i, frq_index]))
	return temp


def calc_djw_dS2s_iso_m5(self, i, frq_index):
	"Calculate the model 5 S2f derivative of the spectral density function for isotropic rotational diffusion."

	temp = 0.4 * self.data.s2f * (self.data.tm / (1.0 + self.data.omega_tm_sqrd[i, frq_index]) - self.data.ts_prime / (1.0 + self.data.omega_ts_prime_sqrd[i, frq_index]))
	return temp


def calc_djw_dts_iso_m5(self, i, frq_index):
	"Calculate the model 5 ts derivative of the spectral density function for isotropic rotational diffusion."

	temp = 0.4 * self.data.s2f * (1.0 - self.data.s2s) * ((1.0 - self.data.omega_ts_prime_sqrd[i, frq_index]) / ((1.0 + self.data.omega_ts_prime_sqrd[i, frq_index])**2)) * self.data.fact_a**2
	return temp
