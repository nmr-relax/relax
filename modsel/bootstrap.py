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
from math import log, pi
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


	def calc_crit(self, res, model, file, n):
		"Calculate the criteria."

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
			real.append(float(self.mf.data.relax_data[set][res][2]))
			real_err.append(float(self.mf.data.relax_data[set][res][3]))
			types.append([self.mf.data.input_info[set][0], float(self.mf.data.input_info[set][2])])


		#self.mf.log.write("\nCalculating bootstrap estimate for res " + `res` + ", model " + model + "\n\n")
		#for set in range(len(self.mf.data.input_info)):
		#	name = "Orig " + self.mf.data.input_info[set][1] + " " + self.mf.data.input_info[set][0]
		#	self.mf.log.write("%-17s" % name)
		#self.mf.log.write("\n")
		#for set in range(len(self.mf.data.input_info)):
		#	self.mf.log.write("%8.4f" % self.mf.data.relax_data[set][res][2])
		#	self.mf.log.write("%1s" % "±")
		#	self.mf.log.write("%-8.4f" % self.mf.data.relax_data[set][res][3])
		#self.mf.log.write("\n\n")

		sum_chi2 = 0.0
		for sim in range(len(file)):
			if match('m1', model):
				back_calc = self.mf.calc_relax_data.calc(self.tm, model, types, [ file[sim][2] ])
			elif match('m2', model) or match('m3', model):
				back_calc = self.mf.calc_relax_data.calc(self.tm, model, types, [ file[sim][2], file[sim][3] ])
			elif match('m4', model) or match('m5', model):
				back_calc = self.mf.calc_relax_data.calc(self.tm, model, types, [ file[sim][2], file[sim][3], file[sim][4] ])
			chi2 = self.mf.calc_chi2.relax_data(real, real_err, back_calc)
			sum_chi2 = sum_chi2 + chi2

			#self.mf.log.write("\n\nSim: " + `sim`)
			#self.mf.log.write("\n")
			#for set in range(len(self.mf.data.input_info)):
			#	self.mf.log.write(self.mf.data.input_info[set][1] + " " + self.mf.data.input_info[set][0] + ": ")
			#	self.mf.log.write("%-7.4f" % back_calc[set])
			#	self.mf.log.write(" | ")
			#self.mf.log.write("\nChi2: ")
			#self.mf.log.write("%-7.4f" % chi2)
			#self.mf.log.write(" | Sum Chi2: ")
			#self.mf.log.write("%-7.4f" % sum_chi2)

		num_sims = float(len(file))
		ave_chi2 = sum_chi2 / num_sims
		#self.mf.log.write("\nAverage Chi2 is: " + `ave_chi2` + "\n\n")

		#self.mf.log.write("A: " + `n*log(2.0*pi)` + "\nB: " + `sum_ln_err` + "\nC: " + `ave_chi2` + "\n")
		bootstrap = n*log(2.0*pi) + sum_ln_err + ave_chi2
		#self.mf.log.write("Bootstrap: " + `bootstrap` + "\n")
		bootstrap = bootstrap / (2.0*n)
		#self.mf.log.write("Bootstrap: " + `bootstrap` + "\n" + "\n")

		return bootstrap


	def model_selection(self):
		print "\n[ Bootstrap model selection ]\n"

		data = self.mf.data.data
		self.mf.data.calc_frq()
		self.mf.data.calc_constants()
		n = len(self.mf.data.input_info)

		print "Calculating the bootstrap criteria"
		self.mf.log.write("\n\n<<< Bootstrap model selection >>>")
		self.tm = float(self.mf.data.usr_param.tm['val'])*1e-9
		for res in range(len(self.mf.data.relax_data[0])):
			print "Residue: " + self.mf.data.relax_data[0][res][1] + " " + self.mf.data.relax_data[0][res][0]
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "< Checking res " + data['m1'][res]['res_num'] + " >\n"))
			file_name = self.mf.data.relax_data[0][res][1] + '_' + self.mf.data.relax_data[0][res][0] + '.out'

			# Model 1.
			file = self.mf.file_ops.open_file("m1/" + file_name)
			data['m1'][res]['bootstrap'] = self.calc_crit(res, 'm1', file, n)

			# Model 2.
			file = self.mf.file_ops.open_file("m2/" + file_name)
			data['m2'][res]['bootstrap'] = self.calc_crit(res, 'm2', file, n)

			# Model 3.
			file = self.mf.file_ops.open_file("m3/" + file_name)
			data['m3'][res]['bootstrap'] = self.calc_crit(res, 'm3', file, n)

			# Model 4.
			file = self.mf.file_ops.open_file("m4/" + file_name)
			data['m4'][res]['bootstrap'] = self.calc_crit(res, 'm4', file, n)

			# Model 5.
			file = self.mf.file_ops.open_file("m5/" + file_name)
			data['m5'][res]['bootstrap'] = self.calc_crit(res, 'm5', file, n)

			# Select model.
			min = 'm1'
			for run in self.mf.data.runs:
				if data[run][res]['bootstrap'] < data[min][res]['bootstrap']:
					min = run
			self.mf.data.results[res] = self.fill_results(data[min][res], model=min[1])

			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m1): " + `data['m1'][res]['bootstrap']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m2): " + `data['m2'][res]['bootstrap']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m3): " + `data['m3'][res]['bootstrap']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m4): " + `data['m4'][res]['bootstrap']` + "\n")
			self.mf.log.write("\n\t" + self.mf.data.usr_param.method + " (m5): " + `data['m5'][res]['bootstrap']` + "\n")
			self.mf.log.write("\tThe selected model is: " + min + "\n\n")

			print "   Model " + self.mf.data.results[res]['model']


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

			# Bootstrap criteria.
			file.write('\n%-20s' % 'Bootstrap')
			for run in self.mf.data.runs:
				if match('^m', run):
					file.write('%-17.3f' % self.mf.data.data[run][res]['bootstrap'])

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
