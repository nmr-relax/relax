# The method given by Farrow et al., 1994:
#
#	Stage 1:   Creation of the files for the initial model-free calculations for models 1 to 5,
#		and f-tests between them.
#	Stage 2:   Model selection.
#

import sys
from re import match

from common_ops import common_operations


class farrow(common_operations):
	def __init__(self, mf):
		"The model-free analysis of Farrow."

		self.mf = mf

		print "Farrow's method for model-free analysis. (Farrow et al., 1994)"
		self.initialize()
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
		self.mf.data.mfin.default_data()
		self.goto_stage()


	def farrows_tests(self):
		"Check the 95% confidence limits and if the parameter is greater than its error."

		data = self.mf.data.data
		relax_data = self.mf.data.relax_data

		for res in range(len(relax_data[0])):
			for model in self.mf.data.runs:
				# 95% confidence limit test.
				fail = 0
				for set in range(len(relax_data)):
					label_fit = self.mf.data.input_info[set][1] + "_" + self.mf.data.input_info[set][0] + "_fit"
					diff = self.mf.data.relax_data[set][res][2] - self.mf.data.data[model][res][label_fit]
					if diff < 0:
						diff = -diff
					limit = 1.96 * float(relax_data[set][res][3])
					if diff > limit:
						fail = fail + 1
				if fail == 0:
					data[model][res]['conf_lim'] = 1
				else:
					data[model][res]['conf_lim'] = 0

				# Parameter greater than err test.
				if match('m1', model):
					params = [ data[model][res]['s2'] ]
					errs = [ data[model][res]['s2_err'] ]
				if match('m2', model):
					params = [ data[model][res]['s2'], data[model][res]['te'] ]
					errs = [ data[model][res]['s2_err'], data[model][res]['te_err'] ]
				if match('m3', model):
					params = [ data[model][res]['s2'], data[model][res]['rex'] ]
					errs = [ data[model][res]['s2_err'], data[model][res]['rex_err'] ]
				if match('m4', model):
					params = [ data[model][res]['s2'], data[model][res]['te'], data[model][res]['rex'] ]
					errs = [ data[model][res]['s2_err'], data[model][res]['te_err'], data[model][res]['rex_err'] ]
				if match('m5', model):
					params = [ data[model][res]['s2f'], data[model][res]['s2s'], data[model][res]['te'] ]
					errs = [ data[model][res]['s2f_err'], data[model][res]['s2s_err'], data[model][res]['te_err'] ]
				data[model][res]['param_test'] = self.test_param(params, errs)


	def model_selection(self):
		"Farrow's model selection."

		data = self.mf.data.data
		self.farrows_tests()

		self.mf.log.write("\n\n<<< Farrow's model selection >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			self.model = '0'

			# Model 1 to 5 tests.
			model_tests = [ 0, 0, 0, 0, 0 ]
			if data['m1'][res]['conf_lim'] == 1 and data['m1'][res]['param_test'] == 1:
				model_tests[0] = 1
			if data['m2'][res]['conf_lim'] == 1 and data['m2'][res]['param_test'] == 1:
				model_tests[1] = 1
			if data['m3'][res]['conf_lim'] == 1 and data['m3'][res]['param_test'] == 1:
				model_tests[2] = 1
			if data['m4'][res]['conf_lim'] == 1 and data['m4'][res]['param_test'] == 1:
				model_tests[3] = 1
			if data['m5'][res]['conf_lim'] == 1 and data['m5'][res]['param_test'] == 1:
				model_tests[4] = 1

			# Check if multiple models pass (m1 to m4).
			# Pick the model with the lowest chi squared value.
			for i in range(4):
				if match('0', self.model) and model_tests[i] == 1:
					self.model = `i + 1`
				elif not match('0', self.model) and model_tests[i] == 1:
					# Test if the chi2 of this new model is lower than the chi2 of the old.
					if data["m"+`i+1`][res]['chi2'] < data["m"+self.model][res]['chi2']:
						self.model = `i + 1`

			# Model 5 test (only if no other models fit).
			if match('0', self.model) and model_tests[4] == 1:
				self.model = '5'

			# Fill in the results.
			if not match('0', self.model):
				self.mf.data.results[res] = self.fill_results(data["m"+self.model][res], model=self.model)
			else:
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
			for model in self.mf.data.runs:
				file.write('%8.3f' % self.mf.data.data[model][res]['s2'])
				file.write('%1s' % '±')
				file.write('%-8.3f' % self.mf.data.data[model][res]['s2_err'])

			# S2f.
			file.write('\n%-20s' % 'S2f')
			for model in self.mf.data.runs:
				file.write('%8.3f' % self.mf.data.data[model][res]['s2f'])
				file.write('%1s' % '±')
				file.write('%-8.3f' % self.mf.data.data[model][res]['s2f_err'])

			# S2s.
			file.write('\n%-20s' % 'S2s')
			for model in self.mf.data.runs:
				file.write('%8.3f' % self.mf.data.data[model][res]['s2s'])
				file.write('%1s' % '±')
				file.write('%-8.3f' % self.mf.data.data[model][res]['s2s_err'])

			# te.
			file.write('\n%-20s' % 'te')
			for model in self.mf.data.runs:
				file.write('%8.3f' % self.mf.data.data[model][res]['te'])
				file.write('%1s' % '±')
				file.write('%-8.3f' % self.mf.data.data[model][res]['te_err'])

			# Rex.
			file.write('\n%-20s' % 'Rex')
			for model in self.mf.data.runs:
				file.write('%8.3f' % self.mf.data.data[model][res]['rex'])
				file.write('%1s' % '±')
				file.write('%-8.3f' % self.mf.data.data[model][res]['rex_err'])

			# Chi2.
			file.write('\n%-20s' % 'Chi2')
			for model in self.mf.data.runs:
				file.write('%-17.3f' % self.mf.data.data[model][res]['chi2'])

			# 95% confidence limits.
			file.write('\n%-20s' % '95% conf limits')
			for model in self.mf.data.runs:
				file.write('%-17i' % self.mf.data.data[model][res]['conf_lim'])

			# Parameters greater than errors test.
			file.write('\n%-20s' % 'params > errs')
			for model in self.mf.data.runs:
				file.write('%-17i' % self.mf.data.data[model][res]['param_test'])

			# Relaxation values
			for set in range(len(self.mf.data.relax_data)):
				file.write('\n%-20s' % (self.mf.data.input_info[set][1] + " " + self.mf.data.input_info[set][0]))
				for model in self.mf.data.runs:
					label_fit = self.mf.data.input_info[set][1] + "_" + self.mf.data.input_info[set][0] + "_fit"
					file.write('%8.3f' % self.mf.data.relax_data[set][res][2])
					file.write('%1s' % "|")
					file.write('%-8.3f' % self.mf.data.data[model][res][label_fit])
				file.write('\n   %-20s' % "diff ± 95%")
				for model in self.mf.data.runs:
					label_fit = self.mf.data.input_info[set][1] + "_" + self.mf.data.input_info[set][0] + "_fit"
					diff = self.mf.data.relax_data[set][res][2] - self.mf.data.data[model][res][label_fit]
					if diff < 0:
						diff = -diff
					file.write('%8.3f' % diff)
					file.write('%1s' % '±')
					file.write('%-8.3f' % (1.96 * float(self.mf.data.relax_data[set][res][3])))


		file.write('\n')
		sys.stdout.write("]\n")
		file.close()


	def set_vars_stage_initial(self):
		"Set the options for the initial runs."

		self.mf.data.mfin.sims = 'y'


	def set_vars_stage_selection(self):
		"Set the options for the final run."

		self.mf.data.mfin.sims = 'y'


	def test_param(self, params, errs):
		test = 1
		for i in range(len(params)):
			if params[i] < errs[i]:
				test = 0
		return test


