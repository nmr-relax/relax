# A method based on AIC model selection.  There are two stages:
#
#	Stage 1:   Creation of the files for the modelfree calculations for models 1 to 5.  Monte Carlo
#		simulations are not used on these initial runs, because the errors are not needed (should
#		speed up analysis considerably).
#	Stage 2:   Model selection and the creation of the final run.  Monte Carlo simulations are used to
#		find errors, and the diffusion tensor is unoptimized.  Files are placed in the directory
#		'final'.

import sys
from math import log, pi
from re import match

from common_ops import common_operations


class aic(common_operations):
	def __init__(self, mf):
		"Modelfree analysis based on AIC model selection."

		self.mf = mf
		print "Modelfree analysis based on AIC model selection."
		self.mf.data.aic.stage = self.ask_stage()
		self.init_log_file(self.mf.data.aic.stage)

		self.mf.file_ops.input()
		self.extract_relax_data()
		self.log_input_info()
		
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']

		if match('1', self.mf.data.aic.stage):
			print "\n[ Stage 1 ]\n"
			self.stage1()
			print "\n[ End of stage 1 ]\n\n"

		if match('2a', self.mf.data.aic.stage):
			print "\n[ Stage 2a ]\n"
			self.stage2()
			print "\n[ End of stage 2a ]\n\n"

		if match('2b', self.mf.data.aic.stage):
			print "\n[ Stage 2b ]\n"
			self.mkdir('optimize')
			self.stage2()
			self.final_optimization()
			print "\n[ End of stage 2b ]\n\n"

		if match('3', self.mf.data.aic.stage):
			print "\n[ Stage 3 ]\n"
			self.stage3()
			print "\n[ End of stage 3 ]\n\n"


	def aic_model_selection(self):
		"AIC model selection."
		
		data = self.mf.data.data

		self.mf.log.write("\n\n<<< AIC model selection >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			# Set up.
			n = self.mf.data.num_data_sets

			sum_ln_err = 0
			for i in range(len(self.mf.data.relax_data)):
				ln_err = log(float(self.mf.data.relax_data[i][res][3]))
				sum_ln_err = sum_ln_err + ln_err

			# Model 1.
			aic = n*log(2*pi) + sum_ln_err + data['m1'][res]['sse'] + 2*1
			aic = aic / ( 2 * n )
			data['m1'][res]['aic'] = aic

			# Model 2.
			aic = n*log(2*pi) + sum_ln_err + data['m2'][res]['sse'] + 2*2
			aic = aic / ( 2 * n )
			data['m2'][res]['aic'] = aic

			# Model 3.
			aic = n*log(2*pi) + sum_ln_err + data['m3'][res]['sse'] + 2*2
			aic = aic / ( 2 * n )
			data['m3'][res]['aic'] = aic

			# Model 4.
			aic = n*log(2*pi) + sum_ln_err + data['m4'][res]['sse'] + 2*3
			aic = aic / ( 2 * n )
			data['m4'][res]['aic'] = aic

			# Model 5.
			aic = n*log(2*pi) + sum_ln_err + data['m5'][res]['sse'] + 2*3
			aic = aic / ( 2 * n )
			data['m5'][res]['aic'] = aic

			# Select model.
			min = 'm1'
			for run in self.mf.data.runs:
				if data[run][res]['aic'] < data[min][res]['aic']:
					min = run
			self.mf.data.results[res] = self.fill_results(data[min][res], model=min[1])

			self.mf.log.write("\n\tAIC (m1): " + `data['m1'][res]['aic']` + "\n")
			self.mf.log.write("\tAIC (m2): " + `data['m2'][res]['aic']` + "\n")
			self.mf.log.write("\tAIC (m3): " + `data['m3'][res]['aic']` + "\n")
			self.mf.log.write("\tAIC (m4): " + `data['m4'][res]['aic']` + "\n")
			self.mf.log.write("\tAIC (m5): " + `data['m5'][res]['aic']` + "\n")
			self.mf.log.write("\tThe selected model is: " + min + "\n\n")





	def ask_stage(self):
		"User input of stage number."

		print "\n[ Select the stage for Modelfree analysis ]\n"
		print "The stages are:"
		print "   Stage 1 (1):    Creation of the files for the modelfree calculations for models 1 to 5."
		print "   Stage 2 (2a):   AIC model selection."
		print "   Stage 2 (2b):   AIC model selection and creation of a final optimization run."
		print "   Stage 3 (3):    Extraction of optimized data."
		while 1:
			stage = raw_input('> ')
			valid_stages = ['1', '2a', '2b', '3']
			if stage in valid_stages:
				break
			else:
				print "Invalid stage number.  Choose either 1, 2a, 2b, or 3."
		print "The stage chosen is " + stage + "\n"
		return stage


	def init_log_file(self, stage):
		"Initialize the log file."
		
		self.mf.log = open('log.stage' + stage, 'w')
		self.mf.log.write("<<< Stage " + stage + " of the AIC based modelfree analysis >>>\n\n\n")


	def stage1(self):
		"""Creation of the files for the modelfree calculations for models 1 to 5.

		Monte Carlo simulations are not used on these initial runs, because the errors are not
		needed (should speed up analysis considerably).
		"""

		for run in self.mf.data.runs:
			print "Creating input files for model " + run
			self.mf.log.write("\n\n<<< Model " + run + " >>>\n\n")
			self.mkdir(dir=run)
			self.open_mf_files(dir=run)
			self.set_run_flags(run)
			self.log_params('M1', self.mf.data.usr_param.md1)
			self.log_params('M2', self.mf.data.usr_param.md2)
			self.create_mfin(run, sims='n')
			self.create_run(dir=run)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				self.create_mfmodel(res, self.mf.data.usr_param.md1, type='M1')
				# Mfpar.
				self.create_mfpar(res)
			self.close_files(dir=run)


	def stage2(self):
		"AIC model selection."

		self.mkdir('grace')
		
		print "\n[ Modelfree data extraction ]\n"
		for run in self.mf.data.runs:
			mfout = self.read_file(run + '/mfout')
			mfout_lines = mfout.readlines()
			mfout.close()
			print "Extracting modelfree data from " + run + "/mfout."
			num_res = len(self.mf.data.relax_data[0])
			self.mf.data.data[run] = self.mf.star.extract(mfout_lines, num_res)

		print "\n[ AIC model selection ]\n"
		self.aic_model_selection()

		print "\n[ Printing results ]\n"
		self.print_results()

		print "\n[ Placing data structures into \"data_all\" ]\n"
		self.print_data()

		print "\n[ Grace file creation ]\n"
		self.grace('grace/S2.agr', 'S2', subtitle="After model selection, unoptimized")
		self.grace('grace/S2f.agr', 'S2f', subtitle="After model selection, unoptimized")
		self.grace('grace/S2s.agr', 'S2s', subtitle="After model selection, unoptimized")
		self.grace('grace/te.agr', 'te', subtitle="After model selection, unoptimized")
		self.grace('grace/Rex.agr', 'Rex', subtitle="After model selection, unoptimized")
		self.grace('grace/SSE.agr', 'SSE', subtitle="After model selection, unoptimized")


	def stage3(self):
		print "Stage 3 not implemented yet.\n"
		sys.exit()
