#! /usr/bin/python

import sys
from math import pi
import math
from re import match


class map:
	def __init__(self):


		self.init_data()
		self.options = ['iso', [10.0 * 1e-9], 'm4']

		# Initialise the true data.
		self.create_true()

		# Create grid.
		print "[ Creating the grid ]"

		file = open('RG_grid', 'w')
		data_file = open('data', 'w')
		data_file2 = open('data2', 'w')

		grid_ops = []

		# alpha
		#######
		
		# S2.
		#grid_ops.append([20.0, 0.5, 1.0])

		# S2 * te
		grid_ops.append([20.0, 0.0, 10000.0 * 1e-12])

		# S2 + 1e9 * te
		#grid_ops.append([20.0, 0.0, 1e5])

		# S2 / (te + tm)
		#grid_ops.append([20.0, 0.0, 10e7])

		# beta
		######

		# te
		#grid_ops.append([20.0, 5000.0 * 1e-12, 10000.0 * 1e-12])

		# sqrt(tm + te)
		#grid_ops.append([20.0, 1.0 * 1e-4, 1.42 * 1e-4])

		# (tm + te)**0.0001
		#grid_ops.append([20.0, 0.9981, 0.9983])

		# te * S2
		#grid_ops.append([20.0, -5.0 * 1e-9, 5.0*1e-9])

		# -log(tm + te)
		#grid_ops.append([20.0, 10.0, 30.0])

		# 1 / (tm + te)
		grid_ops.append([20.0, 0.0, 10e7])

		# te**10
		#grid_ops.append([20.0, 0.0, 1e-80])

		# (1 - S2) * te
		#grid_ops.append([20.0, 0.0, 10000.0 * 1e-12])

		# te
		#grid_ops.append([20.0, -5e7, 5e7])

		# gamma
		#######

		# Rex
		grid_ops.append([20.0, 0.0, 3.0 / self.frq[0]**2])

		self.step_size = []
		for k in range(len(grid_ops)):
			step = (grid_ops[k][2] - grid_ops[k][1]) / (grid_ops[k][0] - 1)
			self.step_size.append(step)

		percent = 0.0
		print "%-19s%-4.3f" % ("Percentage done:", percent)
		percent_inc = 100.0 / ((grid_ops[0][0]) * (grid_ops[1][0]))

		alpha = grid_ops[0][1]
		for alpha_inc in range(grid_ops[0][0]):
			beta = grid_ops[1][1]
			for beta_inc in range(grid_ops[1][0]):
				gamma = grid_ops[2][1]
				for gamma_inc in range(grid_ops[2][0]):
					values = [alpha, beta, gamma]
					self.mf_values = self.remap(values)
					back_calc = self.Ri()
					chi2 = 0.0
					for i in range(self.num_ri):
						chi2 = chi2 + (self.values[i] - back_calc[i])**2 / self.errors[i]**2
					file.write("%30f\n" % chi2)
					data_file.write("%30s" % `self.mf_values[0]`)
					data_file.write("%30s" % `self.mf_values[1] * 1e12`)
					data_file.write("%30s" % `self.mf_values[2] * self.frq[0]**2`)
					data_file.write("%30g\n" % chi2)
					data_file2.write("%30s" % `alpha`)
					data_file2.write("%30s" % `beta`)
					data_file2.write("%30s" % `gamma`)
					data_file2.write("%30g\n" % chi2)
					# Increase gamma.
					gamma = gamma + self.step_size[2]
				percent = percent + percent_inc
				print "%-19s%-4.3f%20s%-8g" % ("Percentage done:", percent, "chi2: ", chi2)
				# Increase beta.
				beta = beta + self.step_size[1]
			# Increase alpha.
			alpha = alpha + self.step_size[0]
		print "Done\n"


	def remap(self, values):
		# S2
		####
 
		# S2
		#s2 = values[0]

		# alpha / te
		#s2 = values[0] / values[1]

		# alpha - 1e9 * te
		#s2 = values[0] - 1e12 * values[1]

		# alpha**(1/3)
		#s2 = values[0]**(1.0/4.0)

		# alpha / (1 - t_prime)
		#te = values[1]*self.options[1][0] / ( (1.0 - values[0])*self.options[1][0] + values[1])
		#if te == 0.0:
		#	t_prime = 0.0
		#else:
		#	t_prime = 1.0 / ( 1.0/self.options[1][0] + 1.0/te)
		#s2 = values[0] * (self.options[1][0] - t_prime)

		# alpha.beta / (1 - tm.beta)
		#if 1.0 - self.options[1][0] * values[1] == 0.0:
		#	s2 = 1e99
		#else:
		#	s2 = values[0] * values[1] / (1.0 - (self.options[1][0] * values[1]))

		# 0.5 * alpha / (alpha + beta)
		#if values[0] == 0.0:
		#	s2 = 0.0
		#elif (values[0] - values[1]) == 0.0:
		#	s2 = 1e99
		#else:
		#	s2 = 0.5 * values[0] / (values[0] - values[1])

		# alpha * (tm + (1-(alpha + beta).tm) / (alpha + beta))
		#if values[0] == 0.0:
		#	s2 = 0
		#elif (values[0] + values[1]) == 0.0:
		#	s2 = 1e99
		#else:
		#	s2 = values[0] * (self.options[1][0] + (1.0 - (values[0] + values[1]) * self.options[1][0]) / (values[0] + values[1]))

		# alpha(tm + beta)
		#s2 = values[0] * (self.options[1][0] + values[1])

		# 1 - alpha/beta
		#if values[0] == 0.0:
		#	s2 = 1
		#elif values[1] == 0.0:
		#	s2 = 1e99
		#else:
		#	s2 = 1.0 - values[0]/values[1]

		if values[0] == 0.0 or values[1] == 0.0:
			s2 = 1e99
		else:
			s2 = ((1.0 / values[1]) - self.options[1][0]) / values[0] - 1.0


		# te
		####

		# te
		#te = values[1]

		# beta / S2
		#te = values[1] / values[0]

		# e**-beta - tm
		#te = math.exp(-values[1]) - self.options[1][0]

		# 1/beta - tm
		if values[1] == 0.0:
			te = 1e99
		else:
			te = 1.0 / values[1] - self.options[1][0]

		# beta**2 - tm
		#te = values[1]**2 - self.options[1][0]

		# beta**10 - tm
		#te = values[1]**10000.0 - self.options[1][0]

		# beta**(1/10)
		#te = values[1]**(1.0/10.0)

		# beta**(1/10)
		#te = values[1]**(1.0/10.0)

		# (beta.tm) / ( (1-alpha)tm - beta )
		#if ((1.0 - values[0])*self.options[1][0] - values[1]) == 0.0:
		#	te = 1e99
		#else:
		#	te = values[1]*self.options[1][0] / ((1.0 - values[0])*self.options[1][0] - values[1])

		# (alpha + beta).tm / (tm - (alpha + beta))
		#if (self.options[1][0] - (values[0] + values[1])) == 0.0:
		#	te = 1e99
		#else:
		#	te = (values[0] + values[1]) * self.options[1][0] / (self.options[1][0] - (values[0] + values[1]))

		# (alpha + beta).tm / (tm - (alpha + beta))
		#if values[1] == 0.0:
		#	te = 1e99
		#else:
		#	te = (1.0 - (values[0] + values[1]) * self.options[1][0]) / values[1]

		#if values[1] == 0.0:
		#	te = 0.0
		#else:
		#	te = 1.0 / (1.0/values[1] - 1.0/self.options[1][0])

		# alpha.tm / (beta.tm - alpha)
		#if values[1] == 0.0:
		#	te = 0.0
		#elif (values[1] * self.options[1][0] - values[0]) == 0.0:
		#	te = 1e99
		#else:
		#	te = values[0] * self.options[1][0] / (values[1] * self.options[1][0] - values[0])

		# 1 / (beta**alpha - 1/tm)
		#if values[0] == 0.0:
		#	te = 0.0
		#else:
		#	te = 1.0 / (values[1]**(1.0/values[0]) - 1.0/self.options[1][0])

		#if (values[1]*(1.0 - values[0])) == 0.0:
		#	te = 1e99
		#else:
		#	te = 1.0 / (values[1]*(1.0 - values[0])) - self.options[1][0]

		#if values[0] == 0.0:
		#	te = 1e99
		#else:
		#	te = values[1]**(1.0/values[0])

		# alpha / (alpha + beta)
		#if (values[0] - values[1]) == 0.0:
		#	te = 1e99
		#else:
		#	te = 0.5 / (values[0] - values[1]) - self.options[1][0]

		# Rex
		#####

		# Rex
		rex = values[2]

		return [s2, te, rex]


	def calc_jw_iso_m13(self, i, frq_index):
		"Calculate the model 1 and 3 spectral density values for isotropic rotational diffusion."

		omega_tm_sqrd = self.frq_sqrd_list[self.remap_table[i]][frq_index] * self.tm_sqrd
		jw = 0.4 * (self.s2_tm / (1.0 + omega_tm_sqrd))
		return jw


	def calc_jw_iso_m24(self, i, frq_index):
		"Calculate the model 2 and 4 spectral density values for isotropic rotational diffusion."

		omega_te_prime_sqrd = self.frq_sqrd_list[self.remap_table[i]][frq_index] * self.te_prime_sqrd
		omega_tm_sqrd = self.frq_sqrd_list[self.remap_table[i]][frq_index] * self.tm_sqrd
		jw = 0.4 * (self.s2_tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2) * self.te_prime / (1.0 + omega_te_prime_sqrd))
		return jw


	def calc_jw_iso_m5(self, i, frq_index):
		"Calculate the model 5 spectral density values for isotropic rotational diffusion."

		omega_ts_prime_sqrd = self.frq_sqrd_list[self.remap_table[i]][frq_index] * self.ts_prime_sqrd
		omega_tm_sqrd = self.frq_sqrd_list[self.remap_table[i]][frq_index] * self.tm_sqrd
		jw = 0.4 * self.s2f * (self.s2s_tm / (1.0 + omega_tm_sqrd) + (1.0 - self.s2s) * self.ts_prime / (1.0 + omega_ts_prime_sqrd))
		return jw


	def calc_noe_iso(self, i, ri):
		"Calculate the Isotropic NOE value."

		if self.noe_r1_table[i] == None:
			r1 = self.calc_r1_iso(i)
		else:
			r1 = ri[self.noe_r1_table[i]]
		if r1 == 0:
			noe = 1
		else:
			noe = 1.0 + (self.dipole_const / r1) * (self.gh/self.gx) * (6.0*self.j[i][4] - self.j[i][2])
		return noe


	def calc_r1_iso(self, i):
		"Calculate the Isotropic R1 value."

		r1_dipole = self.dipole_const * (self.j[i][2] + 3.0*self.j[i][1] + 6.0*self.j[i][4])
		r1_csa = self.csa_const[self.frq_num] * self.j[i][1]
		r1 = r1_dipole + r1_csa
		return r1


	def calc_r2_iso(self, i):
		"Calculate the Isotropic R2 value."

		r2_dipole = (self.dipole_const/2.0) * (4.0*self.j[i][0] + self.j[i][2] + 3.0*self.j[i][1] + 6.0*self.j[i][3] + 6.0*self.j[i][4])
		r2_csa = (self.csa_const[self.frq_num]/6.0) * (4.0*self.j[i][0] + 3.0*self.j[i][1])
		if match('m[34]', self.options[2]):
			r2 = r2_dipole + r2_csa + self.rex
		else:
			r2 = r2_dipole + r2_csa
		return r2


	def create_true(self):
		#self.mf_values = [0.0784, 9930 * 1e-12, 0.000 / self.frq[0]**2]
		self.mf_values = [0.970, 2048.0 * 1e-12, 0.149 / self.frq[0]**2]
		self.values = self.Ri()
		self.errors = []
		for i in range(self.num_ri):
			if match('NOE', self.data_types[i]) and self.frq_label[self.remap_table[i]] == '600':
				self.errors.append(0.04)
			elif match('NOE', self.data_types[i]) and self.frq_label[self.remap_table[i]] == '500':
				self.errors.append(0.05)
			else:
				self.errors.append(self.values[i] * 0.02)


	def init_data(self):
		print "[ Initializing data ]"
		self.gh = 26.7522e7
		self.gx = -2.7126e7
		self.h = 6.6260755e-34
		self.h_bar = self.h / ( 2.0*pi )
		self.mu0 = 4.0*pi * 1e-7

		self.rnh = 1.02 * 1e-10
		self.csa = -160.0 * 1e-6

		self.num_ri = 6
		self.num_frq = 2
		self.frq_label = ['600', '500']
		self.frq = [600.0 * 1e6, 500.0 * 1e6]
		self.frq_list = []
		self.frq_sqrd_list = []
		for i in range(len(self.frq)):
			self.frq_list.append([])
			self.frq_sqrd_list.append([])
			frqH = 2.0 * pi * self.frq[i]
			frqN = frqH * ( self.gx / self.gh )
			self.frq_list[i].append(0.0)
			self.frq_list[i].append(frqN)
			self.frq_list[i].append(frqH - frqN)
			self.frq_list[i].append(frqH)
			self.frq_list[i].append(frqH + frqN)
			self.frq_sqrd_list[i].append(0.0)
			self.frq_sqrd_list[i].append(frqN**2)
			self.frq_sqrd_list[i].append((frqH - frqN)**2)
			self.frq_sqrd_list[i].append(frqH**2)
			self.frq_sqrd_list[i].append((frqH + frqN)**2)
		self.data_types = ['R1', 'R2', 'NOE', 'R1', 'R2', 'NOE']
		self.remap_table = [0, 0, 0, 1, 1, 1]
		self.noe_r1_table = [None, None, 0, None, None, 3]

		# Dipolar constant.
		dip = (self.mu0/(4.0*pi)) * self.h_bar * self.gh * self.gx * self.rnh**-3
		self.dipole_const = (dip**2) / 4.0

		# CSA constant.
		self.csa_const = []
		for i in range(self.num_frq):
			csa_const = self.csa**2 * self.frq_list[i][1]**2 / 3.0
			self.csa_const.append(csa_const)

		print "Done\n"


	def initialise_mf_values(self):
		"""Remap the parameters in self.mf_values, and make sure they are of the type float.

		Rex is not needed (not part of the spectral density)!
		"""

		# Isotropic dependent values.
		if match(self.options[0], 'iso'):
			self.tm = self.options[1][0]
			self.tm_sqrd = self.tm ** 2

		# Diffusion independent values.
		if match('m[13]', self.options[2]):
			self.s2 = self.mf_values[0]
			self.s2_tm = self.s2 * self.tm
		elif match('m[24]', self.options[2]):
			self.s2 = self.mf_values[0]
			self.te = self.mf_values[1]
			if self.te == 0.0 or (1.0/self.tm + 1.0/self.te) == 0:
				self.te_prime = 0.0
			else:
				self.te_prime = 1.0 / (1.0/self.tm + 1.0/self.te)
			#self.te_prime = (self.te * self.tm) / (self.te + self.tm)
			self.te_prime_sqrd = self.te_prime ** 2
			self.s2_tm = self.s2 * self.tm
		elif match('m5', self.options[2]):
			self.s2f = self.mf_values[0]
			self.s2s = self.mf_values[1]
			self.ts = self.mf_values[2]
			self.ts_prime = (self.ts * self.tm) / (self.ts + self.tm)
			self.ts_prime_sqrd = self.ts_prime ** 2
			self.s2s_tm = self.s2s * self.tm


	def J(self):
		"""Function to calculate spectral density values

		The arguments are:
		1: options - an array with:
			[0] - String.  The diffusion tensor, ie 'iso', 'axial', 'aniso'
			[1] - Array.  An array with the diffusion parameters
			[2] - String.  The model-free model
		2: mf_values - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}
		"""

		# Calculate frequency independent terms (to increase speed)
		self.initialise_mf_values()

		last_frq = 0.0
		self.jw = []

		# Loop over the relaxation values.
		for i in range(self.num_ri):
			if self.frq[self.remap_table[i]] != last_frq:
				jw = []
				for frq_index in range(5):
					# Isotropic rotational diffusion.
					if match(self.options[0], 'iso'):
						if match('m[13]', self.options[2]):
							jw.append(self.calc_jw_iso_m13(i, frq_index))
						elif match('m[24]', self.options[2]):
							jw.append(self.calc_jw_iso_m24(i, frq_index))
						elif match('m5', self.options[2]):
							jw.append(self.calc_jw_iso_m5(i, frq_index))

					# Axially symmetric rotational diffusion.
					elif match(self.options[0], 'axail'):
						print "Axially symetric diffusion not implemented yet, quitting program."
						sys.exit()

					# Anisotropic rotational diffusion.
					elif match(self.options[0], 'aniso'):
						print "Anisotropic diffusion not implemented yet, quitting program."
						sys.exit()

					else:
						raise NameError, "Diffusion type set incorrectly, quitting program."


			self.jw.append(jw)

			# Set the last frequency value.
			last_frq = self.frq[self.remap_table[i]]

		return self.jw


	def Ri(self):
		"""Function for the back calculation of relaxation values

		The arguments are:
		1: options - an array with:
			[0] - String.  The diffusion tensor, ie 'iso', 'axial', 'aniso'
			[1] - Array.  An array with the diffusion parameters
			[2] - String.  The model-free model
		3: mf_values - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}

		Calculation of the NOE value requires recalculation of the R1 value - not very efficient!


		Returned is an array of back calculated relaxation values.
		"""

		last_frq = 0.0
		ri = []

		# Calculate the spectral density values
		self.j = self.J()

		# Loop over the relaxation values.
		for i in range(self.num_ri):
			if match('m3', self.options[2]):
				self.rex = self.mf_values[1] * self.frq[self.remap_table[i]]**2
			elif match('m4', self.options[2]):
				self.rex = self.mf_values[2] * self.frq[self.remap_table[i]]**2
			self.frq_num = self.remap_table[i]

			# Back calculate the relaxation value.
			if match(self.options[0], 'iso'):
				if match('R1', self.data_types[i]):
					ri.append(self.calc_r1_iso(i))
				elif match('R2', self.data_types[i]):
					ri.append(self.calc_r2_iso(i))
				elif match('NOE', self.data_types[i]):
					ri.append(self.calc_noe_iso(i, ri))
				else:
					raise NameError, "Relaxation data type " + `self.data_types[i]` + " unknown, quitting program."
			elif match(self.options[0], 'axail'):
				print "Axially symetric diffusion not implemented yet, quitting program."
				sys.exit()
			elif match(self.options[0], 'aniso'):
				print "Anisotropic diffusion not implemented yet, quitting program."
				sys.exit()
			else:
				raise NameError, "Function option not set correctly, quitting program."

			# Set the last frequency value.
			last_frq = self.frq[self.remap_table[i]]

		return ri


if __name__ == "__main__":
	map()
