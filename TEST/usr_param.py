# usr_param.py          v0.1                  10 November 2001        Edward d'Auvergne
#
# Class containing all the user specified parameters.  Used by the program modelfree.
# Make sure the version numbers between the program and this class are identical.


class usr_param:
	def __init__(self):
		"Class containing parameters specified by the user"

		self.init_method_param()
		self.init_run_param()
		self.init_mfin_param()
		self.init_mfpar_param()
		self.init_mfmodel_param()


	def init_method_param(self):
		"""Modelfree analysis method info.
		
		self.method can be set to the following strings:
			Palmer - The method given by Mandel et al., 1995.
			AIC - method of modelfree analysis based on model selection using the
				Akaike Information Criteria.
			BIC - method of modelfree analysis based on model selection using the
				Schwartz Information Criteria.
		"""
		#self.method = 'Palmer'
		#self.method = 'AIC'
		self.method = 'BIC'

		# The following three values are only used in Palmer's method and won't affect the others.
		self.sse_lim = '0.90'       # Set the SSE limit (1 - alpha critical value).
		self.ftest_lim = '0.80'     # Set the F-test limit (1 - alpha critical value).
		self.large_sse = '20'        # Set the SSE limit for when much greater than the SSE limit.

		
	def init_run_param(self):
		"Run file parameters"
		
		self.pdb_file = 'Ap4Aase_new_3.pdb'
		self.pdb_path = './'
		self.pdb_full = self.pdb_path + self.pdb_file


	def init_mfin_param(self):
		"mfin file parameters"

		self.diff = 'isotropic'
		#self.diff = 'axial'
		self.no_sim = '100'
		self.trim = '0'               # Trim unconverged simulations.

		# tm
		self.tm = {}
		self.tm['val']   = '11.09'
		self.tm['flag']  = '1'
		self.tm['bound'] = '2'
		self.tm['lower'] = '9.0'
		self.tm['upper'] = '13.0'
		self.tm['steps'] = '100'

		# dratio
		self.dratio = {}
		self.dratio['val']   = '1.123'
		self.dratio['flag']  = '1'
		self.dratio['bound'] = '0'
		self.dratio['lower'] = '0.6'
		self.dratio['upper'] = '1.5'
		self.dratio['steps'] = '5'

		# theta
		self.theta = {}
		self.theta['val']   = '87.493'
		self.theta['flag']  = '1'
		self.theta['bound'] = '0'
		self.theta['lower'] = '-90'
		self.theta['upper'] = '90'
		self.theta['steps'] = '10'

		# phi
		self.phi = {}
		self.phi['val']   = '-52.470'
		self.phi['flag']  = '1'
		self.phi['bound'] = '0'
		self.phi['lower'] = '-90'
		self.phi['upper'] = '90'
		self.phi['steps'] = '10'


	def init_mfpar_param(self):
		"mfpar file parameters"

		self.const = {}
		self.const['nucleus'] = 'N15'
		self.const['gamma']   = '-2.710'
		self.const['rxh']     = '1.020'
		self.const['csa']     = '-170.00'

		self.vector = {}
		self.vector['atom1'] = 'N'
		self.vector['atom2'] = 'H'


	def init_mfmodel_param(self):
		"mfmodel file parameters"

		self.md1 = {}
		self.md1['tloc'] = {}
		self.md1['tloc']['start'] = '0.0'
		self.md1['tloc']['flag']  = '0'
		self.md1['tloc']['bound'] = '2'
		self.md1['tloc']['lower'] = '0.000'
		self.md1['tloc']['upper'] = '20.000'
		self.md1['tloc']['steps'] = '20'

		self.md1['theta'] = {}
		self.md1['theta']['start'] = '0.0'
		self.md1['theta']['flag']  = '0'
		self.md1['theta']['bound'] = '2'
		self.md1['theta']['lower'] = '0.000'
		self.md1['theta']['upper'] = '90.000'
		self.md1['theta']['steps'] = '20'

		self.md1['sf2'] = {}
		self.md1['sf2']['start'] = '1.0'
		self.md1['sf2']['flag']  = '0'
		self.md1['sf2']['bound'] = '2'
		self.md1['sf2']['lower'] = '0.000'
		self.md1['sf2']['upper'] = '1.000'
		self.md1['sf2']['steps'] = '20'

		self.md1['ss2'] = {}
		self.md1['ss2']['start'] = '1.0'
		self.md1['ss2']['flag']  = '0'
		self.md1['ss2']['bound'] = '2'
		self.md1['ss2']['lower'] = '0.000'
		self.md1['ss2']['upper'] = '1.000'
		self.md1['ss2']['steps'] = '20'
		
		self.md1['te'] = {}
		self.md1['te']['start'] = '0.0'
		self.md1['te']['flag']  = '0'
		self.md1['te']['bound'] = '2'
		self.md1['te']['lower'] = '0.000'
		self.md1['te']['upper'] = '10000.000'
		self.md1['te']['steps'] = '20'

		self.md1['rex'] = {}
		self.md1['rex']['start'] = '0.0'
		self.md1['rex']['flag']  = '0'
		self.md1['rex']['bound'] = '-1'
		self.md1['rex']['lower'] = '0.000'
		self.md1['rex']['upper'] = '20.000'
		self.md1['rex']['steps'] = '20'

		self.md2 = {}
		for param in self.md1.keys():
			self.md2[param] = {}
			for value in self.md1[param].keys():
				self.md2[param][value] = self.md1[param][value]
