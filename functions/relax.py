import sys
from math import pi
from re import match


class relax:
	def __init__(self, mf):
		"Function for the back calculating relaxation values and derivatives."

		self.mf = mf


	def Ri(self, options, mf_values):
		"""Function for the back calculation of relaxation values and their derivatives.

		The arguments are:
		1: options - an array with:
			[0] - String.  The diffusion tensor, ie 'iso', 'axial', 'aniso'
			[1] - Array.  An array with the diffusion parameters
			[2] - String.  The model-free model
			[3] - Int.  0 = no derivatives, 1 = calculate derivatives.
		3: mf_values - a list containing the model-free parameter values specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}

		Calculation of the NOE value requires recalculation of the R1 value - not very efficient!


		Returned is an array of back calculated relaxation values.

		If derivatives are asked for, an array of arrays of relaxation value derivatives where the first dimension
		corresponds to the relaxation values and the second dimension corresponds to the model-free parameters
		is also returned.
		"""

		self.options = options
		self.mf_values = mf_values

		last_frq = 0.0
		self.ri = []
		if self.options[3] == 1:
			self.dri = []
			# Initialise an array with the model-free parameter labels.
			if match('m1', self.options[2]):
				self.param_types = ['S2']
			elif match('m2', self.options[2]):
				self.param_types = ['S2', 'te']
			elif match('m3', self.options[2]):
				self.param_types = ['S2', 'Rex']
			elif match('m4', self.options[2]):
				self.param_types = ['S2', 'te', 'Rex']
			elif match('m5', self.options[2]):
				self.param_types = ['S2f', 'S2s', 'ts']
			else:
				raise NameError, "Should not be here."

		# Calculate the spectral density values and derivatives if asked to.
		if self.options[3] == 0:
			self.j = self.mf.functions.jw.J(self.options, self.mf_values)
		else:
			self.j, self.dj = self.mf.functions.jw.J(self.options, self.mf_values)

		# Loop over the relaxation values.
		for i in range(self.mf.data.num_ri):
			if match('m3', self.options[2]):
				self.rex = self.mf_values[1] * self.mf.data.frq[self.mf.data.remap_table[i]]**2
			elif match('m4', self.options[2]):
				self.rex = self.mf_values[2] * self.mf.data.frq[self.mf.data.remap_table[i]]**2
			self.frq_num = self.mf.data.remap_table[i]

			# Back calculate the relaxation value.
			if match(self.options[0], 'iso'):
				if match('R1', self.mf.data.data_types[i]):
					self.ri.append(self.calc_r1_iso(i))
				elif match('R2', self.mf.data.data_types[i]):
					self.ri.append(self.calc_r2_iso(i))
				elif match('NOE', self.mf.data.data_types[i]):
					self.ri.append(self.calc_noe_iso(i))
				else:
					raise NameError, "Relaxation data type " + `self.mf.data.data_types[i]` + " unknown, quitting program."
			elif match(self.options[0], 'axail'):
				print "Axially symetric diffusion not implemented yet, quitting program."
				sys.exit()
			elif match(self.options[0], 'aniso'):
				print "Anisotropic diffusion not implemented yet, quitting program."
				sys.exit()
			else:
				raise NameError, "Function option not set correctly, quitting program."

			# Derivatives.
			if self.options[3] == 1:
				self.dri.append([])
				for param in range(len(self.param_types)):
					# Isotropic rotational diffusion.
					if match(self.options[0], 'iso'):
						if match('Rex', self.param_types[param]):
							if match('R1', self.mf.data.data_types[i]):
								self.dri[i].append(0.0)
							elif match('R2', self.mf.data.data_types[i]):
								self.dri[i].append(1.0 * self.mf.data.frq[self.mf.data.remap_table[i]]**2)
							elif match('NOE', self.mf.data.data_types[i]):
								self.dri[i].append(0.0)
							else:
								raise NameError, "Relaxation data type " + `self.mf.data.data_types[i]` + " unknown, quitting program."
						else:
							if match('R1', self.mf.data.data_types[i]):
								self.dri[i].append(self.calc_dr1_iso(i, param))
							elif match('R2', self.mf.data.data_types[i]):
								self.dri[i].append(self.calc_dr2_iso(i, param))
							elif match('NOE', self.mf.data.data_types[i]):
								self.dri[i].append(self.calc_dnoe_iso(i, param))
							else:
								raise NameError, "Relaxation data type " + `self.mf.data.data_types[i]` + " unknown, quitting program."

					# Axially symmetric rotational diffusion.
					elif match(self.options[0], 'axail'):
						print "Axially symetric diffusion not implemented yet, quitting program."
						sys.exit()

					# Anisotropic rotational diffusion.
					elif match(self.options[0], 'aniso'):
						print "Anisotropic diffusion not implemented yet, quitting program."
						sys.exit()
					else:
						raise NameError, "Function option not set correctly, quitting program."


			if self.mf.debug == 1:
				self.mf.log.write("%5s%-12.4f%2s" % (" S2: ", self.s2, " |"))
				self.mf.log.write("%6s%-11.4f%2s" % (" S2f: ", self.s2f, " |"))
				self.mf.log.write("%6s%-11.4f%2s" % (" S2s: ", self.s2s, " |"))
				self.mf.log.write("%5s%-12.4g%2s" % (" tf: ", self.tf, " |"))
				self.mf.log.write("%5s%-12.4g%2s" % (" ts: ", self.ts, " |"))
				self.mf.log.write("%10s%-7.4f%2s" % (self.mf.data.nmr_frq[i][0] + " rex: ", self.rex, " |"))
				self.mf.log.write("\n")

				for i in range(self.mf.data.num_ri):
					self.mf.log.write("%-10s" % (" " + `int(self.type[1])` + " " + self.type[0] + ": "))
					self.mf.log.write("%-7.4f%2s" % (self.ri[i], " |"))
				self.mf.log.write("\n")

			# Set the last frequency value.
			last_frq = self.mf.data.frq[self.mf.data.remap_table[i]]

		if self.options[3] == 0:
			return self.ri
		else:
			return self.ri, self.dri


	def calc_dr1_iso(self, i, param):
		"Calculate the derivative of the Isotropic R1 value."

		dr1_dipole = self.mf.data.dipole_const * (self.dj[i][param][2] + 3.0*self.dj[i][param][1] + 6.0*self.dj[i][param][4])
		dr1_csa = self.mf.data.csa_const[self.frq_num] * self.dj[i][param][1]
		dr1 = dr1_dipole + dr1_csa
		return dr1


	def calc_dr2_iso(self, i, param):
		"Calculate the derivative of the Isotropic R2 value."

		dr2_dipole = (self.mf.data.dipole_const/2.0) * (4.0*self.dj[i][param][0] + 3.0*self.dj[i][param][1] + self.dj[i][param][2] + 6.0*self.dj[i][param][3] + 6.0*self.dj[i][param][4])
		dr2_csa = (self.mf.data.csa_const[self.frq_num]/6.0) * (4.0*self.dj[i][param][0] + 3.0*self.dj[i][param][1])
		dr2 = dr2_dipole + dr2_csa
		return dr2


	def calc_dnoe_iso(self, i, param):
		"Calculate the derivative of the Isotropic NOE value."

		r1 = self.ri[self.mf.data.noe_r1_table[i]]
		dr1 = self.dri[self.mf.data.noe_r1_table[i]][param]
		if r1 == 0:
			print "R1 is zero, this should not occur."
			dnoe = 1e99
		elif dr1 == 0:
			dnoe = (self.mf.data.dipole_const / r1) * (self.mf.data.gh/self.mf.data.gx) * (6.0*self.dj[i][4] - self.dj[i][2])
		else:
			dnoe = (r1 * (6.0*self.dj[i][param][4] - self.dj[i][param][2]) - (6.0*self.j[i][4] - self.j[i][2]) * dr1) / r1**2
			dnoe = self.mf.data.dipole_const * (self.mf.data.gh/self.mf.data.gx) * dnoe
		return dnoe


	def calc_r1_iso(self, i):
		"Calculate the Isotropic R1 value."

		r1_dipole = self.mf.data.dipole_const * (self.j[i][2] + 3.0*self.j[i][1] + 6.0*self.j[i][4])
		r1_csa = self.mf.data.csa_const[self.frq_num] * self.j[i][1]
		r1 = r1_dipole + r1_csa
		return r1


	def calc_r2_iso(self, i):
		"Calculate the Isotropic R2 value."

		r2_dipole = (self.mf.data.dipole_const/2.0) * (4.0*self.j[i][0] + self.j[i][2] + 3.0*self.j[i][1] + 6.0*self.j[i][3] + 6.0*self.j[i][4])
		r2_csa = (self.mf.data.csa_const[self.frq_num]/6.0) * (4.0*self.j[i][0] + 3.0*self.j[i][1])
		# Rex frq dep problem.
		if match('m[34]', self.options[2]):
			r2 = r2_dipole + r2_csa + self.rex
		else:
			r2 = r2_dipole + r2_csa
		return r2


	def calc_noe_iso(self, i):
		"Calculate the Isotropic NOE value."

		r1 = self.ri[self.mf.data.noe_r1_table[i]]
		if r1 == 0:
			noe = 1e99
		else:
			noe = 1.0 + (self.mf.data.dipole_const / r1) * (self.mf.data.gh/self.mf.data.gx) * (6.0*self.j[i][4] - self.j[i][2])
		return noe
