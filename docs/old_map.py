#! /usr/bin/python

import sys
from math import pi
from re import match
from string import split


class map:
	def __init__(self):

		self.init_data()

		# Insert randomized nums + errors.
		self.mf_params = [0.952, 0.582, 32]
		self.real = self.calc_relax_data('m5', self.mf_params)
		self.types = [ ['NOE', 600.0], ['R1', 600.0], ['R2', 600.0], ['NOE', 500.0], ['R1', 500.0], ['R2', 500.0] ]
		self.real_err = []
		for i in range(len(self.types)):
			if match('NOE', self.types[i][0]) and self.types[i][1] == 600.0:
				self.real_err.append(0.04)
			elif match('NOE', self.types[i][0]) and self.types[i][1] == 500.0:
				self.real_err.append(0.05)
			else:
				self.real_err.append(self.real[i] * 0.02)

		#self.create_RG_grid()
		self.create_DMG_grid()

		sys.exit()


	def init_data(self):
		print "[ Initializing data ]"
		self.gh = 26.7522e7
		self.gn = -2.7126e7
		self.h = 6.6260755e-34
		self.h_bar = self.h / ( 2.0*pi )
		self.mu0 = 4.0*pi * 1e-7

		self.tm = 10e-9
		self.rnh = 1.02 * 1e-10
		self.csa = -160.0 * 1e-6

		self.nmr_frq = [ 600.0, 500.0 ]
		self.frq = []
		for i in range(len(self.nmr_frq)):
			self.frq.append([])
			frqH = 2.0*pi * ( float(self.nmr_frq[i]) * 1e6 )
			frqN = frqH * ( self.gn / self.gh )
			self.frq[i].append(0.0)
			self.frq[i].append(frqN)
			self.frq[i].append(frqH - frqN)
			self.frq[i].append(frqH)
			self.frq[i].append(frqH + frqN)
		self.types = [ ['NOE', 600], ['R1', 600], ['R2', 600], ['NOE', 500], ['R1', 500], ['R2', 500] ]

		# Dipolar constant.
		dip = (self.mu0/(4.0*pi)) * self.h_bar * self.gh * self.gn * self.rnh**-3
		self.dipole_const = (dip**2) / 4.0
		dip_temp = self.dipole_const / 1e9

		# CSA constant.
		self.csa_const = []
		csa_temp = []
		for i in range(len(self.nmr_frq)):
			csa_const = (self.csa**2) * (self.frq[i][1]**2) / 3.0
			self.csa_const.append(csa_const)
			csa_temp.append(csa_const/1e9)

		print "Done\n"


	def create_RG_grid(self):
		"Rex grid."

		print "[ Creating the grid ]"

		file = open('grid', 'w')

		self.s2_intervals = 100.0
		self.s2_interval_size = 0.6 / self.s2_intervals
		
		self.te_intervals = 100.0
		self.te_interval_size = 1000.0 / self.te_intervals
		
		self.rex_intervals = 100.0
		self.rex_interval_size = 5.0 / self.rex_intervals
		
		s2_val = 0
		for i in range(self.s2_intervals + 1):
			print "%5.1f%-6s" % (float(s2_val*100), "% done")
			te_val = 0
			for j in range(self.te_intervals + 1):
				rex_val = 0
				for k in range(self.rex_intervals + 1):
					mf_params = [s2_val, te_val, rex_val]
					relax_data = self.calc_relax_data('m4', mf_params)
					chi2_sum = 0
					chi2 = []
					for i in range(len(relax_data)):
						chi2.append((( relax_data[i] - self.real[i] ) ** 2)/(self.real_err[i]**2))
						chi2_sum = chi2_sum + chi2[i]

					file.write("%30f\n" % chi2_sum)
					rex_val = rex_val + self.rex_interval_size
				te_val = te_val + self.te_interval_size
			s2_val = s2_val + self.s2_interval_size
		print "Done\n"


	def create_DMG_grid(self):
		"Double motion grid."

		print "[ Creating the grid ]"

		file = open('grid', 'w')

		self.s2f_intervals = 200.0
		self.s2f_interval_size = 0.5 / self.s2f_intervals
		
		self.s2s_intervals = 200.0
		self.s2s_interval_size = 0.5 / self.s2s_intervals
		
		self.te_intervals = 200.0
		self.te_interval_size = 300.0 / self.te_intervals
		
		s2f_val = 0.5
		for i in range(self.s2f_intervals + 1):
			print "%5.1f%-6s" % (float(s2f_val*100), "% done")
			s2s_val = 0.5
			for j in range(self.s2s_intervals + 1):
				te_val = 0
				for k in range(self.te_intervals + 1):
					mf_params = [s2f_val, s2s_val, te_val]
					relax_data = self.calc_relax_data('m5', mf_params)
					chi2_sum = 0
					chi2 = []
					for i in range(len(relax_data)):
						chi2.append((( relax_data[i] - self.real[i] ) ** 2)/(self.real_err[i]**2))
						chi2_sum = chi2_sum + chi2[i]

					file.write("%30f\n" % chi2_sum)
					te_val = te_val + self.te_interval_size
				s2s_val = s2s_val + self.s2s_interval_size
			s2f_val = s2f_val + self.s2f_interval_size
		print "Done\n"


	def calc_relax_data(self, model, mf_params):
		"""Main function for the calculation of all relaxation values.

		The arguments are:
		1: model - one of the following, {m1, m2, m3, m4, m5}
		2: mf_params - a list containing the model-free parameters specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}
		"""

		self.model = model
		self.mf_params = mf_params
		self.rex = []

		if match('m1', self.model):
			self.s2  = float(self.mf_params[0])
			self.s2f = float(self.mf_params[0])
			self.s2s = 1.0
			self.tf  = 0.0 * 1e-12
			self.ts  = 0.0 * 1e-12
			for i in range(len(self.nmr_frq)):
				self.rex.append(0.0)
		elif match('m2', self.model):
			self.s2  = float(self.mf_params[0])
			self.s2f = float(self.mf_params[0])
			self.s2s = 1.0
			self.tf  = float(self.mf_params[1]) * 1e-12
			self.ts  = 0.0 * 1e-12
			for i in range(len(self.nmr_frq)):
				self.rex.append(0.0)
		elif match('m3', self.model):
			self.s2  = float(self.mf_params[0])
			self.s2f = float(self.mf_params[0])
			self.s2s = 1.0
			self.tf  = 0.0 * 1e-12
			self.ts  = 0.0 * 1e-12
			for i in range(len(self.nmr_frq)):
				self.rex.append(float(self.mf_params[1]) * ( (float(self.nmr_frq[i]) / float(self.nmr_frq[0]))**2 ))
		elif match('m4', self.model):
			self.s2  = float(self.mf_params[0])
			self.s2f = float(self.mf_params[0])
			self.s2s = 1.0
			self.tf  = float(self.mf_params[1]) * 1e-12
			self.ts  = 0.0 * 1e-12
			for i in range(len(self.nmr_frq)):
				self.rex.append(float(self.mf_params[2]) * ( (float(self.nmr_frq[i]) / float(self.nmr_frq[0]))**2 ))
		elif match('m5', self.model):
			self.s2  = float(self.mf_params[0]) * float(self.mf_params[1])
			self.s2f = float(self.mf_params[0])
			self.s2s = float(self.mf_params[1])
			self.tf  = 0.0 * 1e-12
			self.ts  = float(self.mf_params[2]) * 1e-12
			for i in range(len(self.nmr_frq)):
				self.rex.append(0.0)

		self.tf_prime = ( self.tf * self.tm ) / ( self.tf + self.tm )
		self.ts_prime = ( self.ts * self.tm ) / ( self.ts + self.tm )

		self.j = []
		for i in range(len(self.nmr_frq)):
			self.j.append([0.0, 0.0, 0.0, 0.0, 0.0])
			self.j[i][0] = self.calc_jw(self.frq[i][0])
			self.j[i][1] = self.calc_jw(self.frq[i][1])
			self.j[i][2] = self.calc_jw(self.frq[i][2])
			self.j[i][3] = self.calc_jw(self.frq[i][3])
			self.j[i][4] = self.calc_jw(self.frq[i][4])

		self.back_calc = []
		for i in range(len(self.types)):
			for j in range(len(self.nmr_frq)):
				if self.types[i][1] == float(self.nmr_frq[j]):
					self.frq_num = j
			if match('NOE', self.types[i][0]):
				self.back_calc.append(self.calc_noe(self.types[i][1]))
			elif match('R1', self.types[i][0]):
				self.back_calc.append(self.calc_r1(self.types[i][1]))
			elif match('R2', self.types[i][0]):
				self.back_calc.append(self.calc_r2(self.types[i][1]))

		return self.back_calc


	def calc_jw(self, frq):
		# Lorentzian 1:
		top = self.s2 * self.tm
		bottom = 1.0 + ( frq * self.tm )**2
		loren1 = top / bottom

		# Lorentzian 2:
		top = ( 1.0 - self.s2f ) * self.tf_prime
		bottom = 1.0 + ( frq * self.tf_prime )**2
		loren2 = top / bottom

		# Lorentzian 3:
		top = ( self.s2f - self.s2 ) * self.ts_prime
		bottom = 1.0 + ( frq * self.ts_prime )**2
		loren3 = top / bottom

		# Spectral density value.
		jw = 2.0/5.0 * ( loren1 + loren2 + loren3 )
		return jw


	def calc_noe(self, frq):
		"Calculate the NOE value."

		r1 = self.calc_r1(frq)
		if r1 == 0:
			noe = 1.0
		else:
			noe = 1.0 + ( self.dipole_const / r1 ) * ( self.gh/self.gn ) * ( 6.0*self.j[self.frq_num][4] - self.j[self.frq_num][2] )
		return noe


	def calc_r1(self, frq):
		"Calculate the R1 value."

		r1_dipole = self.dipole_const * ( self.j[self.frq_num][2] + 3.0*self.j[self.frq_num][1] + 6.0*self.j[self.frq_num][4] )
		r1_csa = self.csa_const[self.frq_num] * ( self.j[self.frq_num][1] )
		r1 = r1_dipole + r1_csa
		return r1


	def calc_r2(self, frq):
		"Calculate the R2 value."

		r2_dipole = (self.dipole_const/2.0) * ( 4.0*self.j[self.frq_num][0] + self.j[self.frq_num][2] + 3.0*self.j[self.frq_num][1] + 6.0*self.j[self.frq_num][3] + 6.0*self.j[self.frq_num][4])
		r2_csa = (self.csa_const[self.frq_num]/6.0) * ( 4.0*self.j[self.frq_num][0] + 3.0*self.j[self.frq_num][1] )
		r2 = r2_dipole + r2_csa + self.rex[self.frq_num]
		return r2


if __name__ == "__main__":
	map()
