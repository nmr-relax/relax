# Calculate the overall discrepancy.
#
# The input relaxation data for this method should be the operating model data (the theoretical, back calculated
# relaxation values) which has been Gaussian randomised for a given error.  The original operating model data
# should be placed in the file 'op_data'.  The format of the file should be as follows.  The first line is a
# header line and is ignored.  The columns are:
#	0 - Residue number.
#	1 - Residue name.
#	2+ - The real data.  Each column from 2 on should correspond to the data specified in the file 'input'.
#	When the data in 'input' is 'none', there should be no corresponding column.
#
#
# The program is divided into the following stages:
#	Stage 1:   Creation of the files for the model-free calculations for models 1 to 5 for the randomised
#		data.
#	Stage 2a:  Calculation of the overall discrepancy for model selection, and the creation of the final
#		run.  Monte Carlo simulations are used to find errors, and the diffusion tensor is unoptimised.
#		Files are placed in the directory 'final'.
#	Stage 2b:  Calculation of the overall discrepancy for model selection, and the creation of the final
#		optimization run.  Monte Carlo simulations are used to find errors, and the diffusion tensor
#		is optimised.  Files are placed in the directory 'optimised'.
#	Stage 3:   Extraction of optimised data.

import sys
from math import log, pi

from common_ops import common_operations


class overall_disc(common_operations):
	def __init__(self, mf):
		"Calculation of the theoretical overall discrepancy."

		self.mf = mf


	def model_selection(self):
		"Model selection."

		data = self.mf.data.data
		self.mf.data.calc_frq()
		self.mf.data.calc_constants()
		n = float(self.mf.data.num_data_sets)
		tm = float(self.mf.usr_param.tm['val']) * 1e-9

		if self.mf.debug == 1:
			self.mf.log.write("\n\n<<< " + self.mf.usr_param.method + " model selection >>>\n\n")

		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})

			if self.mf.debug == 1:
				self.mf.log.write('%-22s\n' % ( "Checking res " + data['m1'][res]['res_num'] ))

			real = []
			err = []
			types = []
			for set in range(len(self.mf.data.relax_data)):
				real.append(float(self.mf.data.overall_disc.op_data[res][set+2]))
				err.append(float(self.mf.data.relax_data[set][res][3]))
				types.append([self.mf.data.input_info[set][0], float(self.mf.data.input_info[set][2])])

			for model in self.mf.data.runs:
				back_calc = []
				for set in range(len(self.mf.data.relax_data)):
					label_fit = self.mf.data.input_info[set][1] + "_" + self.mf.data.input_info[set][0] + "_fit"
					back_calc.append(float(self.mf.data.data[model][res][label_fit]))

				chi2 = self.mf.calc_chi2.relax_data(real, err, back_calc)

				if self.mf.debug == 1:
					self.mf.log.write("\nReal: " + `real`)
					self.mf.log.write("\nError: " + `err`)
					self.mf.log.write("\nBack calc: " + `back_calc`)

				data[model][res]['crit'] = chi2 / (2.0 * n)

			# Select model.
			min = 'm1'
			for run in self.mf.data.runs:
				if data[run][res]['crit'] < data[min][res]['crit']:
					min = run
			if data[min][res]['crit'] == float('inf'):
				self.mf.data.results[res] = self.fill_results(data[min][res], model='0')
			else:
				self.mf.data.results[res] = self.fill_results(data[min][res], model=min[1])

			if self.mf.debug == 1:
				self.mf.log.write(self.mf.usr_param.method + " (m1): " + `data['m1'][res]['crit']` + "\n")
				self.mf.log.write(self.mf.usr_param.method + " (m2): " + `data['m2'][res]['crit']` + "\n")
				self.mf.log.write(self.mf.usr_param.method + " (m3): " + `data['m3'][res]['crit']` + "\n")
				self.mf.log.write(self.mf.usr_param.method + " (m4): " + `data['m4'][res]['crit']` + "\n")
				self.mf.log.write(self.mf.usr_param.method + " (m5): " + `data['m5'][res]['crit']` + "\n")
				self.mf.log.write("The selected model is: " + min + "\n\n")


	def print_data(self):
		"Print all the data into the 'data_all' file."

		file = open('data_all', 'w')
		file_crit = open('crit', 'w')

		sys.stdout.write("[")
		for res in range(len(self.mf.data.results)):
			sys.stdout.write("-")
			file.write("\n\n<<< Residue " + self.mf.data.results[res]['res_num'])
			file.write(", Model " + self.mf.data.results[res]['model'] + " >>>\n")
			file.write('%-20s' % '')
			file.write('%-19s' % 'Model 1')
			file.write('%-19s' % 'Model 2')
			file.write('%-19s' % 'Model 3')
			file.write('%-19s' % 'Model 4')
			file.write('%-19s' % 'Model 5')

			file_crit.write('%-6s' % self.mf.data.results[res]['res_num'])
			file_crit.write('%-6s' % self.mf.data.results[res]['model'])

			# S2.
			file.write('\n%-20s' % 'S2')
			for run in self.mf.data.runs:
				file.write('%9.3f' % self.mf.data.data[run][res]['s2'])
				file.write('%1s' % '±')
				file.write('%-9.3f' % self.mf.data.data[run][res]['s2_err'])

			# S2f.
			file.write('\n%-20s' % 'S2f')
			for run in self.mf.data.runs:
				file.write('%9.3f' % self.mf.data.data[run][res]['s2f'])
				file.write('%1s' % '±')
				file.write('%-9.3f' % self.mf.data.data[run][res]['s2f_err'])

			# S2s.
			file.write('\n%-20s' % 'S2s')
			for run in self.mf.data.runs:
				file.write('%9.3f' % self.mf.data.data[run][res]['s2s'])
				file.write('%1s' % '±')
				file.write('%-9.3f' % self.mf.data.data[run][res]['s2s_err'])

			# te.
			file.write('\n%-20s' % 'te')
			for run in self.mf.data.runs:
				file.write('%9.2f' % self.mf.data.data[run][res]['te'])
				file.write('%1s' % '±')
				file.write('%-9.2f' % self.mf.data.data[run][res]['te_err'])

			# Rex.
			file.write('\n%-20s' % 'Rex')
			for run in self.mf.data.runs:
				file.write('%9.3f' % self.mf.data.data[run][res]['rex'])
				file.write('%1s' % '±')
				file.write('%-9.3f' % self.mf.data.data[run][res]['rex_err'])

			# Chi2.
			file.write('\n%-20s' % 'Chi2')
			for run in self.mf.data.runs:
				file.write('%-19.3f' % self.mf.data.data[run][res]['chi2'])

			# Model selection criteria.
			file.write('\n%-20s' % self.mf.usr_param.method)
			for run in self.mf.data.runs:
				file.write('%-19.6f' % self.mf.data.data[run][res]['crit'])

				file_crit.write('%-25s' % `self.mf.data.data[run][res]['crit']`)
			file_crit.write('\n')

		file.write('\n')
		sys.stdout.write("]\n")
		file.close()
