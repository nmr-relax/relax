import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class Ri_prime:
	def __init__(self):
		"Function for back calculating relaxation values."


	def Ri_prime(self):
		"""Function for back calculation of relaxation values.

		The relaxation equations
		~~~~~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.data.ri
		Dimension:  1D, (relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.data.jw
		Required by:  self.data.chi2, self.data.dchi2, self.data.d2chi2
		Stored:  Yes


		Formulae
		~~~~~~~~

		Relaxation equations
		~~~~~~~~~~~~~~~~~~~~

			R1()  =  d . [J(wH-wN) + 3J(wN) + 6J(wH+wN)]  +  c . [J(wN)]


			         d                                                        c
			R2()  =  - . [4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)]  +  - . [4J(0) + 3J(wN)]  +  Rex
			         2                                                        6


			                d     gH
			NOE()  =  1 +  ---- . -- . [6J(wH+wN) - J(wH-wN)]
			               R1()   gN


		Constants
		~~~~~~~~~
			      1   / mu0    gH.gN.h_bar \ 2
			d  =  - . | ---- . ----------- |
			      4   \ 4.pi     <r**3>    /


			    (wN.csa)**2
			c = -----------
			         3


		It is assumed that the spectral density matrix, self.data.jw, has not been calculated yet.
		"""

		# Debugging code.
		#print "<<< Ri >>>"

		# Initialise the relaxation array.
		self.data.ri_prime = zeros((self.mf.data.num_ri), Float64)

		# Calculate the spectral density values (if the relaxation array has not been made, then neither has the spectral density matrix).
		self.Jw()

		# Calculate the frequency dependent chemical exchange values. (Fix to calculate num_frq times rather than i times!!!)
		rex = zeros((self.mf.data.num_frq), Float64)
		for frq in range(self.mf.data.num_frq):
			if match('m3', self.data.mf_model):
				rex[frq] = self.data.mf_params[1] * (1e-8 * self.mf.data.frq[frq])**2
			elif match('m4', self.data.mf_model):
				rex[frq] = self.data.mf_params[2] * (1e-8 * self.mf.data.frq[frq])**2

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			frq_num = self.mf.data.remap_table[i]

			# Calculate the relaxation data.
			if match('R1', self.mf.data.data_types[i]):
				self.data.ri_prime[i] = self.calc_r1(frq_num)
			elif match('R2', self.mf.data.data_types[i]):
				self.data.ri_prime[i] = self.calc_r2(rex[frq_num], frq_num)
			elif match('NOE', self.mf.data.data_types[i]):
				self.data.ri_prime[i] = self.calc_noe(i, frq_num)
			else:
				raise NameError, "Relaxation data type " + `self.mf.data.data_types[i]` + " unknown, quitting program."

			# Debugging code.
			if self.mf.debug == 1:
				self.mf.log.write("%5s%-12.4f%2s" % (" S2: ", self.s2, " |"))
				self.mf.log.write("%6s%-11.4f%2s" % (" S2f: ", self.s2f, " |"))
				self.mf.log.write("%6s%-11.4f%2s" % (" S2s: ", self.s2s, " |"))
				self.mf.log.write("%5s%-12.4g%2s" % (" tf: ", self.tf, " |"))
				self.mf.log.write("%5s%-12.4g%2s" % (" ts: ", self.ts, " |"))
				self.mf.log.write("%10s%-7.4f%2s" % (self.mf.data.nmr_frq[i][0] + " rex: ", rex, " |"))
				self.mf.log.write("\n")

				for i in range(self.mf.data.num_ri):
					self.mf.log.write("%-10s" % (" " + `int(self.type[1])` + " " + self.type[0] + ": "))
					self.mf.log.write("%-7.4f%2s" % (self.ri[i], " |"))
				self.mf.log.write("\n")


	def calc_r1(self, frq_num):
		"Calculate the R1 value."

		r1_dipole = self.mf.data.dipole_const * (self.data.jw[frq_num, 2] + 3.0*self.data.jw[frq_num, 1] + 6.0*self.data.jw[frq_num, 4])
		r1_csa = self.mf.data.csa_const[frq_num] * self.data.jw[frq_num, 1]
		r1 = r1_dipole + r1_csa
		return r1


	def calc_r2(self, rex, frq_num):
		"Calculate the R2 value."

		r2_dipole = (self.mf.data.dipole_const/2.0) * (4.0*self.data.jw[frq_num, 0] + self.data.jw[frq_num, 2] + 3.0*self.data.jw[frq_num, 1] + 6.0*self.data.jw[frq_num, 3] + 6.0*self.data.jw[frq_num, 4])
		r2_csa = (self.mf.data.csa_const[frq_num]/6.0) * (4.0*self.data.jw[frq_num, 0] + 3.0*self.data.jw[frq_num, 1])
		if match('m[34]', self.data.mf_model):
			r2 = r2_dipole + r2_csa + rex
		else:
			r2 = r2_dipole + r2_csa
		return r2


	def calc_noe(self, i, frq_num):
		"Calculate the NOE value."

		# May need debugging.
		if self.mf.data.noe_r1_table[i] == None:
			r1 = self.calc_r1(frq_num)
		else:
			r1 = self.data.ri_prime[self.mf.data.noe_r1_table[i]]

		if r1 == 0:
			noe = 1e99
		else:
			noe = 1.0 + (self.mf.data.dipole_const / r1) * (self.mf.data.gh/self.mf.data.gx) * (6.0*self.data.jw[frq_num, 4] - self.data.jw[frq_num, 2])
		return noe
