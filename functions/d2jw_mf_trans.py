from Numeric import Float64, zeros
from re import match

class d2Jw:
	def __init__(self):
		"Function for creating the model-free spectral density hessians."


	def d2Jw(self):
		"""Function to create model-free spectral density hessians.

		The spectral density hessians
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.d2jw
		Dimension:  4D, (number of NMR frequencies, 5 spectral density frequencies, model-free parameters, model-free parameters)
		Type:  Numeric 4D matrix, Float64
		Dependencies:  None
		Required by:  self.data.d2ri


		Formulae
		~~~~~~~~

		Parameter transformations
		~~~~~~~~~~~~~~~~~~~~~~~~~
			ae  =  c.te

			af  =  c.tf

			as  =  c.ts


			therefore:

				          tm.ae
				te'  =  ---------
				        ae + c.tm

				          tm.af
				tf'  =  ---------
				        af + c.tm

				          tm.as
				ts'  =  ---------
				        as + c.tm


		Original:  Model-free parameter - Model-free parameter
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

			d2J(w)
			------  =  0
			dS2**2


			 d2J(w)       2                (ae + c.tm)**2 - (w.tm.ae)**2
			-------  =  - - . c . tm**2 . ----------------------------------
			dS2.dae       5               ((ae + c.tm)**2 + (w.tm.ae)**2)**2


			d2J(w)       4                          (ae + c.tm)**3 + 3.c.tm**3.ae.w**2.(ae + c.tm) - (1/ae).(w.tm.ae)**4
			------  =  - - . c . tm**2 . (1 - S2) . --------------------------------------------------------------------
			dae**2       5                                          ((ae + c.tm)**2 + (w.tm.ae)**2)**3


		Original:  Other parameters
		~~~~~~~~~~~~~~~~~~~~~~~~~~~

			 d2J(w)               d2J(w)              d2J(w)
			--------  =  0   ,   --------  =  0   ,   ------  =  0
			dS2.dRex             dS2.dcsa             dS2.dr


			 d2J(w)              d2J(w)               d2J(w)
			--------  =  0   ,  --------  =  0   ,    ------  =  0
			dae.dRex            dae.dcsa              dae.dr


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


			  d2J(w)      2*tm /       1                 (as + c.tm) . as        \ 
			---------  =  ---- | -------------  -  ----------------------------- |
			dS2f.dS2s      5   \ 1 + (w.tm)**2     (as + c.tm)**2 + (w.tm.as)**2 /


			 d2J(w)        2                (af + c.tm)**2 - (w.tm.af)**2    
			--------  =  - - . c . tm**2 . ----------------------------------
			dS2f.daf       5               ((af + c.tm)**2 + (w.tm.af)**2)**2


			 d2J(w)      2                            (as + c.tm)**2 - (w.tm.as)**2
			--------  =  - . c . tm**2 . (1 - S2s) . ----------------------------------
			dS2f.das     5                           ((as + c.tm)**2 + (w.tm.as)**2)**2


			 d2J(w)                d2J(w)
			-------  =  0   ,   -------------  =  0
			dS2s**2             dS2s.daf


			 d2J(w)        2                      (as + c.tm)**2 - (w.tm.as)**2
			--------  =  - - . c . tm**2 . S2f . ----------------------------------
			dS2s.das       5                     ((as + c.tm)**2 + (w.tm.as)**2)**2


			d2J(w)       4                           (af + c.tm)**3 + 3.c.tm**3.af.w**2.(af + c.tm) - (1/af).(w.tm.af)**4
			------  =  - - . c . tm**2 . (1 - S2f) . --------------------------------------------------------------------
			daf**2       5                                          ((af + c.tm)**2 + (w.tm.af)**2)**3


			 d2J(w)
			-------  =  0
			daf.das


			d2J(w)       4                                 (as + c.tm)**3 + 3.c.tm**3.as.w**2.(as + c.tm) - (1/as).(w.tm.as)**4
			------  =  - - . c . tm**2 . S2f . (1 - S2s) . --------------------------------------------------------------------
			das**2       5                                                ((as + c.tm)**2 + (w.tm.as)**2)**3


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
			daf.dRex             daf.dcsa             daf.dr


			 d2J(w)               d2J(w)              d2J(w)
			--------  =  0   ,   --------  =  0   ,   ------  =  0
			das.dRex             das.dcsa             das.dr


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

		# Initialise the spectral density hessians.
		self.data.d2jw = zeros((self.mf.data.num_frq, 5, len(self.data.params), len(self.data.params)), Float64)

		# Isotropic rotational diffusion.
		if match(self.data.diff_type, 'iso'):
			# Model 1 and 3 hessians are zero.
			if match('m[24]', self.data.model):
				for i in range(self.mf.data.num_frq):
					for param1 in range(len(self.data.jw_param_types)):
						for param2 in range(param1 + 1):
							if (self.data.jw_param_types[param1] == 'S2' and self.data.jw_param_types[param2] == 'te') \
								or (self.data.jw_param_types[param1] == 'te' and self.data.jw_param_types[param2] == 'S2'):
								# Calculate the S2/te partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2dae_iso_m24(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2dae_iso_m24(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2dae_iso_m24(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2dae_iso_m24(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2dae_iso_m24(i, 4)
								# Off diagonal hessian components are symmetric.
								self.data.d2jw[i, 0, param2, param1] = self.data.d2jw[i, 0, param1, param2]
								self.data.d2jw[i, 1, param2, param1] = self.data.d2jw[i, 1, param1, param2]
								self.data.d2jw[i, 2, param2, param1] = self.data.d2jw[i, 2, param1, param2]
								self.data.d2jw[i, 3, param2, param1] = self.data.d2jw[i, 3, param1, param2]
								self.data.d2jw[i, 4, param2, param1] = self.data.d2jw[i, 4, param1, param2]
							elif self.data.jw_param_types[param1] == 'te' and self.data.jw_param_types[param2] == 'te':
								# Calculate the te/te partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dae2_iso_m24(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dae2_iso_m24(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dae2_iso_m24(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dae2_iso_m24(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dae2_iso_m24(i, 4)
			elif match('m5', self.data.model):
				for i in range(self.mf.data.num_frq):
					for param1 in range(len(self.data.jw_param_types)):
						for param2 in range(param1 + 1):
							if (self.data.jw_param_types[param1] == 'S2f' and self.data.jw_param_types[param2] == 'S2s') \
								or (self.data.jw_param_types[param1] == 'S2s' and self.data.jw_param_types[param2] == 'S2f'):
								# Calculate the S2f/S2s partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2fdS2s_iso_m5(i, 4)
								# Off diagonal hessian components are symmetric.
								self.data.d2jw[i, 0, param2, param1] = self.data.d2jw[i, 0, param1, param2]
								self.data.d2jw[i, 1, param2, param1] = self.data.d2jw[i, 1, param1, param2]
								self.data.d2jw[i, 2, param2, param1] = self.data.d2jw[i, 2, param1, param2]
								self.data.d2jw[i, 3, param2, param1] = self.data.d2jw[i, 3, param1, param2]
								self.data.d2jw[i, 4, param2, param1] = self.data.d2jw[i, 4, param1, param2]
							elif (self.data.jw_param_types[param1] == 'S2f' and self.data.jw_param_types[param2] == 'ts') \
								or (self.data.jw_param_types[param1] == 'ts' and self.data.jw_param_types[param2] == 'S2f'):
								# Calculate the S2f/ts partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2fdas_iso_m5(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2fdas_iso_m5(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2fdas_iso_m5(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2fdas_iso_m5(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2fdas_iso_m5(i, 4)
								# Off diagonal hessian components are symmetric.
								self.data.d2jw[i, 0, param2, param1] = self.data.d2jw[i, 0, param1, param2]
								self.data.d2jw[i, 1, param2, param1] = self.data.d2jw[i, 1, param1, param2]
								self.data.d2jw[i, 2, param2, param1] = self.data.d2jw[i, 2, param1, param2]
								self.data.d2jw[i, 3, param2, param1] = self.data.d2jw[i, 3, param1, param2]
								self.data.d2jw[i, 4, param2, param1] = self.data.d2jw[i, 4, param1, param2]
							elif (self.data.jw_param_types[param1] == 'S2s' and self.data.jw_param_types[param2] == 'ts') \
								or (self.data.jw_param_types[param1] == 'ts' and self.data.jw_param_types[param2] == 'S2s'):
								# Calculate the S2s/ts partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_dS2sdas_iso_m5(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_dS2sdas_iso_m5(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_dS2sdas_iso_m5(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_dS2sdas_iso_m5(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_dS2sdas_iso_m5(i, 4)
								# Off diagonal hessian components are symmetric.
								self.data.d2jw[i, 0, param2, param1] = self.data.d2jw[i, 0, param1, param2]
								self.data.d2jw[i, 1, param2, param1] = self.data.d2jw[i, 1, param1, param2]
								self.data.d2jw[i, 2, param2, param1] = self.data.d2jw[i, 2, param1, param2]
								self.data.d2jw[i, 3, param2, param1] = self.data.d2jw[i, 3, param1, param2]
								self.data.d2jw[i, 4, param2, param1] = self.data.d2jw[i, 4, param1, param2]
							elif self.data.jw_param_types[param1] == 'ts' and self.data.jw_param_types[param2] == 'ts':
								# Calculate the ts/ts partial derivatives.
								self.data.d2jw[i, 0, param1, param2] = self.calc_d2jw_das2_iso_m5(i, 0)
								self.data.d2jw[i, 1, param1, param2] = self.calc_d2jw_das2_iso_m5(i, 1)
								self.data.d2jw[i, 2, param1, param2] = self.calc_d2jw_das2_iso_m5(i, 2)
								self.data.d2jw[i, 3, param1, param2] = self.calc_d2jw_das2_iso_m5(i, 3)
								self.data.d2jw[i, 4, param1, param2] = self.calc_d2jw_das2_iso_m5(i, 4)


		# Axially symmetric rotational diffusion.
		elif match(self.data.diff_type, 'axail'):
			raise NameError, "Axially symetric diffusion not implemented yet, quitting program."

		# Anisotropic rotational diffusion.
		elif match(self.data.diff_type, 'aniso'):
			raise NameError, "Anisotropic diffusion not implemented yet, quitting program."

		else:
			raise NameError, "Function option not set correctly, quitting program."


	def calc_d2jw_dS2dae_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 S2/te partial derivative of the spectral density function for isotropic rotational diffusion."

		a = (self.data.ae_plus_c_tm_sqrd - self.data.omega_tm_ae_sqrd[i, frq_index])
		b = (self.data.ae_plus_c_tm_sqrd + self.data.omega_tm_ae_sqrd[i, frq_index])**2
		temp = -0.4 * self.data.c * self.data.tm_sqrd * (a/b)
		return temp


	def calc_d2jw_dae2_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 te/te partial derivative of the spectral density function for isotropic rotational diffusion."

		a = self.data.ae_plus_c_tm**3
		b = 3.0 * self.data.c * self.data.tm**3 * self.data.ae * self.mf.data.frq_sqrd_list[i][frq_index] * self.data.ae_plus_c_tm
		c = (self.mf.data.frq_list[i][frq_index] * self.data.tm)**4 * self.data.ae**3
		d = (self.data.ae_plus_c_tm_sqrd + self.data.omega_tm_ae_sqrd[i, frq_index])**3
		temp = -0.8 * self.data.c * self.data.tm_sqrd * (1.0 - self.data.s2) * (a + b - c) / d
		return temp


	def calc_d2jw_dS2fdS2s_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f/S2s partial derivative of the spectral density function for isotropic rotational diffusion."

		a = 1.0 / (1.0 + self.data.omega_tm_sqrd[i, frq_index])
		b = self.data.as_plus_c_tm * self.data.as / (self.data.as_plus_c_tm_sqrd + self.data.omega_tm_as_sqrd[i, frq_index])
		temp = 0.4 * self.data.tm * (a - b)
		return temp


	def calc_d2jw_dS2fdas_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2f/ts partial derivative of the spectral density function for isotropic rotational diffusion."

		a = (self.data.as_plus_c_tm_sqrd - self.data.omega_tm_as_sqrd[i, frq_index])
		b = (self.data.as_plus_c_tm_sqrd + self.data.omega_tm_as_sqrd[i, frq_index])**2
		temp = -0.4 * self.data.c * self.data.tm_sqrd * (a/b)
		return temp


	def calc_d2jw_dS2sdas_iso_m5(self, i, frq_index):
		"Calculate the model 5 S2s/ts partial derivative of the spectral density function for isotropic rotational diffusion."

		a = (self.data.as_plus_c_tm_sqrd - self.data.omega_tm_as_sqrd[i, frq_index])
		b = (self.data.as_plus_c_tm_sqrd + self.data.omega_tm_as_sqrd[i, frq_index])**2
		temp = 0.4 * self.data.c * self.data.tm_sqrd * (1.0 - self.data.s2s) * (a/b)
		return temp


	def calc_d2jw_das2_iso_m5(self, i, frq_index):
		"Calculate the model 5 ts/ts partial derivative of the spectral density function for isotropic rotational diffusion."

		a = self.data.as_plus_c_tm**3
		b = 3.0 * self.data.c * self.data.tm**3 * self.data.as * self.mf.data.frq_sqrd_list[i][frq_index] * self.data.as_plus_c_tm
		c = (self.mf.data.frq_list[i][frq_index] * self.data.tm)**4 * self.data.as**3
		d = (self.data.as_plus_c_tm_sqrd + self.data.omega_tm_as_sqrd[i, frq_index])**3
		temp = -0.8 * self.data.c * self.data.tm_sqrd * self.data.s2f * (1.0 - self.data.s2s) * (a + b - c) / d
		return temp
