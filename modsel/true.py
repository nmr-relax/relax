# Calculate the overall discrepency.
#
# The input relaxation data for this method should be the operating model data (the theoretical, back calculated
# relaxation values) which has been Gaussian randomized for a given error.  The original operating model data
# should be placed in the file 'op_data'.  The format of the file should be as follows.  The first line is a
# header line and is ignored.  The columns are:
#	0 - Residue number.
#	1 - Residue name.
#	2+ - The real data.  Each column from 2 on should correspond to the data specified in the file 'input'.
#	When the data in 'input' is 'none', there should be no corresponding column.
#
#
# The program is divided into the following stages:
#	Stage 1:   Creation of the files for the modelfree calculations for models 1 to 5 for the randomized
#		data.
#	Stage 2a:  Calculation of the overall discrepency for model selection, and the creation of the final
#		run.  Monte Carlo simulations are used to find errors, and the diffusion tensor is unoptimized.
#		Files are placed in the directory 'final'.
#	Stage 2b:  Calculation of the overall discrepency for model selection, and the creation of the final
#		optimization run.  Monte Carlo simulations are used to find errors, and the diffusion tensor
#		is optimized.  Files are placed in the directory 'optimized'.
#	Stage 3:   Extraction of optimized data.

import sys
from math import log, pi
from re import match

from common_ops import common_operations


class true(common_operations):
	def __init__(self, mf):
		"Calculation of the theoretical overall discrepency."

		self.mf = mf

		print "Modelfree analysis based on the overall discrepency for model selection."
		self.initialize()
		message = "See the file 'modsel/true.py' for details.\n"
		self.mf.file_ops.read_file('op_data', message)
		self.mf.data.true.op_data = self.mf.file_ops.open_file(file_name='op_data')
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']
		self.mf.data.mfin.default_data()
		self.goto_stage()


	def calc_crit(self, res, model, mf_data, n):
		"Calculate the criteria"

		real = []
		real_err = []
		types = []
		sum_ln_err = 0.0

		for set in range(len(self.mf.data.input_info)):
			# Sum ln(errors).
			var = float(self.mf.data.relax_data[set][res][3]) ** 2
			if var == 0.0:
				ln_err = -1000.0
			else:
				ln_err = log(var)
			sum_ln_err = sum_ln_err + ln_err

			# Real data and errors.
			real.append(float(self.mf.data.true.op_data[res][set+2]))
			real_err.append(self.mf.data.relax_data[set][res][3])
			types.append([self.mf.data.input_info[set][0], float(self.mf.data.input_info[set][2])])

		if match('m1', model):
			back_calc = self.mf.calc_relax_data.calc(self.tm, model, types, mf_data)
		elif match('m2', model) or match('m3', model):
			back_calc = self.mf.calc_relax_data.calc(self.tm, model, types, mf_data)
		elif match('m4', model) or match('m5', model):
			back_calc = self.mf.calc_relax_data.calc(self.tm, model, types, mf_data)

		chi2 = self.mf.calc_chi2.relax_data(real, real_err, back_calc)

		self.mf.log.write("\nReal: " + `real`)
		self.mf.log.write("\nReal error: " + `real_err`)
		self.mf.log.write("\nBack calc: " + `back_calc`)

		crit = n*log(2.0*pi) + sum_ln_err + chi2
		crit = crit / (2.0*n)
		return crit

	def model_selection(self):
		"Model selection."

		data = self.mf.data.data
		self.mf.data.calc_frq()
		self.mf.data.calc_constants()
		n = len(self.mf.data.input_info)

		self.mf.log.write("\n\n<<< " + self.mf.data.usr_param.method + " model selection >>>")
		self.tm = float(self.mf.data.usr_param.tm['val'])*1e-9
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			n = self.mf.data.num_data_sets

			# Model 1.
			mf_data = [ data['m1'][res]['s2'] ]
			data['m1'][res]['crit'] = self.calc_crit(res, 'm1', mf_data, n)

			# Model 2.
			mf_data = [ data['m2'][res]['s2'], data['m2'][res]['te'] ]
			data['m2'][res]['crit'] = self.calc_crit(res, 'm2', mf_data, n)

			# Model 3.
			mf_data = [ data['m3'][res]['s2'], data['m3'][res]['rex'] ]
			data['m3'][res]['crit'] = self.calc_crit(res, 'm3', mf_data, n)

			# Model 4.
			mf_data = [ data['m4'][res]['s2'], data['m4'][res]['te'], data['m4'][res]['rex'] ]
			data['m4'][res]['crit'] = self.calc_crit(res, 'm4', mf_data, n)

			# Model 5.
			mf_data = [ data['m5'][res]['s2f'], data['m5'][res]['s2s'], data['m5'][res]['te'] ]
			data['m5'][res]['crit'] = self.calc_crit(res, 'm5', mf_data, n)

			# Select model.
			min = 'm1'
			for run in self.mf.data.runs:
				if data[run][res]['crit'] < data[min][res]['crit']:
					min = run
			self.mf.data.results[res] = self.fill_results(data[min][res], model=min[1])

			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m1): " + `data['m1'][res]['crit']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m2): " + `data['m2'][res]['crit']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m3): " + `data['m3'][res]['crit']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m4): " + `data['m4'][res]['crit']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m5): " + `data['m5'][res]['crit']` + "\n")
			self.mf.log.write("\tThe selected model is: " + min + "\n\n")


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

			# Model selection criteria.
			file.write('\n%-20s' % self.mf.data.usr_param.method)
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17.6f' % self.mf.data.data[run][res]['crit'])

		file.write('\n')
		sys.stdout.write("]\n")
		file.close()


	def set_vars_stage_initial(self):
		"Set the options for the initial runs."

		self.mf.data.mfin.sims = 'n'


	def set_vars_stage_selection(self):
		"Set the options for the final run."

		self.mf.data.mfin.sims = 'y'
