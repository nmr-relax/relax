# The method given by (Mandel et al., 1995) is divided into the three stages:
#
#	Stage 1:   Creation of the files for the modelfree calculations for models 1 to 5,
#		and f-tests between them.
#	Stage 2:   Model selection and creation of the final optimization run.  The modelfree
#		input files for optimization are placed into the directory "optimize".
#	Stage 3:   Extraction of optimized data.
#
# These stages are repeated until the data converges.

import sys
from re import match

from common_ops import common_operations


class palmer(common_operations):
	def __init__(self, mf):
		"The modelfree analysis of Palmer."

		self.mf = mf

		print "Palmer's method for modelfree analysis. (Mandel et al., 1995)"
		self.mf.data.palmer.stage = self.ask_stage()
		self.init_log_file(self.mf.data.palmer.stage)

		self.mf.file_ops.input()
		self.extract_relax_data()
		self.log_input_info()

		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'f-m1m2', 'f-m1m3']
		if self.mf.data.num_data_sets > 3:
			self.mf.data.runs.append('f-m2m4')
			self.mf.data.runs.append('f-m2m5')
			self.mf.data.runs.append('f-m3m4')

		if match('1', self.mf.data.palmer.stage):
			self.stage1()
		if match('2', self.mf.data.palmer.stage):
			self.stage2()
		if match('3', self.mf.data.palmer.stage):
			self.stage3()


	def ask_stage(self):
		"User input of stage number."

		print "\n[ Select the stage for Modelfree analysis ]\n"
		print "The stages are:"
		print "   Stage 1 (1):   Initial run of all models 1 to 5 and f-tests between them."
		print "   Stage 2 (2):   Model selection and creation of the final optimization run."
		print "   Stage 3 (3):   Extraction of optimized data."
		while 1:
			stage = raw_input('> ')
			valid_stages = ['1', '2', '3']
			if stage in valid_stages:
				break
			else:
				print "Invalid stage number.  Choose either 1, 2, or 3."
		print "The stage chosen is " + stage + "\n"
		return stage


	def init_log_file(self, stage):
		"Initialize the log file."
		
		self.mf.log = open('log.stage' + stage, 'w')
		text = "<<< Stage " + stage + " of Palmer's method for Modelfree "
		text = text + "analysis >>>\n\n\n"
		self.mf.log.write(text)


	def model_selection(self):
		"Palmer's model selection."

		self.mf.log.write("\n\n<<< Palmer's model selection >>>")


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
			if data['m1'][res]['sse_test'] == 1:
				self.mf.log.write('%-12s' % '[Model 1]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 2 and 3 fit!!! (Should not occur)
			elif data['m2'][res]['sse_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1 \
				and data['m3'][res]['sse_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2 and 3]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='2+3')

			# Model 2 test.
			elif data['m2'][res]['sse_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2]')
				self.mf.data.results[res] = self.fill_results(data['m2'][res], model='2')

			# Model 3 test.
			elif data['m3'][res]['sse_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 3]')
				self.mf.data.results[res] = self.fill_results(data['m3'][res], model='3')

			# Large SSE test for model 1.
			elif data['m1'][res]['large_sse'] == 0:
				self.mf.log.write('%-12s' % '[Model 1*]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 4 and 5 fit!!! (Should not occur)
			elif data['m4'][res]['sse_test'] == 1 and ( data['f-m2m4'][res]['ftest'] == 1 or data['f-m3m4'][res]['ftest'] == 1 ) \
				and data['m5'][res]['sse_test'] == 1 and data['f-m2m5'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 4 and 5]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='4+5')
				
			# Model 4 test.
			elif data['m4'][res]['sse_test'] == 1 and ( data['f-m2m4'][res]['ftest'] == 1 or data['f-m3m4'][res]['ftest'] == 1 ):
				self.mf.log.write('%-12s' % '[Model 4]')
				self.mf.data.results[res] = self.fill_results(data['m4'][res], model='4')
				
			# Model 5 test.
			elif data['m5'][res]['sse_test'] == 1 and data['f-m2m5'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 5]')
				self.mf.data.results[res] = self.fill_results(data['m5'][res], model='5')

			# No model fits!
			else:
				self.mf.log.write('%-12s' % '[Model 0]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='0')


	def stage1(self):
		print "\n[ Stage 1 ]\n"
		for run in self.mf.data.runs:
			if match('^m', run):
				print "Creating input files for model " + run
				self.mf.log.write("\n\n<<< Model " + run + " >>>\n\n")
			elif match('^f', run):
				print "Creating input files for the F-test " + run
				self.mf.log.write("\n\n<<< F-test " + run + " >>>\n\n")
			else:
				print "The run '" + run + "'does not start with an m or f, quitting script!\n\n"
				sys.exit()
			self.mkdir(dir=run)
			self.open_mf_files(dir=run)
			self.set_run_flags(run)
			self.log_params('M1', self.mf.data.usr_param.md1)
			self.log_params('M2', self.mf.data.usr_param.md2)
			if match('^m', run):
				self.create_mfin()
			elif match('^f', run):
				self.create_mfin(sel='ftest')
			self.create_run(dir=run)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
				self.create_mfmodel(self.mf.data.usr_param.md1, type='M1', header=text)
				if match('^f', run):
					self.create_mfmodel(self.mf.data.usr_param.md2, type='M2', header='\n')
				# Mfpar.
				self.create_mfpar(res)
			self.close_files(dir=run)
		print "\n[ End of stage 1 ]\n\n"


	def stage2(self):
		self.mkdir('optimize')
		self.mkdir('grace')

		print "\n[ Modelfree data extraction ]\n"
		for run in self.mf.data.runs:
			mfout = self.read_file(run + '/mfout')
			mfout_lines = mfout.readlines()
			mfout.close()
			print "Extracting modelfree data from " + run + "/mfout."
			num_res = len(self.mf.data.relax_data[0])
			if match('^m', run):
				self.mf.data.data[run] = self.mf.star.extract(mfout_lines, num_res, self.mf.data.usr_param.sse_lim, self.mf.data.usr_param.ftest_lim, float(self.mf.data.usr_param.large_sse), ftest='n')
			if match('^f', run):
				self.mf.data.data[run] = self.mf.star.extract(mfout_lines, num_res, self.mf.data.usr_param.sse_lim, self.mf.data.usr_param.ftest_lim, float(self.mf.data.usr_param.large_sse), ftest='y')

		print "\n[ Palmer's model selection ]\n"
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
			self.model_selection()

		print "\n[ Printing results ]\n"
		self.print_results()

		print "\n[ Placing data structures into \"data_all\" ]\n"
		self.print_data(ftests='y')

		print "\n[ Grace file creation ]\n"
		self.grace('grace/S2.agr', 'S2', subtitle="After model selection, unoptimized")
		self.grace('grace/S2f.agr', 'S2f', subtitle="After model selection, unoptimized")
		self.grace('grace/S2s.agr', 'S2s', subtitle="After model selection, unoptimized")
		self.grace('grace/te.agr', 'te', subtitle="After model selection, unoptimized")
		self.grace('grace/Rex.agr', 'Rex', subtitle="After model selection, unoptimized")
		self.grace('grace/SSE.agr', 'SSE', subtitle="After model selection, unoptimized")

		self.final_optimization()
		print "\n[ End of stage 2 ]\n\n"


	def stage3(self):
		print "Stage 3 not implemented yet.\n"
		sys.exit()
