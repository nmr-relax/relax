from os import system
from re import match
from string import split
import sys


class common_operations:
	def __init__(self):
		"Operations, functions, etc common to the different model-free analysis methods."


	def ask_stage(self):
		"User input of stage number."

		print "\n[ Select the stage for model-free analysis ]\n"
		print "The stages are:"
		print "   Stage 1 (1):  Creation of the files for the model-free calculations for models 1 to 5."
		print "   Stage 2 (2):  Model selection and creation of a final run."
		print "   Stage 3 (3):  Extraction of the data."

		while 1:
			input = raw_input('> ')
			valid_stages = ['1', '2', '3']
			if input in valid_stages:
				stage = input
				break
			else:
				print "Invalid stage number.  Choose either 1, 2, or 3."
		if match('2', stage):
			while 1:
				print "Stage 2 has the following two options for the final run:"
				print "   (a):   No optimization of the diffusion tensor."
				print "   (b):   Optimization of the diffusion tensor."
				input = raw_input('> ')
				valid_stages = ['a', 'b']
				if input in valid_stages:
					stage = stage + input
					break
				else:
					print "Invalid option, choose either a or b."

		print "The stage chosen is " + stage + "\n"
		return stage


	def create_mfdata(self, res, exclude_set=-1, flag='1'):
		"""Create the Modelfree input file mfdata.

		This function is run once for each residue.  If the flag variable is set to 0, all data
		for this residue will be excluded.  If the exclude_set variable is given, the data flag
		corresponding to that set will be set to 0 (Used by the cross-validation method).
		"""

		mfdata = self.mf.mfdata

		mfdata.write("\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n")
		k = 0
		for i in range(len(self.mf.data.nmr_frq)):
			for j in range(3):
				if match('1', self.mf.data.nmr_frq[i][j+2]):
					mfdata.write('%-7s' % self.mf.data.input_info[k][0])
					mfdata.write('%-10s' % self.mf.data.input_info[k][1])
					mfdata.write('%10s' % self.mf.data.relax_data[k][res][2])
					mfdata.write('%10s' % self.mf.data.relax_data[k][res][3])
					if exclude_set == k:
						mfdata.write(' %-3s\n' % 0)
					else:
						mfdata.write(' %-3s\n' % flag)
					k = k + 1
				else:
					if j == 0:
						mfdata.write('%-7s' % 'R1')
					if j == 1:
						mfdata.write('%-7s' % 'R2')
					if j == 2:
						mfdata.write('%-7s' % 'NOE')
					mfdata.write('%-10s' % self.mf.data.nmr_frq[i][0])
					mfdata.write('%10s' % '0.000')
					mfdata.write('%10s' % '0.000')
					mfdata.write(' %-3s\n' % '0')


	def create_mfin(self):
		"Create the Modelfree input file mfin"

		mfin = self.mf.mfin

		mfin.write("optimization    tval\n\n")
		mfin.write("seed            0\n\n")
		mfin.write("search          grid\n\n")
		mfin.write("diffusion       " + self.mf.data.mfin.diff + " " + self.mf.data.mfin.diff_search + "\n\n")
		mfin.write("algorithm       " + self.mf.data.mfin.algorithm + "\n\n")
		if match('y', self.mf.data.mfin.sims):
			mfin.write("simulations     " + self.mf.data.mfin.sim_type + "    " + self.mf.data.mfin.num_sim)
			mfin.write("       " + self.mf.data.mfin.trim + "\n\n")
		elif match('n', self.mf.data.mfin.sims):
			mfin.write("simulations     none\n\n")
		mfin.write("selection       " + self.mf.data.mfin.selection + "\n\n")
		mfin.write("sim_algorithm   " + self.mf.data.mfin.algorithm + "\n\n")
		mfin.write("fields          " + self.mf.data.mfin.num_fields)
		for frq in range(len(self.mf.data.nmr_frq)):
			mfin.write("  " + self.mf.data.nmr_frq[frq][0])
		mfin.write("\n")
		# tm.
		mfin.write('%-7s' % 'tm')
		mfin.write('%14s' % self.mf.data.usr_param.tm['val'])
		mfin.write('%2s' % self.mf.data.usr_param.tm['flag'])
		mfin.write('%3s' % self.mf.data.usr_param.tm['bound'])
		mfin.write('%5s' % self.mf.data.usr_param.tm['lower'])
		mfin.write('%6s' % self.mf.data.usr_param.tm['upper'])
		mfin.write('%4s\n' % self.mf.data.usr_param.tm['steps'])
		# dratio.
		mfin.write('%-7s' % 'Dratio')
		mfin.write('%14s' % self.mf.data.usr_param.dratio['val'])
		mfin.write('%2s' % self.mf.data.usr_param.dratio['flag'])
		mfin.write('%3s' % self.mf.data.usr_param.dratio['bound'])
		mfin.write('%5s' % self.mf.data.usr_param.dratio['lower'])
		mfin.write('%6s' % self.mf.data.usr_param.dratio['upper'])
		mfin.write('%4s\n' % self.mf.data.usr_param.dratio['steps'])
		# theta.
		mfin.write('%-7s' % 'Theta')
		mfin.write('%14s' % self.mf.data.usr_param.theta['val'])
		mfin.write('%2s' % self.mf.data.usr_param.theta['flag'])
		mfin.write('%3s' % self.mf.data.usr_param.theta['bound'])
		mfin.write('%5s' % self.mf.data.usr_param.theta['lower'])
		mfin.write('%6s' % self.mf.data.usr_param.theta['upper'])
		mfin.write('%4s\n' % self.mf.data.usr_param.theta['steps'])
		# phi.
		mfin.write('%-7s' % 'Phi')
		mfin.write('%14s' % self.mf.data.usr_param.phi['val'])
		mfin.write('%2s' % self.mf.data.usr_param.phi['flag'])
		mfin.write('%3s' % self.mf.data.usr_param.phi['bound'])
		mfin.write('%5s' % self.mf.data.usr_param.phi['lower'])
		mfin.write('%6s' % self.mf.data.usr_param.phi['upper'])
		mfin.write('%4s\n' % self.mf.data.usr_param.phi['steps'])


	def create_mfmodel(self, res, md, type='M1'):
		"Create the M1 or M2 section of the Modelfree input file mfmodel"

		mfmodel = self.mf.mfmodel

		if match('M1', type):
			mfmodel.write("\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n")
		else:
			mfmodel.write("\n")

		# tloc.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'tloc')
		mfmodel.write('%-6s' % md['tloc']['start'])
		mfmodel.write('%-4s' % md['tloc']['flag'])
		mfmodel.write('%-2s' % md['tloc']['bound'])
		mfmodel.write('%11s' % md['tloc']['lower'])
		mfmodel.write('%12s' % md['tloc']['upper'])
		mfmodel.write(' %-4s\n' % md['tloc']['steps'])
		# Theta.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'Theta')
		mfmodel.write('%-6s' % md['theta']['start'])
		mfmodel.write('%-4s' % md['theta']['flag'])
		mfmodel.write('%-2s' % md['theta']['bound'])
		mfmodel.write('%11s' % md['theta']['lower'])
		mfmodel.write('%12s' % md['theta']['upper'])
		mfmodel.write(' %-4s\n' % md['theta']['steps'])
		# S2f.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'Sf2')
		mfmodel.write('%-6s' % md['sf2']['start'])
		mfmodel.write('%-4s' % md['sf2']['flag'])
		mfmodel.write('%-2s' % md['sf2']['bound'])
		mfmodel.write('%11s' % md['sf2']['lower'])
		mfmodel.write('%12s' % md['sf2']['upper'])
		mfmodel.write(' %-4s\n' % md['sf2']['steps'])
		# S2s.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'Ss2')
		mfmodel.write('%-6s' % md['ss2']['start'])
		mfmodel.write('%-4s' % md['ss2']['flag'])
		mfmodel.write('%-2s' % md['ss2']['bound'])
		mfmodel.write('%11s' % md['ss2']['lower'])
		mfmodel.write('%12s' % md['ss2']['upper'])
		mfmodel.write(' %-4s\n' % md['ss2']['steps'])
		# te.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'te')
		mfmodel.write('%-6s' % md['te']['start'])
		mfmodel.write('%-4s' % md['te']['flag'])
		mfmodel.write('%-2s' % md['te']['bound'])
		mfmodel.write('%11s' % md['te']['lower'])
		mfmodel.write('%12s' % md['te']['upper'])
		mfmodel.write(' %-4s\n' % md['te']['steps'])
		# Rex.
		mfmodel.write('%-3s' % type)
		mfmodel.write('%-6s' % 'Rex')
		mfmodel.write('%-6s' % md['rex']['start'])
		mfmodel.write('%-4s' % md['rex']['flag'])
		mfmodel.write('%-2s' % md['rex']['bound'])
		mfmodel.write('%11s' % md['rex']['lower'])
		mfmodel.write('%12s' % md['rex']['upper'])
		mfmodel.write(' %-4s\n' % md['rex']['steps'])


	def create_mfpar(self, res):
		"Create the Modelfree input file mfpar"

		mfpar = self.mf.mfpar

		mfpar.write("\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n")

		mfpar.write('%-14s' % "constants")
		mfpar.write('%-6s' % self.mf.data.relax_data[0][res][0])
		mfpar.write('%-7s' % self.mf.data.usr_param.const['nucleus'])
		mfpar.write('%-8s' % self.mf.data.usr_param.const['gamma'])
		mfpar.write('%-8s' % self.mf.data.usr_param.const['rxh'])
		mfpar.write('%-8s\n' % self.mf.data.usr_param.const['csa'])

		mfpar.write('%-10s' % "vector")
		mfpar.write('%-4s' % self.mf.data.usr_param.vector['atom1'])
		mfpar.write('%-4s\n' % self.mf.data.usr_param.vector['atom2'])


	def create_run(self, dir):
		"Create the file 'run' to execute the model-free run"

		self.mf.run.write("modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out")
		if self.mf.data.usr_param.diff == 'axial':
			# Copy the pdb file to the model directory so there are no problems with the *.rotate
			# file already existing.
			cmd = 'cp ' + self.mf.data.usr_param.pdb_full + ' ' + dir
			system(cmd)
			self.mf.run.write(" -s " + self.mf.data.usr_param.pdb_file)
		self.mf.run.write("\n")


	def extract_mf_data(self):
		"Extract the model-free results."

		for model in self.mf.data.runs:
			mfout = self.mf.file_ops.read_file(model + '/mfout')
			mfout_lines = mfout.readlines()
			mfout.close()
			print "Extracting model-free data from " + model + "/mfout."
			num_res = len(self.mf.data.relax_data[0])
			if match('^m', model):
				self.mf.data.data[model] = self.mf.star.extract(mfout_lines, num_res, self.mf.data.usr_param.chi2_lim, self.mf.data.usr_param.ftest_lim, ftest='n')
			if match('^f', model):
				self.mf.data.data[model] = self.mf.star.extract(mfout_lines, num_res, self.mf.data.usr_param.chi2_lim, self.mf.data.usr_param.ftest_lim, ftest='y')


	def extract_relax_data(self):
		"Extract the relaxation data from the files given in the file 'input'"
		print "\n[ Relaxation data extraction ]\n"
		for i in range(len(self.mf.data.input_info)):
			data = self.mf.file_ops.relax_data(self.mf.data.input_info[i][3])
			self.mf.data.relax_data[i] = data


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
			results['chi2']     = data['chi2']
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
			results['chi2']     = data['chi2']
		return results


	def final_run(self):
		"Creation of the final run.  Files are placed in the directory 'final'."

		self.mf.file_ops.mkdir('final')
		self.mf.file_ops.open_mf_files(dir='final')
		self.create_mfin()

		self.create_run(dir='final')
		for res in range(len(self.mf.data.relax_data[0])):
			if match('0', self.mf.data.results[res]['model']):
				model = 'none'
			elif match('2+3', self.mf.data.results[res]['model']):
				model = 'none'
			elif match('4+5', self.mf.data.results[res]['model']):
				model = 'none'
			elif match('^1', self.mf.data.results[res]['model']):
				model = "m1"
			else:
				model = 'm' + self.mf.data.results[res]['model']
			self.set_run_flags(model)
			# Mfdata.
			if match('none', model):
				self.create_mfdata(res, flag='0')
			else:
				self.create_mfdata(res, flag='1')
			# Mfmodel.
			self.create_mfmodel(res, self.mf.data.usr_param.md1, type='M1')
			# Mfpar.
			self.create_mfpar(res)
		self.mf.file_ops.close_mf_files(dir='final')


	def goto_stage(self):
		if match('1', self.mf.data.stage):
			print "\n[ Stage 1 ]\n"
			self.set_vars_stage_initial()
			self.stage_initial()
			print "\n[ End of stage 1 ]\n\n"

		if match('^2', self.mf.data.stage):
			print "\n[ Stage 2 ]\n"
			self.set_vars_stage_selection()
			self.stage_selection()
			if match('2a', self.mf.data.stage):
				self.final_run()
			if match('2b', self.mf.data.stage):
				if match('isotropic', self.mf.data.mfin.diff):
					self.mf.data.mfin.algorithm = 'brent'
					self.mf.data.mfin.diff_search = 'grid'
				elif match('axial', self.mf.data.mfin.diff):
					self.mf.data.mfin.algorithm = 'powell'
				self.final_run()
			print "\n[ End of stage 2 ]\n\n"

		if match('3', self.mf.data.stage):
			print "\n[ Stage 3 ]\n"
			self.stage_final()
			print "\n[ End of stage 3 ]\n\n"


	def grace(self, file_name, type, subtitle):
		"Create grace files for the results."

		file = open(file_name, 'w')

		if match('Chi2', type):
			file.write(self.grace_header(type + ' values', subtitle, 'Residue Number', type, 'xy'))
		else:
			file.write(self.grace_header(type + ' values', subtitle, 'Residue Number', type, 'xydy'))

		for res in range(len(self.mf.data.results)):
			if match('S2', type) and self.mf.data.results[res]['s2']:
				file.write(self.mf.data.results[res]['res_num'] + " ")
				file.write(`self.mf.data.results[res]['s2']` + " ")
				file.write(`self.mf.data.results[res]['s2_err']` + "\n")
			elif match('S2s', type) and self.mf.data.results[res]['s2s']:
				file.write(self.mf.data.results[res]['res_num'] + " ")
				file.write(`self.mf.data.results[res]['s2s']` + " ")
				file.write(`self.mf.data.results[res]['s2s_err']` + "\n")
			elif match('S2f', type) and self.mf.data.results[res]['s2f']:
				file.write(self.mf.data.results[res]['res_num'] + " ")
				file.write(`self.mf.data.results[res]['s2f']` + " ")
				file.write(`self.mf.data.results[res]['s2f_err']` + "\n")
			elif match('te', type) and self.mf.data.results[res]['te']:
				file.write(self.mf.data.results[res]['res_num'] + " ")
				file.write(`self.mf.data.results[res]['te']` + " ")
				file.write(`self.mf.data.results[res]['te_err']` + "\n")
			elif match('Rex', type) and self.mf.data.results[res]['rex']:
				file.write(self.mf.data.results[res]['res_num'] + " ")
				file.write(`self.mf.data.results[res]['rex']` + " ")
				file.write(`self.mf.data.results[res]['rex_err']` + "\n")
			elif match('Chi2', type) and self.mf.data.results[res]['chi2']:
				file.write(self.mf.data.results[res]['res_num'] + " ")
				file.write(`self.mf.data.results[res]['chi2']` + "\n")
		file.write("&\n")
		file.close()


	def grace_header(self, title, subtitle, x, y, type):
		"Create and return a grace header."

		text = "@version 50100\n"
		text = text + "@with g0\n"
		if match('Residue Number', x):
			text = text + "@    world xmax 165\n"
		if match('R1', x) and match('Chi2', y):
			text = text + "@    world xmin 0.8\n"
			text = text + "@    world xmax 2\n"
			text = text + "@    world ymin 0\n"
			text = text + "@    world ymax 2000\n"
		if match('R2', x) and match('Chi2', y):
			text = text + "@    world xmin 5\n"
			text = text + "@    world xmax 45\n"
			text = text + "@    world ymin 0\n"
			text = text + "@    world ymax 2000\n"
		if match('NOE', x) and match('Chi2', y):
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
		if match('R1', x) and match('Chi2', y):
			text = text + "@    xaxis  tick major 0.2\n"
		if match('R2', x) and match('Chi2', y):
			text = text + "@    xaxis  tick major 5\n"
		if match('NOE', x) and match('Chi2', y):
			text = text + "@    xaxis  tick major 0.1\n"
		text = text + "@    xaxis  tick major size 0.480000\n"
		text = text + "@    xaxis  tick major linewidth 0.5\n"
		text = text + "@    xaxis  tick minor linewidth 0.5\n"
		text = text + "@    xaxis  tick minor size 0.240000\n"
		text = text + "@    xaxis  ticklabel char size 0.790000\n"
		text = text + "@    yaxis  label \"" + y + "\"\n"
		if match('R1', x) and match('Chi2', y):
			text = text + "@    yaxis  tick major 200\n"
		if match('R2', x) and match('Chi2', y):
			text = text + "@    yaxis  tick major 200\n"
		if match('NOE', x) and match('Chi2', y):
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


	def initialize(self):
		"A few operations to start up the program."

		self.mf.data.stage = self.ask_stage()
		title = "<<< Stage " + self.mf.data.stage + " - " 
		title = title + self.mf.data.usr_param.method + " model selection >>>\n\n\n"

		if self.mf.debug == 1:
			self.mf.file_ops.init_log_file(title)

		self.update_data(input)
		self.extract_relax_data()

		if self.mf.debug == 1:
			self.log_input_info()


	def log_input_info(self):
		for i in range(len(self.mf.data.input_info)):
			self.mf.log.write('%-25s%-20s\n' % ("Data label:", self.mf.data.input_info[i][0]))
			self.mf.log.write('%-25s%-20s\n' % ("NMR frequency label:", self.mf.data.input_info[i][1]))
			self.mf.log.write('%-25s%-20s\n' % ("NMR proton frequency:", `self.mf.data.input_info[i][2]`))
			self.mf.log.write('%-25s%-20s\n\n' % ("File name:", self.mf.data.input_info[i][3]))
		self.mf.log.write("Number of frequencies:\t" + `self.mf.data.num_frq` + "\n")
		self.mf.log.write("Number of data sets:\t" + `self.mf.data.num_data_sets` + "\n\n")


	def log_params(self, name, mdx):
		"Put the parameter data structures into the log file."

		self.mf.log.write("\n" + name + " data structure\n")
		for param in ['tloc', 'theta', 'ss2', 'sf2', 'te', 'rex']:
			self.mf.log.write('%-10s' % ( param + ":" ))
			self.mf.log.write('%-15s' % ( "start = " + mdx[param]['start'] ))
			self.mf.log.write('%-11s' % ( "flag = " + mdx[param]['flag'] ))
			self.mf.log.write('%-13s' % ( "bound = " + mdx[param]['bound'] ))
			self.mf.log.write('%-20s' % ( "lower = " + mdx[param]['lower'] ))
			self.mf.log.write('%-20s' % ( "upper = " + mdx[param]['upper'] ))
			self.mf.log.write('%-10s\n' % ( "steps = " + mdx[param]['steps'] ))


	def print_results(self):
		"Print the results into the results file."

		file = open('results', 'w')

		file.write('%-6s%-6s%-13s%-13s%-13s' % ( 'ResNo', 'Model', '    S2', '    S2f', '    S2s' ))
		file.write('%-19s%-13s%-10s\n' % ( '       te', '    Rex', '    Chi2' ))
		sys.stdout.write("[")
		for res in range(len(self.mf.data.results)):
			sys.stdout.write("-")
			file.write('%-6s' % self.mf.data.results[res]['res_num'])
			file.write('%-6s' % self.mf.data.results[res]['model'])

			if self.mf.data.results[res]['model'] in ["1", "2", "3", "4", "5"]:
				file.write('%5.3f%1s%-5.3f  ' % ( self.mf.data.results[res]['s2'], '±', self.mf.data.results[res]['s2_err'] ))
			else:
				file.write('%13s' % '')
			if self.mf.data.results[res]['model'] in ["5"]:
				file.write('%5.3f%1s%-5.3f  ' % ( self.mf.data.results[res]['s2f'], '±', self.mf.data.results[res]['s2f_err'] ))
				file.write('%5.3f%1s%-5.3f  ' % ( self.mf.data.results[res]['s2s'], '±', self.mf.data.results[res]['s2s_err'] ))
			else:
				file.write('%26s' % '')
			if self.mf.data.results[res]['model'] in ["2", "4", "5"]:
				file.write('%8.2f%1s%-8.2f  ' % ( self.mf.data.results[res]['te'], '±', self.mf.data.results[res]['te_err'] ))
			else:
				file.write('%19s' % '')
			if self.mf.data.results[res]['model'] in ["3", "4"]:
				file.write('%5.3f%1s%-5.3f  ' % ( self.mf.data.results[res]['rex'], '±', self.mf.data.results[res]['rex_err'] ))
			else:
				file.write('%13s' % '')
			file.write('%10.3f\n' % self.mf.data.results[res]['chi2'])
		sys.stdout.write("]\n")

		file.close()


	def set_run_flags(self, model):
		"Reset, and then set the flags in self.mf.data.usr_param.md1 and md2."

		self.mf.data.usr_param.md1['sf2']['flag'] = '0'
		self.mf.data.usr_param.md1['ss2']['flag'] = '0'
		self.mf.data.usr_param.md1['te']['flag']  = '0'
		self.mf.data.usr_param.md1['rex']['flag'] = '0'

		self.mf.data.usr_param.md2['sf2']['flag'] = '0'
		self.mf.data.usr_param.md2['ss2']['flag'] = '0'
		self.mf.data.usr_param.md2['te']['flag']  = '0'
		self.mf.data.usr_param.md2['rex']['flag'] = '0'

		# Normal runs.
		if model == "m1":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
		if model == "m2":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['te']['flag']  = '1'
		if model == "m3":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['rex']['flag'] = '1'
		if model == "m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['te']['flag']  = '1'
			self.mf.data.usr_param.md1['rex']['flag'] = '1'
		if model == "m5":
			self.mf.data.usr_param.md1['sf2']['flag'] = '1'
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['te']['flag']  = '1'

		# F-tests.
		if model == "f-m1m2":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
		if model == "f-m1m3":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['rex']['flag'] = '1'
		if model == "f-m1m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
			self.mf.data.usr_param.md2['rex']['flag'] = '1'
		if model == "f-m1m5":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['sf2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
		if model == "f-m2m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['te']['flag']  = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
			self.mf.data.usr_param.md2['rex']['flag'] = '1'
		if model == "f-m2m5":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['te']['flag']  = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['sf2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
		if model == "f-m3m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['rex']['flag'] = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
			self.mf.data.usr_param.md2['rex']['flag'] = '1'


	def stage_initial(self):
		"Creation of the files for the Modelfree calculations for the models in self.mf.data.runs."

		for model in self.mf.data.runs:
			if match('^m', model):
				print "Creating input files for model " + model
				if self.mf.debug == 1:
					self.mf.log.write("\n\n<<< Model " + model + " >>>\n\n")
			elif match('^f', model):
				print "Creating input files for the F-test " + model
				if self.mf.debug == 1:
					self.mf.log.write("\n\n<<< F-test " + model + " >>>\n\n")
			else:
				print "The run '" + model + "'does not start with an m or f, quitting script!\n\n"
				sys.exit()
			self.mf.file_ops.mkdir(dir=model)
			self.mf.file_ops.open_mf_files(dir=model)
			self.set_run_flags(model)

			if self.mf.debug == 1:
				self.log_params('M1', self.mf.data.usr_param.md1)
				self.log_params('M2', self.mf.data.usr_param.md2)

			if match('^m', model):
				self.mf.data.mfin.selection = 'none'
				self.create_mfin()
			elif match('^f', model):
				self.mf.data.mfin.selection = 'ftest'
				self.create_mfin()
			self.create_run(dir=model)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				self.create_mfmodel(res, self.mf.data.usr_param.md1, type='M1')
				if match('^f', model):
					self.create_mfmodel(res, self.mf.data.usr_param.md2, type='M2')
				# Mfpar.
				self.create_mfpar(res)
			self.mf.file_ops.close_mf_files(dir=model)


	def stage_selection(self):
		"The stage for model selection common to all techniques."

		print "\n[ Model-free data extraction ]\n"
		self.extract_mf_data()

 		print "\n[ " + self.mf.data.usr_param.method + " model selection ]\n"
		self.model_selection()

		print "\n[ Printing results ]\n"
		self.print_results()

		print "\n[ Placing data structures into \"data_all\" ]\n"
		self.print_data()

		print "\n[ Grace file creation ]\n"
		self.mf.file_ops.mkdir('grace')
		self.grace('grace/S2.agr', 'S2', subtitle="After model selection, unoptimized")
		self.grace('grace/S2f.agr', 'S2f', subtitle="After model selection, unoptimized")
		self.grace('grace/S2s.agr', 'S2s', subtitle="After model selection, unoptimized")
		self.grace('grace/te.agr', 'te', subtitle="After model selection, unoptimized")
		self.grace('grace/Rex.agr', 'Rex', subtitle="After model selection, unoptimized")
		self.grace('grace/Chi2.agr', 'Chi2', subtitle="After model selection, unoptimized")


	def stage_final(self):
		print "Stage 3 not implemented yet.\n"
		sys.exit()


	def update_data(self, input):
		"Extract all the information from the input info."

		self.mf.data.input_info = self.mf.data.usr_param.input_info
		self.mf.data.nmr_frq = self.mf.data.usr_param.nmr_frq

		self.mf.data.num_data_sets = len(self.mf.data.input_info)
		self.mf.data.num_frq = len(self.mf.data.nmr_frq)

		for set in range(len(self.mf.data.input_info)):
			self.mf.data.relax_data.append([])


