from re import match


class calc_relax_data:
	def __init__(self, mf):
		"Class containing functions to calculate relaxation data values from given model-free parameters."

		self.mf = mf


	def calc(self, tm, model, types, mf_params):
		"""Main function for the calculation of all relaxation values.

		The arguments are:
		1: model - one of the following, {m1, m2, m3, m4, m5}
		2: types - a 2D data structure where the first dimension is a list of each data set, and the second is:
			[0] - one of the following, {NOE, R1, R2}
			[1] - the proton Lamor frequency in MHz
		3: mf_params - a list containing the model-free parameters specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}
		"""

		self.model = model
		self.types = types
		self.mf_params = mf_params
		self.tm = tm
		self.rex = []

		if match('m1', self.model):
			self.s2  = float(self.mf_params[0])
			self.s2f = float(self.mf_params[0])
			self.s2s = 1.0
			self.tf  = 0.0 * 1e-12
			self.ts  = 0.0 * 1e-12
			for i in range(len(self.mf.data.nmr_frq)):
				self.rex.append(0.0)
		elif match('m2', self.model):
			self.s2  = float(self.mf_params[0])
			self.s2f = float(self.mf_params[0])
			self.s2s = 1.0
			self.tf  = float(self.mf_params[1]) * 1e-12
			self.ts  = 0.0 * 1e-12
			for i in range(len(self.mf.data.nmr_frq)):
				self.rex.append(0.0)
		elif match('m3', self.model):
			self.s2  = float(self.mf_params[0])
			self.s2f = float(self.mf_params[0])
			self.s2s = 1.0
			self.tf  = 0.0 * 1e-12
			self.ts  = 0.0 * 1e-12
			for i in range(len(self.mf.data.nmr_frq)):
				self.rex.append(float(self.mf_params[1]) * ( (float(self.mf.data.nmr_frq[i][1]) / float(self.mf.data.nmr_frq[0][1]))**2 ))
		elif match('m4', self.model):
			self.s2  = float(self.mf_params[0])
			self.s2f = float(self.mf_params[0])
			self.s2s = 1.0
			self.tf  = float(self.mf_params[1]) * 1e-12
			self.ts  = 0.0 * 1e-12
			for i in range(len(self.mf.data.nmr_frq)):
				self.rex.append(float(self.mf_params[2]) * ( (float(self.mf.data.nmr_frq[i][1]) / float(self.mf.data.nmr_frq[0][1]))**2 ))
		elif match('m5', self.model):
			self.s2  = float(self.mf_params[0]) * float(self.mf_params[1])
			self.s2f = float(self.mf_params[0])
			self.s2s = float(self.mf_params[1])
			self.tf  = 0.0 * 1e-12
			self.ts  = float(self.mf_params[2]) * 1e-12
			for i in range(len(self.mf.data.nmr_frq)):
				self.rex.append(0.0)

		# Debugging code, do not remove!
		#
		#self.mf.log.write("\nS2: ")
		#self.mf.log.write("%-7.4f" % self.s2)
		#self.mf.log.write(" | S2f: ")
		#self.mf.log.write("%-7.4f" % self.s2f)
		#self.mf.log.write(" | S2s: ")
		#self.mf.log.write("%-7.4f" % self.s2s)
		#self.mf.log.write(" | tf: ")
		#self.mf.log.write("%-7s" % `self.tf`)
		#self.mf.log.write(" | ts: ")
		#self.mf.log.write("%-7s" % `self.ts`)
		#for i in range(len(self.mf.data.nmr_frq)):
		#	self.mf.log.write(" | " + self.mf.data.nmr_frq[i][0] + " rex: ")
		#	self.mf.log.write("%-7.4f" % self.rex[i])

		self.tf_prime = ( self.tf * self.tm ) / ( self.tf + self.tm )
		self.ts_prime = ( self.ts * self.tm ) / ( self.ts + self.tm )

		self.j = []
		for i in range(len(self.mf.data.nmr_frq)):
			self.j.append([0.0, 0.0, 0.0, 0.0, 0.0])
			self.j[i][0] = self.calc_jw(self.mf.data.frq[i][0])
			self.j[i][1] = self.calc_jw(self.mf.data.frq[i][1])
			self.j[i][2] = self.calc_jw(self.mf.data.frq[i][2])
			self.j[i][3] = self.calc_jw(self.mf.data.frq[i][3])
			self.j[i][4] = self.calc_jw(self.mf.data.frq[i][4])

		self.back_calc = []
		for i in range(len(self.types)):
			for j in range(len(self.mf.data.nmr_frq)):
				if self.types[i][1] == float(self.mf.data.nmr_frq[j][1]):
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
			noe = 1e99
		else:
			noe = 1.0 + ( self.mf.data.dipole_const / r1 ) * ( self.mf.data.gh/self.mf.data.gn ) * ( 6.0*self.j[self.frq_num][4] - self.j[self.frq_num][2] )
		return noe


	def calc_r1(self, frq):
		"Calculate the R1 value."

		r1_dipole = self.mf.data.dipole_const * ( self.j[self.frq_num][2] + 3.0*self.j[self.frq_num][1] + 6.0*self.j[self.frq_num][4] )
		r1_csa = self.mf.data.csa_const[self.frq_num] * ( self.j[self.frq_num][1] )
		r1 = r1_dipole + r1_csa
		return r1


	def calc_r2(self, frq):
		"Calculate the R2 value."

		r2_dipole = (self.mf.data.dipole_const/2.0) * ( 4.0*self.j[self.frq_num][0] + self.j[self.frq_num][2] + 3.0*self.j[self.frq_num][1] + 6.0*self.j[self.frq_num][3] + 6.0*self.j[self.frq_num][4])
		r2_csa = (self.mf.data.csa_const[self.frq_num]/6.0) * ( 4.0*self.j[self.frq_num][0] + 3.0*self.j[self.frq_num][1] )
		r2 = r2_dipole + r2_csa + self.rex[self.frq_num]
		return r2
