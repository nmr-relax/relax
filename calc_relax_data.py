from re import match


class calc_relax_data:
	def __init__(self, mf):
		"Class containing functions to calculate relaxation data values from given model-free parameters."

		self.mf = mf


	def calc(self, model, type, frq, mf_params):
		"""Main function for the calculation of all relaxation values.

		The arguments are:
		1: model - one of the following, {m1, m2, m3, m4, m5}
		2: type - one of the following, {NOE, R1, R2}
		3: frq - the proton Lamor frequency in MHz
		4: mf_params - a list containing the model-free parameters specific for the given model.
		The order of model-free parameters must be as follows:
			m1 - {S2}
			m2 - {S2, te}
			m3 - {S2, Rex}
			m4 - {S2, te, Rex}
			m5 - {S2f, S2s, ts}
		"""

		self.model = model
		self.type = type
		self.frq = frq
		self.mf_params = mf_params
		tm = float(self.mf.data.usr_param.tm['val'])
		for i in range(len(self.mf.data.nmr_frq)):
			if float(self.frq) == float(self.mf.data.nmr_frq[i][1]):
				self.frq_num = i

		if match('m1', self.model):
			self.s2 = float(self.mf_params[0])
			self.te = 0
			self.rex = 0
		elif match('m2', self.model):
			self.s2 = float(self.mf_params[0])
			self.te = float(self.mf_params[1])
			self.rex = 0
		elif match('m3', self.model):
			self.s2 = float(self.mf_params[0])
			self.te = 0
			self.rex = float(self.mf_params[1])
		elif match('m4', self.model):
			self.s2 = float(self.mf_params[0])
			self.te = float(self.mf_params[1])
			self.rex = float(self.mf_params[2])
		elif match('m5', self.model):
			self.s2f = float(self.mf_params[0])
			self.s2s = float(self.mf_params[1])
			self.ts = float(self.mf_params[2])
			self.rex = 0

		self.j = [0, 0, 0, 0, 0]
		if match('m[1-4]', self.model):
			self.j[0] = self.calc_jw_single(self.mf.data.frq[self.frq_num][0], tm, self.s2, self.te)
			self.j[1] = self.calc_jw_single(self.mf.data.frq[self.frq_num][1], tm, self.s2, self.te)
			self.j[2] = self.calc_jw_single(self.mf.data.frq[self.frq_num][2], tm, self.s2, self.te)
			self.j[3] = self.calc_jw_single(self.mf.data.frq[self.frq_num][3], tm, self.s2, self.te)
			self.j[4] = self.calc_jw_single(self.mf.data.frq[self.frq_num][4], tm, self.s2, self.te)
		else:
			self.j[0] = self.calc_jw_double(self.mf.data.frq[self.frq_num][0], tm, self.s2f, self.s2s, self.ts)
			self.j[1] = self.calc_jw_double(self.mf.data.frq[self.frq_num][1], tm, self.s2f, self.s2s, self.ts)
			self.j[2] = self.calc_jw_double(self.mf.data.frq[self.frq_num][2], tm, self.s2f, self.s2s, self.ts)
			self.j[3] = self.calc_jw_double(self.mf.data.frq[self.frq_num][3], tm, self.s2f, self.s2s, self.ts)
			self.j[4] = self.calc_jw_double(self.mf.data.frq[self.frq_num][4], tm, self.s2f, self.s2s, self.ts)


		if match('NOE', self.type):
			self.value = self.calc_noe()
		elif match('R1', self.type):
			self.value = self.calc_r1()
		elif match('R2', self.type):
			self.value = self.calc_r2()
		return self.value


	def calc_jw_single(self, frq, tm, s2, te):
		jw = ( s2*tm ) / ( 1 + (tm*frq)**2 )
		if te != 0:
			te_prime = 1 / ( 1/tm + 1/te )
			jw = jw + ( 1-s2 )*te_prime / ( 1 + (te_prime*frq)**2 )
		return jw


	def calc_jw_double(self, frq, tm, s2f, s2s, ts):
		jw = ( s2f*tm ) / ( 1 + (tm*frq)**2 )
		if ts != 0:
			ts_prime = 1 / ( 1/tm + 1/ts )
			jw = jw + ( 1-s2s )*ts_prime / ( 1 + (ts_prime*frq)**2 )
		return jw


	def calc_noe(self):
		"Calculate the NOE value."

		r1 = self.calc_r1()
		noe = 1 + ( self.mf.data.gh/self.mf.data.gn ) * ( 1/r1 ) * ( 6*self.j[4] - self.j[2] )
		return noe


	def calc_r1(self):
		"Calculate the R1 value."

		r1_dipole = self.mf.data.dipole_const * ( self.j[2] + 3*self.j[1] + 6*self.j[4] )
		r1_csa = self.mf.data.csa_const[self.frq_num] * ( self.j[1] )
		r1 = r1_dipole + r1_csa
		return r1


	def calc_r2(self):
		"Calculate the R2 value."

		r2_dipole = self.mf.data.dipole_const/2 * ( 4*self.j[0] + self.j[1] + 3*self.j[2] + 6*self.j[3] + 6*self.j[4])
		r2_csa = self.mf.data.csa_const[self.frq_num] * ( 4*self.j[0] + 3*self.j[1] )
		r2 = r2_dipole + r2_csa + self.rex
		return r2
