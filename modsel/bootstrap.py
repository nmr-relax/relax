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


	def model_selection(self):
		"Model selection."

		data = self.mf.data.data
		self.mf.data.calc_frq()
		self.mf.data.calc_constants()
		n = float(self.mf.data.num_data_sets)
		tm = float(self.mf.data.usr_param.tm['val']) * 1e-9

		if self.mf.debug == 1:
			self.mf.log.write("\n\n<<< Bootstrap model selection >>>\n\n")

		print "Calculating the bootstrap criteria"
		for res in range(len(self.mf.data.relax_data[0])):
			print "Residue: " + self.mf.data.relax_data[0][res][1] + " " + self.mf.data.relax_data[0][res][0]
			self.mf.data.results.append({})
			file_name = self.mf.data.relax_data[0][res][1] + '_' + self.mf.data.relax_data[0][res][0] + '.out'

			if self.mf.debug == 1:
				self.mf.log.write('%-22s\n' % ( "< Checking res " + data['m1'][res]['res_num'] + " >\n"))

			real = []
			err = []
			types = []
			for set in range(len(self.mf.data.relax_data)):
				real.append(float(self.mf.data.relax_data[set][res][2]))
				err.append(float(self.mf.data.relax_data[set][res][3]))
				types.append([self.mf.data.input_info[set][0], float(self.mf.data.input_info[set][2])])

			for model in self.mf.data.runs:
				if self.mf.debug == 1:
					self.mf.log.write("\nCalculating bootstrap estimate for res " + `res` + ", model " + model + "\n\n")
					for set in range(len(self.mf.data.input_info)):
						self.mf.log.write("-------------------")
					self.mf.log.write("\n")
					for set in range(len(self.mf.data.input_info)):
						name = " Orig " + self.mf.data.input_info[set][1] + " " + self.mf.data.input_info[set][0]
						self.mf.log.write("%-17s%2s" % (name, " |"))
					self.mf.log.write("\n")
					for set in range(len(self.mf.data.input_info)):
						self.mf.log.write("%8.4f" % self.mf.data.relax_data[set][res][2])
						self.mf.log.write("%1s" % "±")
						self.mf.log.write("%-8.4f" % self.mf.data.relax_data[set][res][3])
						self.mf.log.write("%2s" % " |")
					self.mf.log.write("\n")
					for set in range(len(self.mf.data.input_info)):
						self.mf.log.write("-------------------")
					self.mf.log.write("\n\n")

				file = self.mf.file_ops.open_file(model + "/" + file_name)
				sum_chi2 = 0.0
				num_sims = float(len(file))
				for sim in range(len(file)):
					if self.mf.debug == 1:
						self.mf.log.write("%5s%-10i%2s" % ("Sim: ", sim, " |"))

					#if match('m1', model):
					#	back_calc = self.mf.calc_relax_data.calc(tm, model, types, [ file[sim][2] ])
					#elif match('m2', model) or match('m3', model):
					#	back_calc = self.mf.calc_relax_data.calc(tm, model, types, [ file[sim][2], file[sim][3] ])
					#elif match('m4', model) or match('m5', model):
					#	back_calc = self.mf.calc_relax_data.calc(tm, model, types, [ file[sim][2], file[sim][3], file[sim][4] ])
					#chi2 = self.mf.calc_chi2.relax_data(real, err, back_calc)
					chi2 = float(file[sim][1])
					sum_chi2 = sum_chi2 + chi2

					if self.mf.debug == 1:
						self.mf.log.write("%7s%-10.4f%2s" % (" Chi2: ", chi2, " |"))
						self.mf.log.write("%11s%-13.4f%2s\n" % (" Sum Chi2: ", sum_chi2, " |"))

				ave_chi2 = sum_chi2 / num_sims

				if self.mf.debug == 1:
					self.mf.log.write("\nAverage Chi2 is: " + `ave_chi2` + "\n\n")

				data[model][res]['bootstrap'] = ave_chi2 / (2.0 * n)

			# Select model.
			min = 'm1'
			for model in self.mf.data.runs:
				if data[model][res]['bootstrap'] < data[min][res]['bootstrap']:
					min = model
			if data[min][res]['crit'] == float('inf'):
				self.mf.data.results[res] = self.fill_results(data[min][res], model='0')
			else:
				self.mf.data.results[res] = self.fill_results(data[min][res], model=min[1])

			if self.mf.debug == 1:
				self.mf.log.write(self.mf.data.usr_param.method + " (m1): " + `data['m1'][res]['bootstrap']` + "\n")
				self.mf.log.write(self.mf.data.usr_param.method + " (m2): " + `data['m2'][res]['bootstrap']` + "\n")
				self.mf.log.write(self.mf.data.usr_param.method + " (m3): " + `data['m3'][res]['bootstrap']` + "\n")
				self.mf.log.write(self.mf.data.usr_param.method + " (m4): " + `data['m4'][res]['bootstrap']` + "\n")
				self.mf.log.write(self.mf.data.usr_param.method + " (m5): " + `data['m5'][res]['bootstrap']` + "\n")
				self.mf.log.write("The selected model is: " + min + "\n\n")

			print "   Model " + self.mf.data.results[res]['model']


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
			for model in self.mf.data.runs:
				file.write('%9.3f' % self.mf.data.data[model][res]['s2'])
				file.write('%1s' % '±')
				file.write('%-9.3f' % self.mf.data.data[model][res]['s2_err'])

			# S2f.
			file.write('\n%-20s' % 'S2f')
			for model in self.mf.data.runs:
				file.write('%9.3f' % self.mf.data.data[model][res]['s2f'])
				file.write('%1s' % '±')
				file.write('%-9.3f' % self.mf.data.data[model][res]['s2f_err'])

			# S2s.
			file.write('\n%-20s' % 'S2s')
			for model in self.mf.data.runs:
				file.write('%9.3f' % self.mf.data.data[model][res]['s2s'])
				file.write('%1s' % '±')
				file.write('%-9.3f' % self.mf.data.data[model][res]['s2s_err'])

			# te.
			file.write('\n%-20s' % 'te')
			for model in self.mf.data.runs:
				file.write('%9.2f' % self.mf.data.data[model][res]['te'])
				file.write('%1s' % '±')
				file.write('%-9.2f' % self.mf.data.data[model][res]['te_err'])

			# Rex.
			file.write('\n%-20s' % 'Rex')
			for model in self.mf.data.runs:
				file.write('%9.3f' % self.mf.data.data[model][res]['rex'])
				file.write('%1s' % '±')
				file.write('%-9.3f' % self.mf.data.data[model][res]['rex_err'])

			# Chi2.
			file.write('\n%-20s' % 'Chi2')
			for model in self.mf.data.runs:
				file.write('%-19.3f' % self.mf.data.data[model][res]['chi2'])

			# Bootstrap criteria.
			file.write('\n%-20s' % 'Bootstrap')
			for model in self.mf.data.runs:
				file.write('%-19.3f' % self.mf.data.data[model][res]['bootstrap'])

				file_crit.write('%-25s' % `self.mf.data.data[model][res]['bootstrap']`)
			file_crit.write('\n')

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
