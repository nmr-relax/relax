# A method based on model selection using bootstrap criteria.
#
# The Kullback-Leibeler discrepancy is used.
#
# The program is divided into the following stages:
#	Stage 1:  Creation of the files for the model-free calculations for models 1 to 5.  Monte Carlo
#		simulations are used, but the initial data rather than the backcalculated data is randomized.
#	Stage 2:  Model selection and the creation of the final run.  Monte Carlo simulations are used to
#		find errors.  This stage has the option of optimizing the diffusion tensor along with the
#		model-free parameters.
#	Stage 3:  Extraction of the data.

import sys
from re import match

from common_ops import common_operations


class bootstrap(common_operations):
	def __init__(self, mf):
		"Model-free analysis based on bootstrap model selection."

		self.mf = mf

		print "Model-free analysis based on bootstrap criteria model selection."
		self.initialize()
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
		self.mf.data.mfin.default_data()
		self.goto_stage()


	def model_selection(self):
		print "\n[ Bootstrap criteria model selection ]\n"


	def print_data(self):
		"Print all the data into the 'data_all' file."

		file = open('data_all', 'w')

		sys.stdout.write("[")
		for res in range(len(self.mf.data.results)):
			sys.stdout.write("-")
			file.write("\n\n<<< Residue " + self.mf.data.results[res]['res_num'])
			file.write(", Model " + self.mf.data.results[res]['model'] + " >>>\n")
			file.write('%-20s' % '')
			file.write('%-17s' % 'Model 1')
			file.write('%-17s' % 'Model 2')
			file.write('%-17s' % 'Model 3')
			file.write('%-17s' % 'Model 4')
			file.write('%-17s' % 'Model 5')

			# S2.
			file.write('\n%-20s' % 'S2')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8s' % self.mf.data.data[run][res]['s2'])
					file.write('%1s' % '±')
					file.write('%-8s' % self.mf.data.data[run][res]['s2_err'])

			# S2f.
			file.write('\n%-20s' % 'S2f')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8s' % self.mf.data.data[run][res]['s2f'])
					file.write('%1s' % '±')
					file.write('%-8s' % self.mf.data.data[run][res]['s2f_err'])

			# S2s.
			file.write('\n%-20s' % 'S2s')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8s' % self.mf.data.data[run][res]['s2s'])
					file.write('%1s' % '±')
					file.write('%-8s' % self.mf.data.data[run][res]['s2s_err'])

			# te.
			file.write('\n%-20s' % 'te')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8s' % self.mf.data.data[run][res]['te'])
					file.write('%1s' % '±')
					file.write('%-8s' % self.mf.data.data[run][res]['te_err'])

			# Rex.
			file.write('\n%-20s' % 'Rex')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8s' % self.mf.data.data[run][res]['rex'])
					file.write('%1s' % '±')
					file.write('%-8s' % self.mf.data.data[run][res]['rex_err'])

			# Chi2.
			file.write('\n%-20s' % 'Chi2')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17s' % self.mf.data.data[run][res]['chi2'])

			# Bootstrap criteria.
			file.write('\n%-20s' % 'Bootstrap criteria')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17s' % self.mf.data.data[run][res]['bootstrap'])

		file.write('\n')
		sys.stdout.write("]\n")
		file.close()


	def set_vars_stage_initial(self):
		"Set the options for the initial runs."
		
		self.mf.data.mfin.sims = 'y'
		self.mf.data.mfin.sim_type = 'expr'


	def set_vars_stage_selection(self):
		"Set the options for the final run."
		
		self.mf.data.mfin.sims = 'y'
		self.mf.data.mfin.sim_type = 'pred'
