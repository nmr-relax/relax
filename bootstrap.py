# A method based on asymptotic model selection criteria.
#
# The following asymptotic methods are supported:
#	AIC - Akaike Information Criteria
#	BIC - Schwartz Criteria
#
# The program is divided into the following stages:
#	Stage 1:   Creation of the files for the modelfree calculations for models 1 to 5.  Monte Carlo
#		simulations are not used on these initial runs, because the errors are not needed (should
#		speed up analysis considerably).
#	Stage 2a:   Model selection and the creation of the final run.  Monte Carlo simulations are used to
#		find errors, and the diffusion tensor is unoptimized.  Files are placed in the directory
#		'final'.
#	Stage 2b:   Model selection and the creation of the final optimization run. The modelfree
#		input files for optimization are placed into the directory 'optimize'.
#	Stage 3:   Extraction of optimized data.

import sys
from math import log, pi
from re import match

from common_ops import common_operations


class asymptotic(common_operations):
	def __init__(self, mf):
		"Modelfree analysis based on asymptotic model selection methods."

		self.mf = mf

		print "Modelfree analysis based on " + self.mf.data.usr_param.method + " model selection."
		self.mf.data.asymptotic.stage = self.ask_stage()
		title = "<<< Stage " + self.mf.data.asymptotic.stage + " of the asymptotic criteria based modelfree analysis >>>\n\n\n"
		self.start_up(self.mf.data.asymptotic.stage, title)
		
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5']

		if match('1', self.mf.data.asymptotic.stage):
			print "\n[ Stage 1 ]\n"
			self.initial_runs(sims='n')
			print "\n[ End of stage 1 ]\n\n"

		if match('2a', self.mf.data.asymptotic.stage):
			print "\n[ Stage 2a ]\n"
			self.mf.file_ops.mkdir('final')
			self.stage2()
			self.final_run()
			print "\n[ End of stage 2a ]\n\n"

		if match('2b', self.mf.data.asymptotic.stage):
			print "\n[ Stage 2b ]\n"
			self.mf.file_ops.mkdir('optimize')
			self.stage2()
			self.final_run_optimized()
			print "\n[ End of stage 2b ]\n\n"

		if match('3', self.mf.data.asymptotic.stage):
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
		print "   Stage 2 (2a):   Model selection and creation of a final run with simulations."
		print "   Stage 2 (2b):   Model selection and creation of a final optimization run."
		print "   Stage 3 (3):    Extraction of optimized data."
		print "For more information, see the file 'asymptotic.py'"

		while 1:
			stage = raw_input('> ')
			valid_stages = ['1', '2a', '2b', '3']
			if stage in valid_stages:
				break
			else:
				print "Invalid stage number.  Choose either 1, 2a, 2b, or 3."
		print "The stage chosen is " + stage + "\n"
		return stage


	def bic_model_selection(self):
		"BIC model selection."
		
		data = self.mf.data.data

		self.mf.log.write("\n\n<<< BIC model selection >>>")
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
			bic = n*log(2*pi) + sum_ln_err + data['m1'][res]['sse'] + log(1)
			bic = bic / ( 2 * n )
			data['m1'][res]['bic'] = bic

			# Model 2.
			bic = n*log(2*pi) + sum_ln_err + data['m2'][res]['sse'] + log(2)
			bic = bic / ( 2 * n )
			data['m2'][res]['bic'] = bic

			# Model 3.
			bic = n*log(2*pi) + sum_ln_err + data['m3'][res]['sse'] + log(2)
			bic = bic / ( 2 * n )
			data['m3'][res]['bic'] = bic

			# Model 4.
			bic = n*log(2*pi) + sum_ln_err + data['m4'][res]['sse'] + log(3)
			bic = bic / ( 2 * n )
			data['m4'][res]['bic'] = bic

			# Model 5.
			bic = n*log(2*pi) + sum_ln_err + data['m5'][res]['sse'] + log(3)
			bic = bic / ( 2 * n )
			data['m5'][res]['bic'] = bic

			# Select model.
			min = 'm1'
			for run in self.mf.data.runs:
				if data[run][res]['bic'] < data[min][res]['bic']:
					min = run
			self.mf.data.results[res] = self.fill_results(data[min][res], model=min[1])

			self.mf.log.write("\n\tBIC (m1): " + `data['m1'][res]['bic']` + "\n")
			self.mf.log.write("\tBIC (m2): " + `data['m2'][res]['bic']` + "\n")
			self.mf.log.write("\tBIC (m3): " + `data['m3'][res]['bic']` + "\n")
			self.mf.log.write("\tBIC (m4): " + `data['m4'][res]['bic']` + "\n")
			self.mf.log.write("\tBIC (m5): " + `data['m5'][res]['bic']` + "\n")
			self.mf.log.write("\tThe selected model is: " + min + "\n\n")


	def stage2(self):
		self.mf.file_ops.mkdir('grace')
		
		print "\n[ Modelfree data extraction ]\n"
		for run in self.mf.data.runs:
			mfout = self.mf.file_ops.read_file(run + '/mfout')
			mfout_lines = mfout.readlines()
			mfout.close()
			print "Extracting modelfree data from " + run + "/mfout."
			num_res = len(self.mf.data.relax_data[0])
			self.mf.data.data[run] = self.mf.star.extract(mfout_lines, num_res)

		if match('AIC', self.mf.data.usr_param.method):
			print "\n[ AIC model selection ]\n"
			self.aic_model_selection()
		elif match('BIC', self.mf.data.usr_param.method):
			print "\n[ BIC model selection ]\n"
			self.bic_model_selection()

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
