# The method given by (Mandel et al., 1995) is divided into the three stages:
#
#	Stage 1:  Creation of the files for the initial model-free calculations for models 1 to 5,
#		and f-tests between them.
#	Stage 2:  Model selection and the creation of the final run.  Monte Carlo simulations are used to
#		find errors.  This stage has the option of optimizing the diffusion tensor along with the
#		model-free parameters.
#	Stage 3:  Extraction of the data.
#
# These stages are repeated until the data converges.

import sys
from re import match

from common_ops import common_operations


class palmer(common_operations):
	def __init__(self, mf):
		"The model-free analysis of Palmer."

		self.mf = mf

		print "Palmer's method for model-free analysis. (Mandel et al., 1995)"
		self.initialize()
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'f-m1m2', 'f-m1m3']
		if self.mf.data.num_data_sets > 3:
			self.mf.data.runs.append('f-m2m4')
			self.mf.data.runs.append('f-m2m5')
			self.mf.data.runs.append('f-m3m4')
		self.mf.data.mfin.default_data()
		self.goto_stage()


	def anova_tests(self):
		"Do the chi squared and F-tests."

		for res in range(len(self.mf.data.relax_data[0])):
			for run in self.mf.data.runs:
				if match('^m', run):
					# Chi squared test.
					if self.mf.data.data[run][res]['chi2'] <= self.mf.data.data[run][res]['chi2_lim']:
						self.mf.data.data[run][res]['chi2_test'] = 1
					else:
						self.mf.data.data[run][res]['chi2_test'] = 0

					# Large chi squared test.
					if self.mf.data.data[run][res]['chi2'] >= float(self.mf.data.usr_param.large_chi2):
						self.mf.data.data[run][res]['large_chi2'] = 1
					else:
						self.mf.data.data[run][res]['large_chi2'] = 0

					# Zero chi squared test.
					if self.mf.data.data[run][res]['chi2'] == 0.0:
						self.mf.data.data[run][res]['zero_chi2'] = 1
					else:
						self.mf.data.data[run][res]['zero_chi2'] = 0

				else:
					# F-test.
					if self.mf.data.data[run][res]['fstat_lim'] < 1.5:
						if self.mf.data.data[run][res]['fstat'] > 1.5:
							self.mf.data.data[run][res]['ftest'] = 1
						else:
							self.mf.data.data[run][res]['ftest'] = 0
					elif self.mf.data.data[run][res]['fstat_lim'] >= 1.5:
						if self.mf.data.data[run][res]['fstat'] > self.mf.data.data[run][res]['fstat_lim']:
							self.mf.data.data[run][res]['ftest'] = 1
						else:
							self.mf.data.data[run][res]['ftest'] = 0

	def model_selection(self):
		"Palmer's model selection."

		self.anova_tests()
		if self.mf.data.num_data_sets > 3:
			# ie degrees of freedom > 0 in all models.
			self.mf.log.write("Extended model selection.\n\n")
			print "The number of data sets is greater than 3."
			print "\tRunning Palmer's model selection, with additional chi-squared and F-tests"
			print "\tfor models 4 and 5 (the degrees of freedom for these models are greater than 0).\n"
			self.model_selection_extended()
		else:
			self.mf.log.write("Normal model selection.\n\n")
			print "The number of data sets is equal to 3."
			print "\tRunning Palmer's model selection.\n"
			self.model_selection_normal()


	def model_selection_normal(self):
		"Palmer's model selection."

		data = self.mf.data.data

		self.mf.log.write("\n\n<<< Palmer's model selection >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			# Model 1 test.
			if data['m1'][res]['chi2_test'] == 1:
				self.mf.log.write('%-12s' % '[Model 1]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 2 and 3 fit!!! (Should not occur)
			elif data['m2'][res]['chi2_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1 \
				and data['m3'][res]['chi2_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2 and 3]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='2+3')

			# Model 2 test.
			elif data['m2'][res]['chi2_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2]')
				self.mf.data.results[res] = self.fill_results(data['m2'][res], model='2')

			# Model 3 test.
			elif data['m3'][res]['chi2_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 3]')
				self.mf.data.results[res] = self.fill_results(data['m3'][res], model='3')

			# Large chi squared test for model 1.
			elif data['m1'][res]['large_chi2'] == 0:
				self.mf.log.write('%-12s' % '[Model 1*]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 4 and 5 fit!!! (Should not occur)
			elif data['m4'][res]['zero_chi2'] == 1 and data['m5'][res]['zero_chi2'] == 1:
				self.mf.log.write('%-12s' % '[Model 4 and 5]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='4+5')

			# Model 4 test.
			elif data['m4'][res]['zero_chi2'] == 1:
				self.mf.log.write('%-12s' % '[Model 4]')
				self.mf.data.results[res] = self.fill_results(data['m4'][res], model='4')

			# Model 5 test.
			elif data['m5'][res]['zero_chi2'] == 1:
				self.mf.log.write('%-12s' % '[Model 5]')
				self.mf.data.results[res] = self.fill_results(data['m5'][res], model='5')

			# No model fits!
			else:
				self.mf.log.write('%-12s' % '[Model 0]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='0')


	def model_selection_extended(self):
		"""Palmer's model selection (extended).

		Palmer's model selection, but with additional chi-squared and F-tests for models 4 and 5
		because the number of degrees of freedom for these models are greater than 0.  See the code
		below for details of these changes.
		"""

		data = self.mf.data.data

		self.mf.log.write("\n\n<<< Palmer's model selection (extended) >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			# Model 1 test.
			if data['m1'][res]['chi2_test'] == 1:
				self.mf.log.write('%-12s' % '[Model 1]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 2 and 3 fit!!! (Should not occur)
			elif data['m2'][res]['chi2_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1 \
				and data['m3'][res]['chi2_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2 and 3]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='2+3')

			# Model 2 test.
			elif data['m2'][res]['chi2_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2]')
				self.mf.data.results[res] = self.fill_results(data['m2'][res], model='2')

			# Model 3 test.
			elif data['m3'][res]['chi2_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 3]')
				self.mf.data.results[res] = self.fill_results(data['m3'][res], model='3')

			# Large chi squared test for model 1.
			elif data['m1'][res]['large_chi2'] == 0:
				self.mf.log.write('%-12s' % '[Model 1*]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 4 and 5 fit!!! (Should not occur)
			elif data['m4'][res]['chi2_test'] == 1 and ( data['f-m2m4'][res]['ftest'] == 1 or data['f-m3m4'][res]['ftest'] == 1 ) \
				and data['m5'][res]['chi2_test'] == 1 and data['f-m2m5'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 4 and 5]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='4+5')

			# Model 4 test.
			elif data['m4'][res]['chi2_test'] == 1 and ( data['f-m2m4'][res]['ftest'] == 1 or data['f-m3m4'][res]['ftest'] == 1 ):
				self.mf.log.write('%-12s' % '[Model 4]')
				self.mf.data.results[res] = self.fill_results(data['m4'][res], model='4')

			# Model 5 test.
			elif data['m5'][res]['chi2_test'] == 1 and data['f-m2m5'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 5]')
				self.mf.data.results[res] = self.fill_results(data['m5'][res], model='5')

			# No model fits!
			else:
				self.mf.log.write('%-12s' % '[Model 0]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='0')


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
					file.write('%8.3f' % self.mf.data.data[run][res]['s2'])
					file.write('%1s' % '±')
					file.write('%-8.3f' % self.mf.data.data[run][res]['s2_err'])

			# S2f.
			file.write('\n%-20s' % 'S2f')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8.3f' % self.mf.data.data[run][res]['s2f'])
					file.write('%1s' % '±')
					file.write('%-8.3f' % self.mf.data.data[run][res]['s2f_err'])

			# S2s.
			file.write('\n%-20s' % 'S2s')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8.3f' % self.mf.data.data[run][res]['s2s'])
					file.write('%1s' % '±')
					file.write('%-8.3f' % self.mf.data.data[run][res]['s2s_err'])

			# te.
			file.write('\n%-20s' % 'te')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8.3f' % self.mf.data.data[run][res]['te'])
					file.write('%1s' % '±')
					file.write('%-8.3f' % self.mf.data.data[run][res]['te_err'])

			# Rex.
			file.write('\n%-20s' % 'Rex')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%8.3f' % self.mf.data.data[run][res]['rex'])
					file.write('%1s' % '±')
					file.write('%-8.3f' % self.mf.data.data[run][res]['rex_err'])

			# Chi2.
			file.write('\n%-20s' % 'Chi2')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17.3f' % self.mf.data.data[run][res]['chi2'])

			# Chi2 limit.
			file.write('\n%-20s' % 'Chi2 limit')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17.3f' % self.mf.data.data[run][res]['chi2_lim'])

			# Chi2 test.
			file.write('\n%-20s' % 'Chi2 test')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17s' % self.mf.data.data[run][res]['chi2_test'])

			# large Chi2.
			file.write('\n%-20s' % 'large Chi2')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17s' % self.mf.data.data[run][res]['large_chi2'])

			# zero Chi2.
			file.write('\n%-20s' % 'zero Chi2')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17s' % self.mf.data.data[run][res]['zero_chi2'])

		file.write('\n')
		sys.stdout.write("]\n")
		file.close()


	def set_vars_stage_initial(self):
		"Set the options for the initial runs."

		self.mf.data.mfin.sims = 'y'


	def set_vars_stage_selection(self):
		"Set the options for the final run."

		self.mf.data.mfin.sims = 'y'
