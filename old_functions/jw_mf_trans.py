from Numeric import Float64, zeros
from re import match

class Jw:
	def __init__(self):
		"Function for creating the model-free spectral density values using parameter transformations."


	def Jw(self):
		"""Function to create the model-free spectral density values using parameter transformations."

		The spectral density equation
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.jw
		Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
		Type:  Numeric matrix, Float64
		Dependencies:  None
		Required by:  self.data.ri, self.data.dri, self.data.d2ri


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


		Original
		~~~~~~~~

			         2.tm /      S2             (1 - S2)(ae + c.tm) . ae    \ 
			J(w)  =  ---- | -------------  +  ----------------------------- |
			          5   \ 1 + (w.tm)**2     (ae + c.tm)**2 + (w.tm.ae)**2 /


		Extended
		~~~~~~~~

			         2.tm /      S2             (1 - S2f)(af + c.tm) . af        (S2f - S2)(as + c.tm) . as   \ 
			J(w)  =  ---- | -------------  +  -----------------------------  +  ----------------------------- |
			          5   \ 1 + (w.tm)**2     (af + c.tm)**2 + (w.tm.af)**2     (as + c.tm)**2 + (w.tm.as)**2 /


		"""

		# The value of the constant.
		self.data.c = 1e10

		# Calculate frequency independent terms (to increase speed)
		self.initialise_jw_values()

		# Initialise the spectral density values.
		self.data.jw = zeros((self.relax.data.num_frq, 5), Float64)

		# Isotropic rotational diffusion.
		if match(self.data.diff_type, 'iso'):
			if match('m[13]', self.data.model):
				for i in range(self.relax.data.num_frq):
					self.data.jw[i, 0] = self.calc_jw_iso_m13(i, 0)
					self.data.jw[i, 1] = self.calc_jw_iso_m13(i, 1)
					self.data.jw[i, 2] = self.calc_jw_iso_m13(i, 2)
					self.data.jw[i, 3] = self.calc_jw_iso_m13(i, 3)
					self.data.jw[i, 4] = self.calc_jw_iso_m13(i, 4)
			elif match('m[24]', self.data.model):
				for i in range(self.relax.data.num_frq):
					self.data.jw[i, 0] = self.calc_jw_iso_m24(i, 0)
					self.data.jw[i, 1] = self.calc_jw_iso_m24(i, 1)
					self.data.jw[i, 2] = self.calc_jw_iso_m24(i, 2)
					self.data.jw[i, 3] = self.calc_jw_iso_m24(i, 3)
					self.data.jw[i, 4] = self.calc_jw_iso_m24(i, 4)
			elif match('m5', self.data.model):
				for i in range(self.relax.data.num_frq):
					self.data.jw[i, 0] = self.calc_jw_iso_m5(i, 0)
					self.data.jw[i, 1] = self.calc_jw_iso_m5(i, 1)
					self.data.jw[i, 2] = self.calc_jw_iso_m5(i, 2)
					self.data.jw[i, 3] = self.calc_jw_iso_m5(i, 3)
					self.data.jw[i, 4] = self.calc_jw_iso_m5(i, 4)

		# Axially symmetric rotational diffusion.
		elif match(self.data.diff_type, 'axail'):
			raise NameError, "Axially symetric diffusion not implemented yet, quitting program."

		# Anisotropic rotational diffusion.
		elif match(self.data.diff_type, 'aniso'):
			raise NameError, "Anisotropic diffusion not implemented yet, quitting program."

		else:
			raise NameError, "Diffusion type set incorrectly, quitting program."


	def calc_jw_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 spectral density values for isotropic rotational diffusion."

		temp = 0.4 * self.data.tm * (self.data.s2 / (1.0 + self.data.omega_tm_sqrd[i, frq_index]))
		return temp


	def calc_jw_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 spectral density values for isotropic rotational diffusion."

		a = self.data.s2 / (1.0 + self.data.omega_tm_sqrd[i, frq_index])
		b = (1.0 - self.data.s2) * self.data.ae_plus_c_tm * self.data.ae / (self.data.ae_plus_c_tm_sqrd + self.data.omega_tm_ae_sqrd[i, frq_index])
		temp = 0.4 * self.data.tm * (a + b)
		return temp


	def calc_jw_iso_m5(self, i, frq_index):
		"Calculate the model 5 spectral density values for isotropic rotational diffusion."

		a = self.data.s2s / (1.0 + self.data.omega_tm_sqrd[i, frq_index])
		b = (1.0 - self.data.s2s) * self.data.as_plus_c_tm * self.data.as / (self.data.as_plus_c_tm_sqrd + self.data.omega_tm_as_sqrd[i, frq_index])
		temp = 0.4 * self.data.tm * self.data.s2f * (a + b)
		return temp


	def initialise_jw_values(self):
		"Remap the parameters in self.data.params"

		# Isotropic dependent values.
		if match(self.data.diff_type, 'iso'):
			self.data.tm = self.data.diff_params[0]
			self.data.tm_sqrd = self.data.tm ** 2
			self.data.omega_tm_sqrd = zeros((self.relax.data.num_frq, 5), Float64)

		# Diffusion independent values.
		if match('m[13]', self.data.model):
			self.data.s2 = self.data.params[0]

		elif match('m[24]', self.data.model):
			self.data.s2 = self.data.params[0]
			self.data.ae = self.data.params[1]
			self.data.ae_plus_c_tm = self.data.ae + self.data.c * self.data.tm
			self.data.ae_plus_c_tm_sqrd = self.data.ae_plus_c_tm ** 2
			self.data.omega_tm_ae_sqrd = zeros((self.relax.data.num_frq, 5), Float64)

		elif match('m5', self.data.model):
			self.data.s2f = self.data.params[0]
			self.data.s2s = self.data.params[1]
			self.data.s2 = self.data.s2f * self.data.s2s
			self.data.as = self.data.params[2]
			self.data.as_plus_c_tm = self.data.as + self.data.c * self.data.tm
			self.data.as_plus_c_tm_sqrd = self.data.as_plus_c_tm ** 2
			self.data.omega_tm_as_sqrd = zeros((self.relax.data.num_frq, 5), Float64)

		for i in range(self.relax.data.num_frq):
			for frq_index in range(5):
				self.data.omega_tm_sqrd[i, frq_index] = self.relax.data.frq_sqrd_list[i][frq_index] * self.data.tm_sqrd
				if match('m[24]', self.data.model):
					self.data.omega_tm_ae_sqrd[i, frq_index] = (self.relax.data.frq_list[i][frq_index] * self.data.tm * self.data.ae)**2
				elif match('m5', self.data.model):
					self.data.omega_tm_as_sqrd[i, frq_index] = (self.relax.data.frq_list[i][frq_index] * self.data.tm * self.data.as)**2
