from Numeric import Float64, copy, zeros
from re import match

from jw_mf import *


class mf:
	def __init__(self, relax, equation=None, param_types, scaling=None, print_flag=0):
		"""asdf

		"""

		# Arguments.
		self.relax = relax
		self.equation = equation
		self.param_types = param_types
		self.scaling = scaling
		self.print_flag = print_flag

		# Setup the equations.
		if not self.setup_equations():
			print "The model-free equations could not be setup."
			return 0
		return 1


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
				elif match('Bond length', self.param_types[i]):
					self.r_index = i
				elif match('CSA', self.param_types[i]):
					self.csa_index = i
				else:
					return 0

			# Setup the equations for the calculation of spectral density values.
			if self.s2_index and self.te_index:
				self.calc_jw = calc_iso_jw_s2_te
				self.calc_jw_data = calc_iso_jw_s2_te_data
				self.data.mf_indecies = [self.s2_index, self.te_index]
			elif self.s2_index and not self.te_index:
				self.calc_jw = calc_iso_jw_s2
				self.calc_jw_data = calc_iso_jw_s2_data
				self.data.mf_indecies = [self.s2_index]
			elif not self.s2_index and self.te_index:
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
				elif match('Bond length', self.param_types[i]):
					self.r_index = i
				elif match('CSA', self.param_types[i]):
					self.csa_index = i
				else: return 0

			# Setup the equations for the calculation of spectral density values.
			if self.s2f_index and self.tf_index and self.s2s_index and self.ts_index:
				self.calc_jw = calc_iso_jw_s2f_tf_s2s_ts
				self.calc_jw_data = calc_iso_jw_s2f_tf_s2s_ts_data
				self.data.mf_indecies = [self.s2f_index, self.tf_index, self.s2s_index, self.ts_index]
			elif self.s2f_index and not self.tf_index and self.s2s_index and self.ts_index:
				self.calc_jw = calc_iso_jw_s2f_s2s_ts
				self.calc_jw_data = calc_iso_jw_s2f_s2s_ts_data
				self.data.mf_indecies = [self.s2f_index, self.s2s_index, self.ts_index]
			else:
				print "Invalid combination of parameters for the extended model-free equation."
				return 0

			self.data.ri_indecies = [self.r_index, self.csa_index]

		else:
			return 0
		return 1
