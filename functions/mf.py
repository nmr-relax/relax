from Numeric import Float64, ones, outerproduct, sum, zeros
from math import pi
from re import match

from data import data

from jw_mf_comps import *
from jw_mf import *
from ri_comps import *
from ri_prime import *
from ri import *
from chi2 import *


class mf:
	def __init__(self, relax, equation=None, param_types=None, init_params=None, relax_data=None, errors=None, bond_length=None, csa=None, diff_type=None, diff_params=None, scaling_vector=None, print_flag=0):
		"""The model-free minimisation class.

		This class should be initialised before every calculation.

		Arguments
		~~~~~~~~~

		relax:		The program base class self.relax
		equation:	The model-free equation string which should be either 'mf_orig' or 'mf_ext'.
		param_types:	An array of the parameter types used in minimisation.
		relax_data:	An array containing the experimental relaxation values.
		errors:		An array containing the experimental errors.
		bond_length:	The fixed bond length in meters.
		csa:		The fixed CSA value.
		diff_type:	The diffusion tensor string which should be either 'iso', 'axial', or 'aniso'.
		diff_params:	An array with the diffusion parameters.
		scaling_vector:	An array with the factors by which to scale the parameter vector.
		print_flag:	A flag specifying how much should be printed to screen.


		"""

		# Arguments.
		self.relax = relax
		self.equation = equation
		self.param_types = param_types
		self.params = init_params
		self.scaling_vector = scaling_vector
		self.print_flag = print_flag

		# Initialise the data class used to store data.
		self.data = data()

		# Calculate the five frequencies per field strength which cause R1, R2, and NOE relaxation.
		self.calc_frq_list()

		# Initialise the data.
		self.data.params = zeros(len(init_params), Float64)
		self.data.func_test = pi * ones(len(init_params), Float64)
		self.data.grad_test = pi * ones(len(init_params), Float64)
		self.data.hess_test = pi * ones(len(init_params), Float64)
		self.data.relax_data = relax_data
		self.data.errors = errors
		self.data.bond_length = bond_length
		self.data.csa = csa
		self.data.diff_type = diff_type
		self.data.diff_params = diff_params
		self.init_data()

		# Set the functions.
		if self.scaling_vector:
			self.scaling_flag = 1
			self.set_params = self.set_params_scaled
		else:
			self.scaling_flag = 0
			self.set_params = self.set_params_unscaled

		# Setup the equations.
		if not self.setup_equations():
			print "The model-free equations could not be setup."

		# Initialise the R1 data class used only if an NOE data set is collected but the R1 data of the same frequency has not.
		self.init_r1_data()


	def calc_frq_list(self):
		"Calculate the five frequencies per field strength which cause R1, R2, and NOE relaxation."

		self.data.frq_list = zeros((self.relax.data.num_frq, 5), Float64)
		for i in range(self.relax.data.num_frq):
			frqH = 2.0 * pi * self.relax.data.frq[i]
			frqX = frqH * (self.relax.data.gx / self.relax.data.gh)
			self.data.frq_list[i, 1] = frqX
			self.data.frq_list[i, 2] = frqH - frqX
			self.data.frq_list[i, 3] = frqH
			self.data.frq_list[i, 4] = frqH + frqX

		self.data.frq_sqrd_list = self.data.frq_list ** 2


	def func(self, params, print_flag=0):
		"""The function for calculating the model-free chi-squared value.

		The chi-sqared equation
		~~~~~~~~~~~~~~~~~~~~~~~
		        _n_
		        \    (Ri - Ri()) ** 2
		Chi2  =  >   ----------------
		        /__    sigma_i ** 2
		        i=1

		where:
			Ri are the values of the measured relaxation data set.
			Ri() are the values of the back calculated relaxation data set.
			sigma_i are the values of the error set.

		"""

		# Arguments
		self.set_params(params)
		self.print_flag = print_flag

		# Test if the function has already been calculated with these parameter values.
		if sum(self.data.params == self.data.func_test) == len(self.data.params):
			if len(self.data.params):
				return self.data.chi2

		# Store the parameter values in self.data.func_test for testing on next call if the function has already been calculated.
		self.data.func_test = self.data.params * 1.0

		# Calculate the spectral density values.
		if self.calc_jw_comps:
			self.calc_jw_comps(self.data)
		create_jw_struct(self.data, self.calc_jw)

		# Calculate the relaxation formula components.
		self.create_ri_comps(self.data, self.create_dip_func, self.create_dip_jw_func, self.create_csa_func, self.create_csa_jw_func, self.create_rex_func)

		# Calculate the R1, R2, and sigma_noe values.
		self.create_ri_prime(self.data)

		# Calculate the R1, R2, and NOE values.
		self.data.ri = self.data.ri_prime * 1.0
		ri(self.data, self.create_ri, self.get_r1)

		# Calculate the chi-squared value.
		self.data.chi2 = chi2(self.data.relax_data, self.data.ri, self.data.errors)

		return self.data.chi2


	def dfunc(self, params, print_flag=0):
		"""The function for calculating the model-free chi-squared gradient vector.

		The chi-sqared gradient
		~~~~~~~~~~~~~~~~~~~~~~~
		               _n_
		 dChi2         \   /  Ri - Ri()      dRi()  \ 
		-------  =  -2  >  | ----------  .  ------- |
		dthetaj        /__ \ sigma_i**2     dthetaj /
		               i=1

		where:
			Ri are the values of the measured relaxation data set.
			Ri() are the values of the back calculated relaxation data set.
			sigma_i are the values of the error set.

		"""

		# Arguments
		self.set_params(params)
		self.print_flag = print_flag

		# Test if the gradient has already been calculated with these parameter values.
		if sum(self.data.params == self.data.grad_test) == len(self.data.params):
			if len(self.data.params):
				return self.data.dchi2

		# Test if the function has already been called
		if sum(self.data.params == self.data.func_test) != len(self.data.params):
			temp_chi2 = self.func(params, print_flag)

		# Store the parameter values in self.data.grad_test for testing on next call if the gradient has already been calculated.
		self.data.grad_test = self.data.params * 1.0

		# Calculate the spectral density gradients.
		if self.calc_djw_comps:
			self.calc_djw_comps(self.data)
		create_djw_struct(self.data, self.calc_djw)

		# Calculate the relaxation gradient components.
		self.create_dri_comps(self.data, self.create_dip_grad, self.create_dip_jw_grad, self.create_csa_grad, self.create_csa_jw_grad, self.create_rex_grad)

		# Calculate the R1, R2, and sigma_noe gradients.
		for i in range(len(self.data.params)):
			self.create_dri_prime[i](self.data, i)

		# Calculate the R1, R2, and NOE gradients.
		self.data.dri = self.data.dri_prime * 1.0
		dri(self.data, self.create_dri, self.get_dr1)

		# Calculate the chi-squared gradient.
		self.data.dchi2 = dchi2(self.data.relax_data, self.data.ri, self.data.dri, self.data.errors)

		# Diagonal scaling.
		if self.scaling_flag:
			self.scale_gradient()

		return self.data.dchi2


	def d2func(self, params, print_flag=0):
		"""The function for calculating the model-free chi-squared gradient vector.

		The chi-sqared Hessian
		~~~~~~~~~~~~~~~~~~~~~~
			                      _n_
			     d2chi2           \       1      /  dRi()     dRi()                         d2Ri()     \ 
			---------------  =  2  >  ---------- | ------- . -------  -  (Ri - Ri()) . --------------- |
			dthetaj.dthetak       /__ sigma_i**2 \ dthetaj   dthetak                   dthetaj.dthetak / 
			                      i=1

		where:
			Ri are the values of the measured relaxation data set.
			Ri() are the values of the back calculated relaxation data set.
			sigma_i are the values of the error set.

		"""

		# Arguments
		self.set_params(params)
		self.print_flag = print_flag

		# Test if the Hessian has already been calculated with these parameter values.
		if sum(self.data.params == self.data.hess_test) == len(self.data.params):
			if len(self.data.params):
				return self.data.d2chi2

		# Test if the gradient has already been called
		if sum(self.data.params == self.data.grad_test) != len(self.data.params):
			temp_dchi2 = self.dfunc(params, print_flag)

		# Store the parameter values in self.data.hess_test for testing on next call if the Hessian has already been calculated.
		self.data.hess_test = self.data.params * 1.0

		# Calculate the spectral density Hessians.
		create_d2jw_struct(self.data, self.calc_d2jw)

		# Calculate the relaxation Hessian components.
		self.create_d2ri_comps(self.data, self.create_dip_hess, self.create_dip_jw_hess, self.create_csa_hess, self.create_csa_jw_hess, None)

		# Calculate the R1, R2, and sigma_noe Hessians.
		for i in range(len(self.data.params)):
			for j in range(i + 1):
				if self.create_d2ri_prime[i][j]:
					self.create_d2ri_prime[i][j](self.data, i, j)

					# Make the Hessian symmetric.
					if i != j:
						self.data.d2ri_prime[:, j, i] = self.data.d2ri_prime[:, i, j]

		# Calculate the R1, R2, and NOE Hessians.
		self.data.d2ri = self.data.d2ri_prime * 1.0
		d2ri(self.data, self.create_d2ri, self.get_d2r1)

		# Calculate the chi-squared Hessian.
		self.data.d2chi2 = d2chi2(self.data.relax_data, self.data.ri, self.data.dri, self.data.d2ri, self.data.errors)

		# Diagonal scaling.
		if self.scaling_flag:
			self.scale_hessian()

		return self.data.d2chi2


	def init_data(self):
		"Function for initialisation of the data."

		# Place some data structures from self.relax.data into the data class
		self.data.gh = self.relax.data.gh
		self.data.gx = self.relax.data.gx
		self.data.g_ratio = self.relax.data.g_ratio
		self.data.h_bar = self.relax.data.h_bar
		self.data.mu0 = self.relax.data.mu0
		self.data.num_ri = self.relax.data.num_ri
		self.data.num_frq = self.relax.data.num_frq
		self.data.frq = self.relax.data.frq
		self.data.remap_table = self.relax.data.remap_table
		self.data.noe_r1_table = self.relax.data.noe_r1_table
		self.data.ri_labels = self.relax.data.ri_labels

		# Diagonal scaling data.
		if self.scaling_vector:
			self.data.scaling_vector = self.scaling_vector
			self.data.scaling_matrix = outerproduct(self.scaling_vector, self.scaling_vector)

		# Spectral density components.
		self.data.w_tm_sqrd = zeros((self.data.num_frq, 5), Float64)
		self.data.fact_tm = zeros((self.data.num_frq, 5), Float64)
		self.data.w_tm_sqrd = self.data.frq_sqrd_list * self.data.diff_params[0] ** 2
		self.data.fact_tm = 1.0 / (1.0 + self.data.w_tm_sqrd)
		self.data.w_te_tm_sqrd = zeros((self.data.num_frq, 5), Float64)
		self.data.te_denom = zeros((self.data.num_frq, 5), Float64)
		self.data.two_fifths_tm = 0.4 * self.data.diff_params[0]
		self.data.two_fifths_tm_sqrd = 0.4 * self.data.diff_params[0] ** 2

		# Spectral density values, gradients, and Hessians.
		self.data.jw = zeros((self.relax.data.num_frq, 5), Float64)
		self.data.djw = zeros((self.relax.data.num_frq, 5, len(self.params)), Float64)
		self.data.d2jw = zeros((self.relax.data.num_frq, 5, len(self.params), len(self.params)), Float64)

		# Calculate the fixed components of the dipolar and CSA constants.
		calc_fixed_csa(self.data)
		calc_fixed_dip(self.data)

		# Dipolar and CSA constants.
		self.data.dip_const_func = 0.0
		self.data.dip_const_grad = 0.0
		self.data.dip_const_hess = 0.0
		self.data.csa_const_func = zeros((self.relax.data.num_frq), Float64)
		self.data.csa_const_grad = zeros((self.relax.data.num_frq), Float64)
		self.data.csa_const_hess = zeros((self.relax.data.num_frq), Float64)

		# Components of the transformed relaxation equations.
		self.data.dip_comps_func = zeros((self.relax.data.num_ri), Float64)
		self.data.csa_comps_func = zeros((self.relax.data.num_ri), Float64)
		self.data.rex_comps_func = zeros((self.relax.data.num_ri), Float64)
		self.data.dip_jw_comps_func = zeros((self.relax.data.num_ri), Float64)
		self.data.csa_jw_comps_func = zeros((self.relax.data.num_ri), Float64)

		# Initialise the first partial derivative components of the transformed relaxation equations.
		self.data.dip_comps_grad = zeros((self.relax.data.num_ri), Float64)
		self.data.csa_comps_grad = zeros((self.relax.data.num_ri), Float64)
		self.data.rex_comps_grad = zeros((self.relax.data.num_ri), Float64)
		self.data.dip_jw_comps_grad = zeros((self.relax.data.num_ri, len(self.params)), Float64)
		self.data.csa_jw_comps_grad = zeros((self.relax.data.num_ri, len(self.params)), Float64)

		# Initialise the first partial derivative components of the transformed relaxation equations.
		self.data.dip_comps_hess = zeros((self.relax.data.num_ri), Float64)
		self.data.csa_comps_hess = zeros((self.relax.data.num_ri), Float64)
		self.data.rex_comps_hess = zeros((self.relax.data.num_ri), Float64)
		self.data.dip_jw_comps_hess = zeros((self.relax.data.num_ri, len(self.params), len(self.params)), Float64)
		self.data.csa_jw_comps_hess = zeros((self.relax.data.num_ri, len(self.params), len(self.params)), Float64)

		# Initialise the transformed relaxation values, gradients, and Hessians.
		self.data.ri_prime = zeros((self.relax.data.num_ri), Float64)
		self.data.dri_prime = zeros((self.relax.data.num_ri, len(self.params)), Float64)
		self.data.d2ri_prime = zeros((self.relax.data.num_ri, len(self.params), len(self.params)), Float64)

		# Initialise the data structures containing the R1 values at the position of and corresponding to the NOE.
		self.data.r1 = zeros((self.relax.data.num_ri), Float64)
		self.data.dr1 = zeros((self.relax.data.num_ri, len(self.params)), Float64)
		self.data.d2r1 = zeros((self.relax.data.num_ri, len(self.params), len(self.params)), Float64)


	def init_r1_data(self):
		"""Function for initialisation of the R1 data class.

		This data class is only used if an NOE data set is collected but no R1 data set corresponding to the same frequency exists.
		"""

		self.data.r1_data = data()
		self.data.r1_data.num_frq = self.data.num_frq
		self.data.r1_data.dip_const_fixed = self.data.dip_const_fixed
		self.data.r1_data.csa_const_fixed = self.data.csa_const_fixed

		# Components of the transformed relaxation equations.
		self.data.r1_data.dip_comps_func = zeros((self.relax.data.num_ri), Float64)
		self.data.r1_data.csa_comps_func = zeros((self.relax.data.num_ri), Float64)
		self.data.r1_data.dip_jw_comps_func = zeros((self.relax.data.num_ri), Float64)
		self.data.r1_data.csa_jw_comps_func = zeros((self.relax.data.num_ri), Float64)

		# Initialise the first partial derivative components of the transformed relaxation equations.
		self.data.r1_data.dip_comps_grad = zeros((self.relax.data.num_ri), Float64)
		self.data.r1_data.csa_comps_grad = zeros((self.relax.data.num_ri), Float64)
		self.data.r1_data.rex_comps_grad = zeros((self.relax.data.num_ri), Float64)
		self.data.r1_data.dip_jw_comps_grad = zeros((self.relax.data.num_ri, len(self.params)), Float64)
		self.data.r1_data.csa_jw_comps_grad = zeros((self.relax.data.num_ri, len(self.params)), Float64)

		# Initialise the first partial derivative components of the transformed relaxation equations.
		self.data.r1_data.dip_comps_hess = zeros((self.relax.data.num_ri), Float64)
		self.data.r1_data.csa_comps_hess = zeros((self.relax.data.num_ri), Float64)
		self.data.r1_data.rex_comps_hess = zeros((self.relax.data.num_ri), Float64)
		self.data.r1_data.dip_jw_comps_hess = zeros((self.relax.data.num_ri, len(self.params), len(self.params)), Float64)
		self.data.r1_data.csa_jw_comps_hess = zeros((self.relax.data.num_ri, len(self.params), len(self.params)), Float64)

		# Initialise the transformed relaxation values, gradients, and Hessians.
		self.data.r1_data.ri_prime = zeros((self.relax.data.num_ri), Float64)
		self.data.r1_data.dri_prime = zeros((self.relax.data.num_ri, len(self.params)), Float64)
		self.data.r1_data.d2ri_prime = zeros((self.relax.data.num_ri, len(self.params), len(self.params)), Float64)

		# Place a few function pointer arrays in the data class for the calculation of the R1 value when an NOE data set exists but the R1 set does not.
		self.data.r1_data.create_dri_prime = self.create_dri_prime
		self.data.r1_data.create_d2ri_prime = self.create_d2ri_prime

		self.data.r1_data.csa_index = self.data.csa_index
		self.data.r1_data.r_index = self.data.r_index
		self.data.r1_data.rex_index = self.data.rex_index


	def lm_dri(self):
		"Return the function used for Levenberg-Marquardt minimisation."

		# Diagonal scaling.
		if self.scaling_flag:
			return self.data.dri * self.data.scaling_vector
		else:
			return self.data.dri


	def scale_gradient(self):
		"Function for the diagonal scaling of the chi-squared gradient."

		self.data.dchi2 = self.data.dchi2 * self.data.scaling_vector


	def scale_hessian(self):
		"Function for the diagonal scaling of the chi-squared gradient."

		self.data.d2chi2 = self.data.d2chi2 * self.data.scaling_matrix


	def set_params_scaled(self, params):
		"Function for setting self.data.params to the parameter vector multiplied with the scaling vector"

		self.data.params = params * self.data.scaling_vector


	def set_params_unscaled(self, params):
		"Function for setting self.data.params to the parameter vector"

		self.data.params = params * 1.0


	def setup_equations(self):
		"Setup the equations used to calculate the chi-squared statistic."

		# Initialise the spectral density gradient and Hessian function lists.
		self.calc_djw = []
		self.calc_d2jw = []
		for i in range(len(self.params)):
			self.calc_djw.append(None)
			self.calc_d2jw.append([])
			for j in range(len(self.params)):
				self.calc_d2jw[i].append(None)


		# The original model-free equations.
		####################################

		if match('mf_orig', self.equation):
			# Find the indecies of the parameters in self.param_types
			self.data.s2_index, self.data.te_index, self.data.rex_index, self.data.r_index, self.data.csa_index = None, None, None, None, None
			for i in range(len(self.param_types)):
				if match('S2', self.param_types[i]):
					self.data.s2_index = i
				elif match('te', self.param_types[i]):
					self.data.te_index = i
				elif match('Rex', self.param_types[i]):
					self.data.rex_index = i
				elif match('Bond length', self.param_types[i]):
					self.data.r_index = i
				elif match('CSA', self.param_types[i]):
					self.data.csa_index = i
				else:
					return 0

			# Setup the equations for the calculation of spectral density values.
			if self.data.s2_index != None and self.data.te_index != None:
				self.calc_jw = calc_iso_s2_te_jw
				self.calc_jw_comps = calc_iso_s2_te_jw_comps
				self.calc_djw_comps = calc_iso_s2_te_djw_comps
				self.calc_djw[self.data.s2_index] = calc_iso_S2_te_djw_dS2
				self.calc_djw[self.data.te_index] = calc_iso_S2_te_djw_dte
				self.calc_d2jw[self.data.s2_index][self.data.te_index] = self.calc_d2jw[self.data.te_index][self.data.s2_index] = calc_iso_S2_te_d2jw_dS2dte
				self.calc_d2jw[self.data.te_index][self.data.te_index] = calc_iso_S2_te_d2jw_dte2
			elif self.data.s2_index != None:
				self.calc_jw = calc_iso_s2_jw
				self.calc_jw_comps = None
				self.calc_djw_comps = None
				self.calc_djw[self.data.s2_index] = calc_iso_S2_djw_dS2
			elif self.data.te_index != None and self.data.s2_index == None:
				print "Invalid model, you cannot have te as a parameter without S2 existing as well."
				return 0
			else:
				self.calc_jw = calc_iso_jw
				self.calc_jw_comps = None
				self.calc_djw_comps = None

		# The extended model-free equations.
		####################################

		elif match('mf_ext', self.equation):
			# Find the indecies of the parameters in self.param_types
			self.data.s2f_index, self.data.tf_index, self.data.s2s_index, self.data.ts_index, self.data.rex_index, self.data.r_index, self.data.csa_index,  = None, None, None, None, None, None, None
			for i in range(len(self.param_types)):
				if match('S2f', self.param_types[i]):
					self.data.s2f_index = i
				elif match('tf', self.param_types[i]):
					self.data.tf_index = i
				elif match('S2s', self.param_types[i]):
					self.data.s2s_index = i
				elif match('ts', self.param_types[i]):
					self.data.ts_index = i
				elif match('Rex', self.param_types[i]):
					self.data.rex_index = i
				elif match('Bond length', self.param_types[i]):
					self.data.r_index = i
				elif match('CSA', self.param_types[i]):
					self.data.csa_index = i
				else: return 0

			# Setup the equations for the calculation of spectral density values.
			if self.data.s2f_index != None and self.data.tf_index != None and self.data.s2s_index != None and self.data.ts_index != None:
				self.calc_jw = calc_iso_s2f_tf_s2s_ts_jw
				self.calc_jw_comps = calc_iso_s2f_tf_s2s_ts_jw_comps
				self.calc_djw_comps = calc_iso_s2f_tf_s2s_ts_djw_comps
				self.calc_djw[self.data.s2f_index] = calc_iso_S2f_tf_S2s_ts_djw_dS2f
				self.calc_djw[self.data.tf_index] = calc_iso_S2f_tf_S2s_ts_djw_dtf
				self.calc_djw[self.data.s2s_index] = calc_iso_S2f_tf_S2s_ts_djw_dS2s
				self.calc_djw[self.data.ts_index] = calc_iso_S2f_tf_S2s_ts_djw_dts
				self.calc_d2jw[self.data.s2f_index][self.data.s2s_index] = self.calc_d2jw[self.data.s2s_index][self.data.s2f_index] = calc_iso_S2f_tf_S2s_ts_d2jw_dS2fdS2s
				self.calc_d2jw[self.data.s2f_index][self.data.tf_index] = self.calc_d2jw[self.data.tf_index][self.data.s2f_index] = calc_iso_S2f_tf_S2s_ts_d2jw_dS2fdtf
				self.calc_d2jw[self.data.s2f_index][self.data.ts_index] = self.calc_d2jw[self.data.ts_index][self.data.s2f_index] = calc_iso_S2f_tf_S2s_ts_d2jw_dS2fdts
				self.calc_d2jw[self.data.s2s_index][self.data.ts_index] = self.calc_d2jw[self.data.ts_index][self.data.s2s_index] = calc_iso_S2f_tf_S2s_ts_d2jw_dS2sdts
				self.calc_d2jw[self.data.tf_index][self.data.tf_index] = calc_iso_S2f_tf_S2s_ts_d2jw_dtf2
				self.calc_d2jw[self.data.ts_index][self.data.ts_index] = calc_iso_S2f_tf_S2s_ts_d2jw_dts2
			elif self.data.s2f_index != None and self.data.tf_index == None and self.data.s2s_index != None and self.data.ts_index != None:
				self.calc_jw = calc_iso_s2f_s2s_ts_jw
				self.calc_jw_comps = calc_iso_s2f_s2s_ts_jw_comps
				self.calc_djw_comps = calc_iso_s2f_s2s_ts_djw_comps
				self.calc_djw[self.data.s2f_index] = calc_iso_S2f_S2s_ts_djw_dS2f
				self.calc_djw[self.data.s2s_index] = calc_iso_S2f_S2s_ts_djw_dS2s
				self.calc_djw[self.data.ts_index] = calc_iso_S2f_S2s_ts_djw_dts
				self.calc_d2jw[self.data.s2f_index][self.data.s2s_index] = self.calc_d2jw[self.data.s2s_index][self.data.s2f_index] = calc_iso_S2f_S2s_ts_d2jw_dS2fdS2s
				self.calc_d2jw[self.data.s2f_index][self.data.ts_index] = self.calc_d2jw[self.data.ts_index][self.data.s2f_index] = calc_iso_S2f_S2s_ts_d2jw_dS2fdts
				self.calc_d2jw[self.data.s2s_index][self.data.ts_index] = self.calc_d2jw[self.data.ts_index][self.data.s2s_index] = calc_iso_S2f_S2s_ts_d2jw_dS2sdts
				self.calc_d2jw[self.data.ts_index][self.data.ts_index] = calc_iso_S2f_S2s_ts_d2jw_dts2
			else:
				print "Invalid combination of parameters for the extended model-free equation."
				return 0

		else:
			return 0


		# Initialise function pointer data structures.
		##############################################

		# Relaxation equation components.
		self.create_dip_func = []
		self.create_dip_grad = []
		self.create_dip_hess = []
		self.create_csa_func = []
		self.create_csa_grad = []
		self.create_csa_hess = []
		self.create_rex_func = []
		self.create_rex_grad = []

		self.create_dip_jw_func = []
		self.create_dip_jw_grad = []
		self.create_dip_jw_hess = []
		self.create_csa_jw_func = []
		self.create_csa_jw_grad = []
		self.create_csa_jw_hess = []

		# Ri'
		self.create_ri_prime = None
		self.create_dri_prime = []
		self.create_d2ri_prime = []

		# Ri
		self.create_ri = []
		self.create_dri = []
		self.create_d2ri = []

		self.get_r1 = []
		self.get_dr1 = []
		self.get_d2r1 = []

		# Fill the structures with None.
		for i in range(self.relax.data.num_ri):
			self.create_dip_func.append(None)
			self.create_dip_grad.append(None)
			self.create_dip_hess.append(None)
			self.create_csa_func.append(None)
			self.create_csa_grad.append(None)
			self.create_csa_hess.append(None)
			self.create_rex_func.append(None)
			self.create_rex_grad.append(None)
			self.create_dip_jw_func.append(None)
			self.create_dip_jw_grad.append(None)
			self.create_dip_jw_hess.append(None)
			self.create_csa_jw_func.append(None)
			self.create_csa_jw_grad.append(None)
			self.create_csa_jw_hess.append(None)
			self.create_ri.append(None)
			self.create_dri.append(None)
			self.create_d2ri.append(None)
			self.get_r1.append(None)
			self.get_dr1.append(None)
			self.get_d2r1.append(None)


		# Make pointers to the functions for the calculation of ri_prime, dri_prime, and d2ri_prime components.
		#######################################################################################################

		for i in range(self.relax.data.num_ri):
			# The R1 equations.
			if self.relax.data.ri_labels[i] == 'R1':
				self.create_csa_func[i] = comp_r1_csa_const
				self.create_csa_grad[i] = comp_r1_csa_const
				self.create_csa_hess[i] = comp_r1_csa_const
				self.create_dip_jw_func[i] = comp_r1_dip_jw
				self.create_dip_jw_grad[i] = comp_r1_dip_jw
				self.create_dip_jw_hess[i] = comp_r1_dip_jw
				self.create_csa_jw_func[i] = comp_r1_csa_jw
				self.create_csa_jw_grad[i] = comp_r1_csa_jw
				self.create_csa_jw_hess[i] = comp_r1_csa_jw

			# The R2 equations.
			elif self.relax.data.ri_labels[i] == 'R2':
				self.create_dip_func[i] = comp_r2_dip_const
				self.create_dip_grad[i] = comp_r2_dip_const
				self.create_dip_hess[i] = comp_r2_dip_const
				self.create_csa_func[i] = comp_r2_csa_const
				self.create_csa_grad[i] = comp_r2_csa_const
				self.create_csa_hess[i] = comp_r2_csa_const
				self.create_rex_func[i] = comp_rex_const_func
				self.create_rex_grad[i] = comp_rex_const_grad
				self.create_dip_jw_func[i] = comp_r2_dip_jw
				self.create_dip_jw_grad[i] = comp_r2_dip_jw
				self.create_dip_jw_hess[i] = comp_r2_dip_jw
				self.create_csa_jw_func[i] = comp_r2_csa_jw
				self.create_csa_jw_grad[i] = comp_r2_csa_jw
				self.create_csa_jw_hess[i] = comp_r2_csa_jw

			# The NOE equations.
			elif self.relax.data.ri_labels[i] == 'NOE':
				self.create_dip_jw_func[i] = comp_sigma_noe_dip_jw
				self.create_dip_jw_grad[i] = comp_sigma_noe_dip_jw
				self.create_dip_jw_hess[i] = comp_sigma_noe_dip_jw
				self.create_ri[i] = calc_noe
				self.create_dri[i] = calc_dnoe
				self.create_d2ri[i] = calc_d2noe
				if self.relax.data.noe_r1_table[i] == None:
					self.get_r1[i] = calc_r1
					self.get_dr1[i] = calc_dr1
					self.get_d2r1[i] = calc_d2r1
				else:
					self.get_r1[i] = extract_r1
					self.get_dr1[i] = extract_dr1
					self.get_d2r1[i] = extract_d2r1


		# Make pointers to the functions for the calculation of ri_prime, dri_prime, and d2ri_prime.
		############################################################################################

		# ri_prime.
		if self.data.rex_index == None:
			self.create_ri_prime = func_ri_prime
		else:
			self.create_ri_prime = func_ri_prime_rex

		# dri_prime and d2ri_prime.
		for i in range(len(self.data.params)):
			if match('Rex', self.param_types[i]):
				self.create_dri_prime.append(func_dri_drex_prime)
				self.create_d2ri_prime.append([])
				for j in range(len(self.data.params)):
					if match('Rex', self.param_types[j]):
						self.create_d2ri_prime[i].append(None)
					elif match('Bond length', self.param_types[j]):
						self.create_d2ri_prime[i].append(None)
					elif match('CSA', self.param_types[j]):
						self.create_d2ri_prime[i].append(None)
					else:
						self.create_d2ri_prime[i].append(None)
			elif match('Bond length', self.param_types[i]):
				self.create_dri_prime.append(func_dri_dr_prime)
				self.create_d2ri_prime.append([])
				for j in range(len(self.data.params)):
					if match('Rex', self.param_types[j]):
						self.create_d2ri_prime[i].append(None)
					elif match('Bond length', self.param_types[j]):
						self.create_d2ri_prime[i].append(func_d2ri_dr2_prime)
					elif match('CSA', self.param_types[j]):
						self.create_d2ri_prime[i].append(None)
					else:
						self.create_d2ri_prime[i].append(func_d2ri_drdjw_prime)
			elif match('CSA', self.param_types[i]):
				self.create_dri_prime.append(func_dri_dcsa_prime)
				self.create_d2ri_prime.append([])
				for j in range(len(self.data.params)):
					if match('Rex', self.param_types[j]):
						self.create_d2ri_prime[i].append(None)
					elif match('Bond length', self.param_types[j]):
						self.create_d2ri_prime[i].append(None)
					elif match('CSA', self.param_types[j]):
						self.create_d2ri_prime[i].append(func_d2ri_dcsa2_prime)
					else:
						self.create_d2ri_prime[i].append(func_d2ri_dcsadjw_prime)
			else:
				self.create_dri_prime.append(func_dri_djw_prime)
				self.create_d2ri_prime.append([])
				for j in range(len(self.data.params)):
					if match('Rex', self.param_types[j]):
						self.create_d2ri_prime[i].append(None)
					elif match('Bond length', self.param_types[j]):
						self.create_d2ri_prime[i].append(func_d2ri_djwdr_prime)
					elif match('CSA', self.param_types[j]):
						self.create_d2ri_prime[i].append(func_d2ri_djwdcsa_prime)
					else:
						self.create_d2ri_prime[i].append(func_d2ri_djwidjwj_prime)


		# Both the bond length and CSA are fixed.
		#########################################

		if self.data.r_index == None and self.data.csa_index == None:
			# The main ri component functions
			if self.data.rex_index == None:
				self.create_ri_comps = ri_comps
				self.create_dri_comps = dri_comps
				self.create_d2ri_comps = d2ri_comps
			else:
				self.create_ri_comps = ri_comps_rex
				self.create_dri_comps = dri_comps_rex
				self.create_d2ri_comps = d2ri_comps

			# Calculate the dipolar and CSA constant components.
			comp_dip_const_func(self.data, self.data.bond_length)
			comp_csa_const_func(self.data, self.data.csa)
			for i in range(self.data.num_ri):
				self.data.dip_comps_func[i] = self.data.dip_const_func
				if self.create_dip_func[i]:
					self.data.dip_comps_func[i] = self.create_dip_func[i](self.data.dip_const_func)
				if self.create_csa_func[i]:
					self.data.csa_comps_func[i] = self.create_csa_func[i](self.data.csa_const_func[self.data.remap_table[i]])


		# The bond length is a parameter.
		#################################

		elif self.data.r_index != None and self.data.csa_index == None:
			# The main ri component functions
			if self.data.rex_index == None:
				self.create_ri_comps = ri_comps_r
				self.create_dri_comps = dri_comps_r
				self.create_d2ri_comps = d2ri_comps_r
			else:
				self.create_ri_comps = ri_comps_r_rex
				self.create_dri_comps = dri_comps_r_rex
				self.create_d2ri_comps = d2ri_comps_r

			# Calculate the CSA constant.
			comp_csa_const_func(self.data, self.data.csa)
			for i in range(self.data.num_ri):
				if self.create_csa_func[i]:
					self.data.csa_comps_func[i] = self.create_csa_func[i](self.data.csa_const_func[self.data.remap_table[i]])


		# The CSA is a parameter.
		#########################

		elif self.data.r_index == None and self.data.csa_index != None:
			# The main ri component functions
			if self.data.rex_index == None:
				self.create_ri_comps = ri_comps_csa
				self.create_dri_comps = dri_comps_csa
				self.create_d2ri_comps = d2ri_comps_csa
			else:
				self.create_ri_comps = ri_comps_csa_rex
				self.create_dri_comps = dri_comps_csa_rex
				self.create_d2ri_comps = d2ri_comps_csa

			# Calculate the dipolar constant.
			comp_dip_const_func(self.data, self.data.bond_length)
			for i in range(self.data.num_ri):
				self.data.dip_comps_func[i] = self.data.dip_const_func
				if self.create_dip_func[i]:
					self.data.dip_comps_func[i] = self.create_dip_func[i](self.data.dip_const_func)


		# Both the bond length and CSA are parameters.
		##############################################

		elif self.data.r_index != None and self.data.csa_index != None:
			# The main ri component functions
			if self.data.rex_index == None:
				self.create_ri_comps = ri_comps_r_csa
				self.create_dri_comps = dri_comps_r_csa
				self.create_d2ri_comps = d2ri_comps_r_csa
			else:
				self.create_ri_comps = ri_comps_r_csa_rex
				self.create_dri_comps = dri_comps_r_csa_rex
				self.create_d2ri_comps = d2ri_comps_r_csa


		# Invalid combination of parameters.
		####################################

		else:
			print "Invalid combination of parameters for the model-free equations."
			return 0

		return 1
