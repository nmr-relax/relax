import sys
from math import pi
from re import match


class relax:
	def __init__(self, mf):
		"""Functions for the back calculating relaxation values and derivatives.

		Ri() - Calculate the spectral density value for the model-free model, parameter values, and frequency.
			A single spectral density value is returned.

		dRi() - Calculate the derivative of the spectral density function for the model-free model, parameter values, and frequency.
			An array is returned with the elements as the derivative of the spectral density function with respect to the
			corresponding model-free model parameters.

		Large repetition of code is to increase the speed of the function.
		"""

		self.mf = mf


	def Ri(self, options, type, mf_values):
		"""Function for the back calculation of relaxation values.

		The arguments are:
		1: options - an array with:
			[0] - the diffusion tensor, ie 'iso', 'axial', 'aniso'
			[1] - an array with the diffusion parameters
			[2] - the model-free model
		2: type - an array with:
			[0] - one of the following, {NOE, R1, R2}
			[1] - the proton Lamor frequency in MHz
		3: mf_values - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}

		Calculation of the NOE value requires recalculation of the R1 value - not very efficient!

		Returned is the single relaxation value.
		"""

		self.options = options
		self.type = type
		self.mf_values = mf_values

		self.initialise_mf_values()

		# Calculate the spectral densities.
		for i in range(len(self.mf.usr_param.nmr_frq)):
			if match(self.type[1], self.mf.usr_param.nmr_frq[i][0]):
				self.frq = self.mf.usr_param.nmr_frq[i][1]
				self.frq_num = i
		self.j = []
		self.j.append(self.mf.functions.jw.J(self.options, self.mf.data.frq[self.frq_num][0], self.mf_values))
		self.j.append(self.mf.functions.jw.J(self.options, self.mf.data.frq[self.frq_num][1], self.mf_values))
		self.j.append(self.mf.functions.jw.J(self.options, self.mf.data.frq[self.frq_num][2], self.mf_values))
		self.j.append(self.mf.functions.jw.J(self.options, self.mf.data.frq[self.frq_num][3], self.mf_values))
		self.j.append(self.mf.functions.jw.J(self.options, self.mf.data.frq[self.frq_num][4], self.mf_values))

		# Back calculate the relaxation value.
		if match(self.options[0], 'iso'):
			if match('R1', self.type[0]):
				self.ri = self.calc_r1_iso()
			elif match('R2', self.type[0]):
				self.ri = self.calc_r2_iso()
			elif match('NOE', self.type[0]):
				self.ri = self.calc_noe_iso()
			else:
				print "Relaxation data type " + `self.type[0]` + " unknown, quitting program."
				sys.exit()

		elif match(self.options[0], 'axail'):
			print "Axially symetric diffusion not implemented yet, quitting program."
			sys.exit()

		elif match(self.options[0], 'aniso'):
			print "Anisotropic diffusion not implemented yet, quitting program."
			sys.exit()

		else:
			print "Function option not set correctly, quitting program."
			sys.exit()


		if self.mf.debug == 1:
			self.mf.log.write("%5s%-12.4f%2s" % (" S2: ", self.s2, " |"))
			self.mf.log.write("%6s%-11.4f%2s" % (" S2f: ", self.s2f, " |"))
			self.mf.log.write("%6s%-11.4f%2s" % (" S2s: ", self.s2s, " |"))
			self.mf.log.write("%5s%-12.4g%2s" % (" tf: ", self.tf, " |"))
			self.mf.log.write("%5s%-12.4g%2s" % (" ts: ", self.ts, " |"))
			for i in range(len(self.mf.data.nmr_frq)):
				self.mf.log.write("%10s%-7.4f%2s" % (self.mf.data.nmr_frq[i][0] + " rex: ", self.rex[i], " |"))
			self.mf.log.write("\n")

			for i in range(len(self.type)):
				self.mf.log.write("%-10s" % (" " + `int(self.type[1])` + " " + self.type[0] + ": "))
				self.mf.log.write("%-7.4f%2s" % (self.ri[i], " |"))
			self.mf.log.write("\n")

		del self.j

		return self.ri


	def dRi(self, options, type, mf_values):
		"""Function to calculate the derivative of the relaxation values.

		The arguments are:
		1: options - an array with:
			[0] - the diffusion tensor, ie 'iso', 'axial', 'aniso'
			[1] - an array with the diffusion parameters
			[2] - the model-free model
		2: type - an array with:
			[0] - one of the following, {NOE, R1, R2}
			[1] - the proton Lamor frequency in MHz
		3: mf_values - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}

		Calculation of the NOE value requires recalculation of the R1 value - not very efficient!

		Returned is an array with the elements as the derivative of the spectral density function with respect to the
		corresponding model-free model parameters.
		"""

		self.options = options
		self.type = type
		self.mf_values = mf_values

		self.initialise_mf_values()

		# Create empty relaxation derivative vector.
		self.dri = []

		# Initialise an array with the model-free parameter labels.
		self.param_types = []
		if match('m1', self.options[2]):
			self.param_types.append('S2')
		elif match('m2', self.options[2]):
			self.param_types.append('S2')
			self.param_types.append('te')
		elif match('m3', self.options[2]):
			self.param_types.append('S2')
			self.param_types.append('Rex')
		elif match('m4', self.options[2]):
			self.param_types.append('S2')
			self.param_types.append('te')
			self.param_types.append('Rex')
		elif match('m5', self.options[2]):
			self.param_types.append('S2f')
			self.param_types.append('S2s')
			self.param_types.append('ts')
		else:
			print "Should not be here."
			sys.exit()

		# Calculate the spectral densities.
		for i in range(len(self.mf.usr_param.nmr_frq)):
			if match(self.type[1], self.mf.usr_param.nmr_frq[i][0]):
				self.frq = self.mf.usr_param.nmr_frq[i][1]
				self.frq_num = i
		self.j = []
		self.j.append(self.mf.functions.jw.J(self.options, self.mf.data.frq[self.frq_num][0], self.mf_values))
		self.j.append(self.mf.functions.jw.J(self.options, self.mf.data.frq[self.frq_num][1], self.mf_values))
		self.j.append(self.mf.functions.jw.J(self.options, self.mf.data.frq[self.frq_num][2], self.mf_values))
		self.j.append(self.mf.functions.jw.J(self.options, self.mf.data.frq[self.frq_num][3], self.mf_values))
		self.j.append(self.mf.functions.jw.J(self.options, self.mf.data.frq[self.frq_num][4], self.mf_values))

		# Loop over the model-free parameters.
		for param_type in self.param_types:
			# Calculate the derivative of the spectral densities.
			self.dj = []
			self.dj.append(self.mf.functions.jw.dJ(self.options, self.mf.data.frq[self.frq_num][0], self.mf_values, param_type))
			self.dj.append(self.mf.functions.jw.dJ(self.options, self.mf.data.frq[self.frq_num][1], self.mf_values, param_type))
			self.dj.append(self.mf.functions.jw.dJ(self.options, self.mf.data.frq[self.frq_num][2], self.mf_values, param_type))
			self.dj.append(self.mf.functions.jw.dJ(self.options, self.mf.data.frq[self.frq_num][3], self.mf_values, param_type))
			self.dj.append(self.mf.functions.jw.dJ(self.options, self.mf.data.frq[self.frq_num][4], self.mf_values, param_type))

			# Calculate the derivative of the relaxation value.
			if match(self.options[0], 'iso'):
				if match('Rex', param_type):
					if match('R1', self.type[0]):
						self.dri.append(0.0)
					elif match('R2', self.type[0]):
						self.dri.append(1.0)
					elif match('NOE', self.type[0]):
						self.dri.append(0.0)
					else:
						print "Relaxation data type " + `self.type[0]` + " unknown, quitting program."
						sys.exit()
				else:
					if match('R1', self.type[0]):
						self.dri.append(self.calc_dr1_iso())
					elif match('R2', self.type[0]):
						self.dri.append(self.calc_dr2_iso())
					elif match('NOE', self.type[0]):
						self.dri.append(self.calc_dnoe_iso())
					else:
						print "Relaxation data type " + `self.type[0]` + " unknown, quitting program."
						sys.exit()

			elif match(self.options[0], 'axail'):
				print "Axially symetric diffusion not implemented yet, quitting program."
				sys.exit()

			elif match(self.options[0], 'aniso'):
				print "Anisotropic diffusion not implemented yet, quitting program."
				sys.exit()

			else:
				print "Function option not set correctly, quitting program."
				sys.exit()

			del self.dj


		if self.mf.debug == 1:
			self.mf.log.write("%5s%-12.4f%2s" % (" S2: ", self.s2, " |"))
			self.mf.log.write("%6s%-11.4f%2s" % (" S2f: ", self.s2f, " |"))
			self.mf.log.write("%6s%-11.4f%2s" % (" S2s: ", self.s2s, " |"))
			self.mf.log.write("%5s%-12.4g%2s" % (" tf: ", self.tf, " |"))
			self.mf.log.write("%5s%-12.4g%2s" % (" ts: ", self.ts, " |"))
			for i in range(len(self.mf.data.nmr_frq)):
				self.mf.log.write("%10s%-7.4f%2s" % (self.mf.data.nmr_frq[i][0] + " rex: ", self.rex[i], " |"))
			self.mf.log.write("\n")

			for i in range(len(self.type)):
				self.mf.log.write("%-10s" % (" " + `int(self.type[1])` + " " + self.type[0] + ": "))
				self.mf.log.write("%-7.4f%2s" % (self.dri[i], " |"))
			self.mf.log.write("\n")

		del self.j

		return self.dri


	def calc_dr1_iso(self):
		"Calculate the derivative of the R1 value."

		dr1_dipole = self.mf.data.dipole_const * (self.dj[2] + 3.0*self.dj[1] + 6.0*self.dj[4])
		dr1_csa = self.mf.data.csa_const[self.frq_num] * self.dj[1]
		dr1 = dr1_dipole + dr1_csa
		return dr1


	def calc_dr2_iso(self):
		"Calculate the derivative of the R2 value."

		dr2_dipole = (self.mf.data.dipole_const/2.0) * (4.0*self.dj[0] + 3.0*self.dj[1] + self.dj[2] + 6.0*self.dj[3] + 6.0*self.dj[4])
		dr2_csa = (self.mf.data.csa_const[self.frq_num]/6.0) * (4.0*self.dj[0] + 3.0*self.dj[1])
		dr2 = dr2_dipole + dr2_csa
		return dr2


	def calc_dnoe_iso(self):
		"Calculate the derivative of the NOE value."

		r1 = self.calc_r1_iso()
		dr1 = self.calc_dr1_iso()
		if r1 == 0:
			print "R1 is zero, this should not occur."
			dnoe = 10000.0
		elif dr1 == 0:
			dnoe = (self.mf.data.dipole_const / r1) * (self.mf.data.gh/self.mf.data.gx) * (6.0*self.dj[4] - self.dj[2])
		else:
			dnoe = (r1 * (6.0*self.dj[4] - self.dj[2]) - (6.0*self.j[4] - self.j[2]) * dr1) / r1**2
			dnoe = self.mf.data.dipole_const * (self.mf.data.gh/self.mf.data.gx) * dnoe
		return dnoe


	def calc_r1_iso(self):
		"Calculate the R1 value."

		r1_dipole = self.mf.data.dipole_const * (self.j[2] + 3.0*self.j[1] + 6.0*self.j[4])
		r1_csa = self.mf.data.csa_const[self.frq_num] * self.j[1]
		r1 = r1_dipole + r1_csa
		return r1


	def calc_r2_iso(self):
		"Calculate the R2 value."

		r2_dipole = (self.mf.data.dipole_const/2.0) * (4.0*self.j[0] + self.j[2] + 3.0*self.j[1] + 6.0*self.j[3] + 6.0*self.j[4])
		r2_csa = (self.mf.data.csa_const[self.frq_num]/6.0) * (4.0*self.j[0] + 3.0*self.j[1])
		# Rex frq dep problem.
		r2 = r2_dipole + r2_csa + self.rex
		return r2


	def calc_noe_iso(self):
		"Calculate the NOE value."

		r1 = self.calc_r1_iso()
		if r1 == 0:
			noe = 1.0
		else:
			noe = 1.0 + (self.mf.data.dipole_const / r1) * (self.mf.data.gh/self.mf.data.gx) * (6.0*self.j[4] - self.j[2])
		return noe


	def initialise_mf_values(self):
		"Remap the Rex parameter in self.mf_values, and make sure they are of the type float."
		if match('m[34]', self.options[2]):
			self.rex = float(self.mf_values[1]) / float(self.type[1])**2
		elif not match('m[125]', self.options[2]):
			print "Model-free model " + `self.options[2]` + " not implemented yet, quitting program."
			sys.exit()
