from math import pi
from re import match

from data import data
from jw_mf import *
from ri_prime import *


class mf:
	def __init__(self, relax, equation=None, param_types=None, bond_length=None, csa=None, scaling=None, print_flag=0):
		"""asdf

		"""

		# Arguments.
		self.relax = relax
		self.equation = equation
		self.param_types = param_types
		self.bond_length = bond_length
		self.csa = csa
		self.scaling = scaling
		self.print_flag = print_flag

		# Initialise the data.
		self.init_data()

		# Calculate the five frequencies per field strength which cause R1, R2, and NOE relaxation.
		self.calc_frq_list()

		calc_ri_constants(self.data)

		# Setup the equations.
		if not self.setup_equations():
			print "The model-free equations could not be setup."


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


	def func(self, params, diff_type, diff_params, relax_data, errors, print_flag=0):
		"asdf"

		# Arguments
		self.data.params = params
		self.data.diff_type = diff_type
		self.data.diff_params = diff_params
		self.data.relax_data = relax_data
		self.data.errors = errors
		self.print_flag = print_flag

		self.calc_jw_data(self.data)
		create_jw_struct(self.data, self.calc_jw)
		print "dir(data): " + `dir(self.data)`
		print "J(w): " + `self.data.jw`

		calc_ri_prime(self.data, self.ri_funcs)
		print "dir(data): " + `dir(self.data)`
		print "Ri_prime: " + `self.data.ri_prime`
		import sys
		sys.exit()


	def dfunc(self, params, diff_type, diff_params, relax_data, errors, print_flag=0):
		"asdf"

	def d2func(self, params, diff_type, diff_params, relax_data, errors, print_flag=0):
		"asdf"


	def init_data(self):
		"Function for initialisation of the data."

		# Initialise the data class used to store data.
		self.data = data()

		self.data.bond_length = self.bond_length
		self.data.csa = self.csa
		# Place some data structures from self.relax.data into the data class
		self.data.gh = self.relax.data.gh
		self.data.gx = self.relax.data.gx
		self.data.h_bar = self.relax.data.h_bar
		self.data.mu0 = self.relax.data.mu0
		self.data.num_ri = self.relax.data.num_ri
		self.data.num_frq = self.relax.data.num_frq
		self.data.frq = self.relax.data.frq
		self.data.remap_table = self.relax.data.remap_table
		self.data.ri_labels = self.relax.data.ri_labels

		# Initialise the spectral density values.
		self.data.jw = zeros((self.relax.data.num_frq, 5), Float64)

		# Initialise the components of the transformed relaxation equations.
		self.data.dip_comps = zeros((self.relax.data.num_ri), Float64)
		self.data.j_dip_comps = zeros((self.relax.data.num_ri), Float64)
		self.data.csa_comps = zeros((self.relax.data.num_ri), Float64)
		self.data.j_csa_comps = zeros((self.relax.data.num_ri), Float64)
		self.data.rex_comps = zeros((self.relax.data.num_ri), Float64)

		# Initialise the transformed relaxation values.
		self.data.ri_prime = zeros((self.relax.data.num_ri), Float64)


	def lm_dri(self):
		"Return the function used for Levenberg-Marquardt minimisation."

		return self.data.dri


	def setup_equations(self):
		"Setup the equations used to calculate the chi-squared statistic."

		# The original model-free equations.
		if match('mf_orig', self.equation):
			# Find the indecies of the parameters in self.param_types
			self.r_index, self.csa_index, self.s2_index, self.te_index = None, None, None, None
			for i in range(len(self.param_types)):
				if match('S2', self.param_types[i]):
					self.s2_index = i
				elif match('te', self.param_types[i]):
					self.te_index = i
				elif match('Rex', self.param_types[i]):
					self.r_index = i
				elif match('CSA', self.param_types[i]):
					self.csa_index = i
				else:
					return 0

			# Setup the equations for the calculation of spectral density values.
			if not self.s2_index == None and not self.te_index == None:
				self.calc_jw = calc_iso_jw_s2_te
				self.calc_jw_data = calc_iso_jw_s2_te_data
				self.data.mf_indecies = [self.s2_index, self.te_index]
			elif not self.s2_index == None and self.te_index == None:
				self.calc_jw = calc_iso_jw_s2
				self.calc_jw_data = calc_iso_jw_s2_data
				self.data.mf_indecies = [self.s2_index]
			elif self.s2_index == None and not self.te_index == None:
				print "Invalid model, you cannot have te as a parameter without S2 existing as well."
				return 0
			else:
				print "Invalid combination of parameters for the original model-free equation."
				return 0

			# Package the indecies into a single structure.
			self.data.ri_indecies = [self.r_index, self.csa_index]

		# The extended model-free equations.
		elif match('mf_ext', self.equation):
			# Find the indecies of the parameters in self.param_types
			self.r_index, self.csa_index, self.s2f_index, self.tf_index, self.s2s_index, self.ts_index = None, None, None, None, None, None
			for i in range(len(self.param_types)):
				if match('S2f', self.param_types[i]):
					self.s2f_index = i
				elif match('tf', self.param_types[i]):
					self.tf_index = i
				elif match('S2s', self.param_types[i]):
					self.s2s_index = i
				elif match('ts', self.param_types[i]):
					self.ts_index = i
				elif match('Rex', self.param_types[i]):
					self.r_index = i
				elif match('CSA', self.param_types[i]):
					self.csa_index = i
				else: return 0

			# Setup the equations for the calculation of spectral density values.
			if not self.s2f_index == None and not self.tf_index == None and not self.s2s_index == None and not self.ts_index == None:
				self.calc_jw = calc_iso_jw_s2f_tf_s2s_ts
				self.calc_jw_data = calc_iso_jw_s2f_tf_s2s_ts_data
				self.data.mf_indecies = [self.s2f_index, self.tf_index, self.s2s_index, self.ts_index]
			elif not self.s2f_index == None and self.tf_index == None and not self.s2s_index == None and not self.ts_index == None:
				self.calc_jw = calc_iso_jw_s2f_s2s_ts
				self.calc_jw_data = calc_iso_jw_s2f_s2s_ts_data
				self.data.mf_indecies = [self.s2f_index, self.s2s_index, self.ts_index]
			else:
				print "Invalid combination of parameters for the extended model-free equation."
				return 0

			self.data.ri_indecies = [self.r_index, self.csa_index]

		else:
			return 0

		# The transformed relaxation equations.
		self.ri_funcs = []
		for i in range(self.relax.data.num_ri):
			if self.relax.data.ri_labels[i]  == 'R1':
				self.ri_funcs.append(calc_r1_prime)
			elif self.relax.data.ri_labels[i] == 'R2':
				if self.data.ri_indecies[0] == None:
					self.ri_funcs.append(calc_r2_prime)
				else:
					self.ri_funcs.append(calc_r2_rex_prime)
			elif self.relax.data.ri_labels[i] == 'NOE':
				self.ri_funcs.append(calc_sigma_noe)


		return 1
