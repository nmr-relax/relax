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


	def fill_results(self, data, model='0'):
		"Initialize the next row of the results data structure."

		results = {}
		results['res_num']   = data['res_num']
		results['model']   = model
		if match('0', model) or match('2\+3', model) or match('4\+5', model):
			results['s2']      = ''
			results['s2_err']  = ''
			results['s2f']     = ''
			results['s2f_err'] = ''
			results['s2s']     = ''
			results['s2s_err'] = ''
			results['te']      = ''
			results['te_err']  = ''
			results['rex']     = ''
			results['rex_err'] = ''
			results['sse']     = data['sse']
		else:
			results['s2']      = data['s2']
			results['s2_err']  = data['s2_err']
			results['s2f']     = data['s2f']
			results['s2f_err'] = data['s2f_err']
			results['s2s']     = data['s2s']
			results['s2s_err'] = data['s2s_err']
			results['te']      = data['te']
			results['te_err']  = data['te_err']
			results['rex']     = data['rex']
			results['rex_err'] = data['rex_err']
			results['sse']     = data['sse']
		return results


	def grace(self, file, type, subtitle):
		"Create grace files for the results."

		text = self.grace_header('S2 values', subtitle, 'Residue Number', 'S2', 'xydy')
		for res in range(len(self.mf.data.results)):
			if match('S2', type) and match('^[0-9]', self.mf.data.results[res]['s2']):
				text = text + self.mf.data.results[res]['res_num'] + " "
				text = text + self.mf.data.results[res]['s2'] + " "
				text = text + self.mf.data.results[res]['s2_err'] + "\n"
			elif match('S2s', type) and match('^[0-9]', self.mf.data.results[res]['s2s']):
				text = text + self.mf.data.results[res]['res_num'] + " "
				text = text + self.mf.data.results[res]['s2s'] + " "
				text = text + self.mf.data.results[res]['s2s_err'] + "\n"
			elif match('S2f', type) and match('^[0-9]', self.mf.data.results[res]['s2f']):
				text = text + self.mf.data.results[res]['res_num'] + " "
				text = text + self.mf.data.results[res]['s2f'] + " "
				text = text + self.mf.data.results[res]['s2f_err'] + "\n"
			elif match('te', type) and match('^[0-9]', self.mf.data.results[res]['te']):
				text = text + self.mf.data.results[res]['res_num'] + " "
				text = text + self.mf.data.results[res]['te'] + " "
				text = text + self.mf.data.results[res]['te_err'] + "\n"
			elif match('Rex', type) and match('^[0-9]', self.mf.data.results[res]['rex']):
				text = text + self.mf.data.results[res]['res_num'] + " "
				text = text + self.mf.data.results[res]['rex'] + " "
				text = text + self.mf.data.results[res]['rex_err'] + "\n"
			elif match('SSE', type):
				text = text + self.mf.data.results[res]['res_num'] + " "
				text = text + `self.mf.data.results[res]['sse']` + "\n"
		text = text + "&\n"
		file.write(text)


	def grace_header(self, title, subtitle, x, y, type):
		"Create and return a grace header."

		text = "@version 50100\n"
		text = text + "@with g0\n"
		if match('Residue Number', x):
			text = text + "@    world xmax 165\n"
		if match('R1', x) and match('SSE', y):
			text = text + "@    world xmin 0.8\n"
			text = text + "@    world xmax 2\n"
			text = text + "@    world ymin 0\n"
			text = text + "@    world ymax 2000\n"
		if match('R2', x) and match('SSE', y):
			text = text + "@    world xmin 5\n"
			text = text + "@    world xmax 45\n"
			text = text + "@    world ymin 0\n"
			text = text + "@    world ymax 2000\n"
		if match('NOE', x) and match('SSE', y):
			text = text + "@    world xmin 0\n"
			text = text + "@    world xmax 1\n"
			text = text + "@    world ymin 0\n"
			text = text + "@    world ymax 2000\n"
		text = text + "@    view xmax 1.22\n"
		text = text + "@    title \"" + title + "\"\n"
		text = text + "@    subtitle \"" + subtitle + "\"\n"
		text = text + "@    xaxis  label \"" + x + "\"\n"
		if match('Residue Number', x):
			text = text + "@    xaxis  tick major 10\n"
		if match('R1', x) and match('SSE', y):
			text = text + "@    xaxis  tick major 0.2\n"
		if match('R2', x) and match('SSE', y):
			text = text + "@    xaxis  tick major 5\n"
		if match('NOE', x) and match('SSE', y):
			text = text + "@    xaxis  tick major 0.1\n"
		text = text + "@    xaxis  tick major size 0.480000\n"
		text = text + "@    xaxis  tick major linewidth 0.5\n"
		text = text + "@    xaxis  tick minor linewidth 0.5\n"
		text = text + "@    xaxis  tick minor size 0.240000\n"
		text = text + "@    xaxis  ticklabel char size 0.790000\n"
		text = text + "@    yaxis  label \"" + y + "\"\n"
		if match('R1', x) and match('SSE', y):
			text = text + "@    yaxis  tick major 200\n"
		if match('R2', x) and match('SSE', y):
			text = text + "@    yaxis  tick major 200\n"
		if match('NOE', x) and match('SSE', y):
			text = text + "@    yaxis  tick major 200\n"
		text = text + "@    yaxis  tick major size 0.480000\n"
		text = text + "@    yaxis  tick major linewidth 0.5\n"
		text = text + "@    yaxis  tick minor linewidth 0.5\n"
		text = text + "@    yaxis  tick minor size 0.240000\n"
		text = text + "@    yaxis  ticklabel char size 0.790000\n"
		text = text + "@    frame linewidth 0.5\n"
		text = text + "@    s0 symbol 1\n"
		text = text + "@    s0 symbol size 0.49\n"
		text = text + "@    s0 symbol fill pattern 1\n"
		text = text + "@    s0 symbol linewidth 0.5\n"
		text = text + "@    s0 line linestyle 0\n"
		text = text + "@target G0.S0\n@type " + type + "\n"
		return text


	def init_log_file(self, stage):
		"Initialize the log file."
		
		self.mf.log = open('log.stage' + stage, 'w')
		text = "<<< Stage " + stage + " of Palmer's method for Modelfree "
		text = text + "analysis >>>\n\n\n"
		self.mf.log.write(text)


	def init_stage2_files(self):
		"Open the stage 2 specific files."
		
		self.data_file = open('data_all', 'w')
		self.results_file = open('results.stage2', 'w')
		self.s2agr_file = open('grace/S2.stage2.agr', 'w')
		self.s2fagr_file = open('grace/S2f.stage2.agr', 'w')
		self.s2sagr_file = open('grace/S2s.stage2.agr', 'w')
		self.teagr_file = open('grace/te.stage2.agr', 'w')
		self.rexagr_file = open('grace/Rex.stage2.agr', 'w')
		self.sseagr_file = open('grace/SSE.stage2.agr', 'w')


	def model_selection_extended(self):
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
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))
			self.mf.data.results.append({})

			# Model 1 test.
			if data['m1'][res]['sse_test'] == 1:
				self.mf.log.write('%-12s' % '[Model 1]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')
				#self.mf.data.results[res]['model'] = '1'

			# Test if both model 2 and 3 fit!!! (Should not occur)
			elif data['m2'][res]['sse_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1 \
				and data['m3'][res]['sse_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2 and 3]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='2+3')
				#self.mf.data.results[res]['model'] = '2+3'

			# Model 2 test.
			elif data['m2'][res]['sse_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2]')
				self.mf.data.results[res] = self.fill_results(data['m2'][res], model='2')
				#self.mf.data.results[res]['model'] = '2'

			# Model 3 test.
			elif data['m3'][res]['sse_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 3]')
				self.mf.data.results[res] = self.fill_results(data['m3'][res], model='3')
				#self.mf.data.results[res]['model'] = '3'

			# Large SSE test for model 1.
			elif data['m1'][res]['large_sse'] == 0:
				self.mf.log.write('%-12s' % '[Model 1*]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')
				#self.mf.data.results[res]['model'] = '1*'

			# Test if both model 4 and 5 fit!!! (Should not occur)
			elif data['m4'][res]['sse_test'] == 1 and ( data['f-m2m4'][res]['ftest'] == 1 or data['f-m3m4'][res]['ftest'] == 1 ) \
				and data['m5'][res]['sse_test'] == 1 and data['f-m2m5'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 4 and 5]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='4+5')
				#self.mf.data.results[res]['model'] = '4+5'
				
			# Model 4 test.
			elif data['m4'][res]['sse_test'] == 1 and ( data['f-m2m4'][res]['ftest'] == 1 or data['f-m3m4'][res]['ftest'] == 1 ):
				self.mf.log.write('%-12s' % '[Model 4]')
				self.mf.data.results[res] = self.fill_results(data['m4'][res], model='4')
				#self.mf.data.results[res]['model'] = '4'
				
			# Model 5 test.
			elif data['m5'][res]['sse_test'] == 1 and data['f-m2m5'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 5]')
				self.mf.data.results[res] = self.fill_results(data['m5'][res], model='5')
				#self.mf.data.results[res]['model'] = '5'

			# No model fits!
			else:
				self.mf.log.write('%-12s' % '[Model 0]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='0')
				#self.mf.data.results[res]['model'] = '0'


	def print_data(self):
		"Print the results into the results file."

		text = ''
		for res in range(len(self.mf.data.results)):
			text = text + "<<< Residue " + self.mf.data.results[res]['res_num']
			text = text + ", Model " + self.mf.data.results[res]['model'] + " >>>\n"
			text = text + '%-10s' % ''
			text = text + '%-8s%-8s%-8s%-8s' % ( 'S2', 'S2_err', 'S2f', 'S2f_err' )
			text = text + '%-10s%-10s%-8s%-8s' % ( 'te', 'te_err', 'Rex', 'Rex_err' )
			text = text + '%-10s%-10s%-10s' % ( 'SSE', 'SSElim', 'SSEtest' )
			text = text + '%-10s%-10s\n' % ( 'LargeSSE', 'ZeroSSE' )
			for run in self.mf.data.runs:
				if match('^m', run):
					text = text + '%-10s' % run
					text = text + '%-8s' % self.mf.data.data[run][res]['s2']
					text = text + '%-8s' % self.mf.data.data[run][res]['s2_err']
					text = text + '%-8s' % self.mf.data.data[run][res]['s2f']
					text = text + '%-8s' % self.mf.data.data[run][res]['s2f_err']
					text = text + '%-10s' % self.mf.data.data[run][res]['te']
					text = text + '%-10s' % self.mf.data.data[run][res]['te_err']
					text = text + '%-8s' % self.mf.data.data[run][res]['rex']
					text = text + '%-8s' % self.mf.data.data[run][res]['rex_err']
					text = text + '%-10s' % self.mf.data.data[run][res]['sse']
					text = text + '%-10s' % self.mf.data.data[run][res]['sse_lim']
					text = text + '%-10s' % self.mf.data.data[run][res]['sse_test']
					text = text + '%-10s' % self.mf.data.data[run][res]['large_sse']
					text = text + '%-10s\n' % self.mf.data.data[run][res]['zero_sse']
		self.data_file.write(text)



	def print_results(self):
		"Print the results into the results file."
		
		text = '%-6s%-6s%-13s%-13s%-19s' % ( 'ResNo', 'Model', '    S2', '    S2f', '       te' )
		text = text + '%-13s%-10s\n' % ( '    Rex', '    SSE' )
		for res in range(len(self.mf.data.results)):
			text = text + '%-6s' % self.mf.data.results[res]['res_num']
			text = text + '%-6s' % self.mf.data.results[res]['model']
			text = text + '%5s%1s%-5s  ' % ( self.mf.data.results[res]['s2'], '±', self.mf.data.results[res]['s2_err'] )
			text = text + '%5s%1s%-5s  ' % ( self.mf.data.results[res]['s2f'], '±', self.mf.data.results[res]['s2f_err'] )
			text = text + '%5s%1s%-5s  ' % ( self.mf.data.results[res]['s2s'], '±', self.mf.data.results[res]['s2s_err'] )
			text = text + '%8s%1s%-8s  ' % ( self.mf.data.results[res]['te'], '±', self.mf.data.results[res]['te_err'] )
			text = text + '%5s%1s%-5s  ' % ( self.mf.data.results[res]['rex'], '±', self.mf.data.results[res]['rex_err'] )
			text = text + '%10s\n' % self.mf.data.results[res]['sse']
		self.results_file.write(text)


	def read_file(self, file_name):
		"Attempt to read the file, or quit the script if it does not exist."

		try:
			open(file_name, 'r')
		except IOError:
			print "The file '" + file_name + "' does not exist, quitting script.\n\n"
			sys.exit()
		file = open(file_name, 'r')
		return file


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
			self.mkdir(run)
			self.open_files(run)
			self.set_run_flags(run)
			self.log_params('M1', self.mf.data.usr_param.md1)
			self.log_params('M2', self.mf.data.usr_param.md2)
			if match('^m', run):
				self.create_mfin(run)
			elif match('^f', run):
				self.create_mfin(run, sel='ftest')
			self.create_run(run)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
				self.create_mfmodel(self.mf.data.usr_param.md1, type='M1', header=text)
				if match('^f', run):
					self.create_mfmodel(self.mf.data.usr_param.md2, type='M1', header='\n')
				# Mfpar.
				self.create_mfpar(res)
			self.close_files(run)
		print "\n[ End of Stage 1 ]\n\n"


	def stage2(self):
		self.mkdir('optimize')
		self.mkdir('grace')
		self.init_stage2_files()
		print "\n[ Modelfree Data Extraction ]\n"
		for run in self.mf.data.runs:
			file_name = run + '/mfout'
			mfout = self.read_file(file_name)
			mfout_lines = mfout.readlines()
			mfout.close()
			print "Extracting modelfree data from " + run + "/mfout."
			num_res = len(self.mf.data.relax_data[0])
			if match('^m', run):
				self.mf.data.data[run] = self.mf.star.extract(mfout_lines, num_res, self.mf.data.usr_param.sse_lim, self.mf.data.usr_param.ftest_lim, float(self.mf.data.usr_param.large_sse), ftest='n')
			if match('^f', run):
				self.mf.data.data[run] = self.mf.star.extract(mfout_lines, num_res, self.mf.data.usr_param.sse_lim, self.mf.data.usr_param.ftest_lim, float(self.mf.data.usr_param.large_sse), ftest='y')

		print "\n[ Model Selection ]\n"
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
		self.print_results()
		print "\n[ Placing Data Structures into \"data_all\" ]\n"
		self.print_data()
		print "\n[ Grace File Creation ]\n"
		subtitle = "After model selection, unoptimized"
		self.grace(self.s2agr_file, 'S2', subtitle)
		self.grace(self.s2fagr_file, 'S2f', subtitle)
		self.grace(self.s2sagr_file, 'S2s', subtitle)
		self.grace(self.teagr_file, 'te', subtitle)
		self.grace(self.rexagr_file, 'Rex', subtitle)
		self.grace(self.sseagr_file, 'SSE', subtitle)




		print "Stage 2 incomplete.\n\n"
		sys.exit()

			# Final optimization.
#			self.open_files('optimize')
#			if match('isotropic', self.mf.data.usr_param.diff):
#				self.create_mfin(run, algorithm='brent', diffusion_search='grid')
#			elif match('axial', self.mf.data.usr_param.diff):
#				self.create_mfin(run, algorithm='powell')
#
#			for res in range(len(self.mf.data.relax_data[0])):
#				if match('0', self.mf.data.results[res]{model}):
#					self.opt_model = 'none'
#				elif match('2+3', self.mf.data.results[res]{model}):
#					self.opt_model = 'none'
#				elif match('4+5', self.mf.data.results[res]{model}):
#					self.opt_model = 'none'
#				elif match('^1', results[res]{model}):
#					self.opt_model = "m1"
#				else:
#					self.opt_model = 'm' + results[res]{model}
#
#				self.set_run_flags(self.opt_model)
#				# Mfdata.
#				if match('none', self.opt_model):
#					self.create_mfdata(res, flag='0')
#				else:
#					self.create_mfdata(res, flag='1')
#				# Mfmodel.
#				text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
#				self.create_mfmodel(type='M1', self.mf.data.usr_param.md1, header=text)
#				# Mfpar.
#				self.create_mfpar(res)


	def stage3(self):
		print "Stage 3 not implemented yet.\n"
		sys.exit()
