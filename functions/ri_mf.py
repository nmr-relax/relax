import sys
from math import pi
from Numeric import Float64, copy, zeros
from re import match


class Ri:
	def __init__(self, mf):
		"Function for the back calculating relaxation values."

		self.mf = mf


	def calc(self, mf_params, diff_type, diff_params, mf_model):
		"""Function for the back calculation of relaxation values.

		Function arguments
		~~~~~~~~~~~~~~~~~~

		1:  mf_params - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}
		2:  diff_type - string.  The diffusion tensor, ie 'iso', 'axial', 'aniso'
		3:  diff_params - array.  An array with the diffusion parameters
		4:  mf_model - string.  The model-free model


		The relaxation array
		~~~~~~~~~~~~~~~~~~~~

		Data structure:  self.ri
		Dimension:  1D, (relaxation data)
		Type:  Numeric array, Float64
		Dependencies:  self.jw
		Required by:  self.chi2, self.dchi2
		Stored:  Yes
		Formulae:
			Normal relaxation equations (Abragam, 1961)
				R1  = d * [J(wH-wN) + 3J(wN) + 6J(wH+wN)] + c * [J(wN)]
				R2  = d/2 * [4J(0) + J(wH-wN) + 3J(wN) + 6J(wH) + 6J(wH+wN)] + c/6 * [4J(0) + 3J(wN)] + Rex
				NOE = 1 + (d/R1).(gH/gN).[6J(wH+wN) - J(wH-wN)]

				d = ((mu0/4.pi).(gN.gH.h_bar/(2.<rNH>**-3)))**2
				c = ((wN.csa)**2)/3


		It is assumed that the spectral density matrix, self.mf.data.mf_data.jw, has not been calculated yet.
		"""

		self.mf_params = mf_params
		self.diff_type = diff_type
		self.diff_params = diff_params
		self.mf_model = mf_model

		# Debugging code.
		#print "<<< Ri >>>"

		# Initialise the relaxation array.
		self.ri = zeros((self.mf.data.num_ri), Float64)

		# Calculate the spectral density values (if the relaxation array has not been made, then neither has the spectral density matrix).
		self.mf.mf_functions.Jw.calc(self.mf_params, self.diff_type, self.diff_params, self.mf_model)

		# Calculate the frequency dependent chemical exchange values. (Fix to calculate num_frq times rather than i times!!!)
		rex = zeros((self.mf.data.num_frq), Float64)
		for frq in range(self.mf.data.num_frq):
			if match('m3', self.mf_model):
				rex[frq] = self.mf_params[1] * self.mf.data.frq[frq]**2
			elif match('m4', self.mf_model):
				rex[frq] = self.mf_params[2] * self.mf.data.frq[frq]**2

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			self.frq_num = self.mf.data.remap_table[i]

			# Calculate the relaxation data.
			if match('R1', self.mf.data.data_types[i]):
				self.ri[i] = self.calc_r1()
			elif match('R2', self.mf.data.data_types[i]):
				self.ri[i] = self.calc_r2(rex[self.frq_num])
			elif match('NOE', self.mf.data.data_types[i]):
				self.ri[i] = self.calc_noe(i)
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

		# Store the relaxation array.
		self.mf.data.mf_data.ri = copy.deepcopy(self.ri)


	def calc_r1(self):
		"Calculate the R1 value."

		r1_dipole = self.mf.data.dipole_const * (self.mf.data.mf_data.jw[self.frq_num, 2] + 3.0*self.mf.data.mf_data.jw[self.frq_num, 1] + 6.0*self.mf.data.mf_data.jw[self.frq_num, 4])
		r1_csa = self.mf.data.csa_const[self.frq_num] * self.mf.data.mf_data.jw[self.frq_num, 1]
		r1 = r1_dipole + r1_csa
		return r1


	def calc_r2(self, rex):
		"Calculate the R2 value."

		r2_dipole = (self.mf.data.dipole_const/2.0) * (4.0*self.mf.data.mf_data.jw[self.frq_num, 0] + self.mf.data.mf_data.jw[self.frq_num, 2] + 3.0*self.mf.data.mf_data.jw[self.frq_num, 1] + 6.0*self.mf.data.mf_data.jw[self.frq_num, 3] + 6.0*self.mf.data.mf_data.jw[self.frq_num, 4])
		r2_csa = (self.mf.data.csa_const[self.frq_num]/6.0) * (4.0*self.mf.data.mf_data.jw[self.frq_num, 0] + 3.0*self.mf.data.mf_data.jw[self.frq_num, 1])
		if match('m[34]', self.mf_model):
			r2 = r2_dipole + r2_csa + rex
		else:
			r2 = r2_dipole + r2_csa
		return r2


	def calc_noe(self, i):
		"Calculate the NOE value."

		# May need debugging.
		if self.mf.data.noe_r1_table[i] == None:
			r1 = self.calc_r1()
		else:
			r1 = self.ri[self.mf.data.noe_r1_table[i]]

		if r1 == 0:
			noe = 1e99
		else:
			noe = 1.0 + (self.mf.data.dipole_const / r1) * (self.mf.data.gh/self.mf.data.gx) * (6.0*self.mf.data.mf_data.jw[self.frq_num, 4] - self.mf.data.mf_data.jw[self.frq_num, 2])
		return noe
