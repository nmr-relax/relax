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
from os import chmod
from re import match
from shutil import copy

from common_ops import common_operations

class palmer(common_operations):
	def __init__(self, mf):
		"The modelfree analysis of Palmer."

		self.mf = mf

		self.print_subheader()
		self.mf.data.palmer.stage = self.ask_stage()
		self.init_log_file()

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
	

	class init_stage2_files:
		def __init__(self):
			"Class containing the stage 2 specific files."
			
			self.data = open('data', 'w')
			self.results = open('results.stage2', 'w')
			self.s2agr = open('grace/S2.stage2.agr', 'w')
			self.s2fagr = open('grace/S2f.stage2.agr', 'w')
			self.teagr = open('grace/te.stage2.agr', 'w')
			self.rexagr = open('grace/Rex.stage2.agr', 'w')
			self.sseagr = open('grace/SSE.stage2.agr', 'w')


	def stage1(self):
		"Section for running the stage 1 functions for Palmer's method."
			
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
			self.create_mfin(run)
			self.create_run(run)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
				self.mfmodel.write(text)
				self.create_mfmodel('M1', self.mf.data.usr_param.md1)
				if match('^f', run):
					self.mfmodel.write('\n')
					self.create_mfmodel('M2', self.mf.data.usr_param.md2)
				# Mfpar.
				self.create_mfpar(res)
			self.close_files(run)
		print "\n[ End of Stage 1 ]\n\n"


	def stage2(self):
		"Section for running the stage 2 functions for Palmer's method."
			
		self.mkdir('optimize')
		self.mkdir('grace')
		self.files2 = self.init_stage2_files()
		print "\n[ Modelfree Data Extraction ]\n"
		for model in self.mf.data.models:
			file_name = model + '/mfout'
			self.mfout = self.read_file(file_name)

	def stage3(self):
		"Section for running the stage 3 functions for Palmer's method."
			

	def ask_stage(self):
		"User input of stage number."

		print "\n[ Select the stage for Modelfree analysis ]\n"
		print "The stages are:"
		print "\tStage 1 (1):   Initial run of all models 1 to 5 and f-tests between them."
		print "\tStage 2 (2):   Model selection and creation of the final optimization run."
		print "\tStage 3 (3):   Extraction of optimized data."
		while 1:
			stage = raw_input("> ")
			valid_stages = ["1", "2", "3"]
			if stage in valid_stages:
				break
			else:
				print "Invalid stage number.  Choose either 1, 2, or 3."
		print "The stage chosen is " + stage + "\n"
		return stage

	def close_files(self, dir):
		"Close the mfin, mfdata, mfmodel, mfpar, and run files, and make the run file executable."

		run = dir + "/run"
		self.mfin.close()
		self.mfdata.close()
		self.mfmodel.close()
		self.mfpar.close()
		self.run.close()
		chmod(run, 0777)
		
	
	def create_mfdata(self, res):
		"Create the Modelfree input file mfdata"

		text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
		if match('2', self.mf.data.palmer.stage):
			if match('none', self.opt_model):
				flag = 0
			else:
				flag = 1
		else:
			flag = 1
		for i in range(len(self.mf.data.input_info)):
			text = text + '%-7s' % self.mf.data.input_info[i][0]
			text = text + '%-10s' % self.mf.data.input_info[i][1]
			text = text + '%10s' % self.mf.data.relax_data[i][res][2]
			text = text + '%10s' % self.mf.data.relax_data[i][res][3]
			text = text + ' %-3s\n' % flag
		self.mfdata.write(text)


	def create_mfin(self, model):
		"Create the Modelfree input file mfin"

		sel = 'none'
		if self.mf.data.palmer.stage == '1':
			algorithm = 'fix'
			diffusion_search = 'none'
			if match('^f', model):
				sel = 'ftest'
		elif self.mf.data.palmer.stage == '2':
			if self.mf.data.usr_param.diff == 'isotropic':
				algorithm = 'brent'
				diffusion_search = 'grid'
			elif self.mf.data.usr_param.diff == 'axial':
				algorithm = 'powell'
				diffusion_search = 'none'
		
		text = ""
		text = text + "optimization    tval\n\n"
		text = text + "seed            0\n\n"
		text = text + "search          grid\n\n"
		text = text + "diffusion       " + self.mf.data.usr_param.diff + " " + diffusion_search + "\n\n"
		text = text + "algorithm       " + algorithm + "\n\n"
		if match('1', self.mf.data.palmer.stage):
			text = text + "simulations     pred    " + self.mf.data.usr_param.no_sim
			text = text + "       " + self.mf.data.usr_param.trim + "\n\n"
		elif match('2', self.mf.data.palmer.stage):
			text = text + "simulations     none\n\n"
		text = text + "selection       " + sel + "\n\n"
		text = text + "sim_algorithm   " + algorithm + "\n\n"
		text = text + "fields          " + `len(self.mf.data.nmr_frq)`
		for frq in range(len(self.mf.data.nmr_frq)):
			text = text + "  " + self.mf.data.nmr_frq[frq][0]
		text = text + "\n"
		# tm.
		text = text + '%-7s' % 'tm'
		text = text + '%14s' % self.mf.data.usr_param.tm['val']
		text = text + '%2s' % self.mf.data.usr_param.tm['flag']
		text = text + '%3s' % self.mf.data.usr_param.tm['bound']
		text = text + '%5s' % self.mf.data.usr_param.tm['lower']
		text = text + '%6s' % self.mf.data.usr_param.tm['upper']
		text = text + '%4s\n' % self.mf.data.usr_param.tm['steps']
		# dratio.
		text = text + '%-7s' % 'Dratio'
		text = text + '%14s' % self.mf.data.usr_param.dratio['val']
		text = text + '%2s' % self.mf.data.usr_param.dratio['flag']
		text = text + '%3s' % self.mf.data.usr_param.dratio['bound']
		text = text + '%5s' % self.mf.data.usr_param.dratio['lower']
		text = text + '%6s' % self.mf.data.usr_param.dratio['upper']
		text = text + '%4s\n' % self.mf.data.usr_param.dratio['steps']
		# theta.
		text = text + '%-7s' % 'Theta'
		text = text + '%14s' % self.mf.data.usr_param.theta['val']
		text = text + '%2s' % self.mf.data.usr_param.theta['flag']
		text = text + '%3s' % self.mf.data.usr_param.theta['bound']
		text = text + '%5s' % self.mf.data.usr_param.theta['lower']
		text = text + '%6s' % self.mf.data.usr_param.theta['upper']
		text = text + '%4s\n' % self.mf.data.usr_param.theta['steps']
		# phi.
		text = text + '%-7s' % 'Phi'
		text = text + '%14s' % self.mf.data.usr_param.phi['val']
		text = text + '%2s' % self.mf.data.usr_param.phi['flag']
		text = text + '%3s' % self.mf.data.usr_param.phi['bound']
		text = text + '%5s' % self.mf.data.usr_param.phi['lower']
		text = text + '%6s' % self.mf.data.usr_param.phi['upper']
		text = text + '%4s\n' % self.mf.data.usr_param.phi['steps']
		
		self.mfin.write(text)


	def create_mfmodel(self, type, md):
		"Create the M1 or M2 section of the Modelfree input file mfmodel"

		text = ""
		# tloc.
		text = text + '%-3s' % type
		text = text + '%-6s' % 'tloc'
		text = text + '%-6s' % md['tloc']['start']
		text = text + '%-4s' % md['tloc']['flag']
		text = text + '%-2s' % md['tloc']['bound']
		text = text + '%11s' % md['tloc']['lower']
		text = text + '%12s' % md['tloc']['upper']
		text = text + ' %-4s\n' % md['tloc']['steps']
		# Theta.
		text = text + '%-3s' % type
		text = text + '%-6s' % 'Theta'
		text = text + '%-6s' % md['theta']['start']
		text = text + '%-4s' % md['theta']['flag']
		text = text + '%-2s' % md['theta']['bound']
		text = text + '%11s' % md['theta']['lower']
		text = text + '%12s' % md['theta']['upper']
		text = text + ' %-4s\n' % md['theta']['steps']
		# S2f.
		text = text + '%-3s' % type
		text = text + '%-6s' % 'Sf2'
		text = text + '%-6s' % md['sf2']['start']
		text = text + '%-4s' % md['sf2']['flag']
		text = text + '%-2s' % md['sf2']['bound']
		text = text + '%11s' % md['sf2']['lower']
		text = text + '%12s' % md['sf2']['upper']
		text = text + ' %-4s\n' % md['sf2']['steps']
		# S2s.
		text = text + '%-3s' % type
		text = text + '%-6s' % 'Ss2'
		text = text + '%-6s' % md['ss2']['start']
		text = text + '%-4s' % md['ss2']['flag']
		text = text + '%-2s' % md['ss2']['bound']
		text = text + '%11s' % md['ss2']['lower']
		text = text + '%12s' % md['ss2']['upper']
		text = text + ' %-4s\n' % md['ss2']['steps']
		# te.
		text = text + '%-3s' % type
		text = text + '%-6s' % 'te'
		text = text + '%-6s' % md['te']['start']
		text = text + '%-4s' % md['te']['flag']
		text = text + '%-2s' % md['te']['bound']
		text = text + '%11s' % md['te']['lower']
		text = text + '%12s' % md['te']['upper']
		text = text + ' %-4s\n' % md['te']['steps']
		# Rex.
		text = text + '%-3s' % type
		text = text + '%-6s' % 'Rex'
		text = text + '%-6s' % md['rex']['start']
		text = text + '%-4s' % md['rex']['flag']
		text = text + '%-2s' % md['rex']['bound']
		text = text + '%11s' % md['rex']['lower']
		text = text + '%12s' % md['rex']['upper']
		text = text + ' %-4s\n' % md['rex']['steps']

		self.mfmodel.write(text)


	def create_mfpar(self, res):
		"Create the Modelfree input file mfpar"

		text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"

		text = text + '%-14s' % "constants"
		text = text + '%-6s' % self.mf.data.relax_data[0][res][0]
		text = text + '%-7s' % self.mf.data.usr_param.const['nucleus']
		text = text + '%-8s' % self.mf.data.usr_param.const['gamma']
		text = text + '%-8s' % self.mf.data.usr_param.const['rxh']
		text = text + '%-8s\n' % self.mf.data.usr_param.const['csa']

		text = text + '%-10s' % "vector"
		text = text + '%-4s' % self.mf.data.usr_param.vector['atom1']
		text = text + '%-4s\n' % self.mf.data.usr_param.vector['atom2']

		self.mfpar.write(text)


	def create_run(self, dir):
		"Create the file 'run' to execute the modelfree run"

		text = "#! /bin/sh\n"
		text = text + "modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out"
		if self.mf.data.usr_param.diff == 'axial':
			# Copy the pdb file to the model directory so there are no problems with the *.rotate
			# file already existing.
			copy(self.mf.data.usr_param.pdb_full, dir)
			text = text + " -s " + self.mf.data.usr_param.pdb_file
		text = text + "\n"
		self.run.write(text)


	def init_log_file(self):
		"Initialize the log file."
		
		self.mf.log = open('log.stage' + self.mf.data.palmer.stage, 'w')
		text = "<<< Stage " + self.mf.data.palmer.stage + " of Palmer's method for Modelfree "
		text = text + "analysis >>>\n\n\n"
		self.mf.log.write(text)


	def log_params(self, name, mdx):
		"Put the parameter data structures into the log file."

		text = "\n" + name + " data structure\n"
		for param in ['tloc', 'theta', 'ss2', 'sf2', 'te', 'rex']:
			text = text + '%-10s' % ( param + ":" )
			text = text + '%-15s' % ( "start = " + mdx[param]['start'] )
			text = text + '%-11s' % ( "flag = " + mdx[param]['flag'] )
			text = text + '%-13s' % ( "bound = " + mdx[param]['bound'] )
			text = text + '%-20s' % ( "lower = " + mdx[param]['lower'] )
			text = text + '%-20s' % ( "upper = " + mdx[param]['upper'] )
			text = text + '%-10s\n' % ( "steps = " + mdx[param]['steps'] )
		self.mf.log.write(text)


	def open_files(self, dir):
		"Open the mfin, mfdata, mfmodel, mfpar, and run files for writing."

		self.mfin = open(dir + '/mfin', 'w')
		self.mfdata = open(dir + '/mfdata', 'w')
		self.mfmodel = open(dir + '/mfmodel', 'w')
		self.mfpar = open(dir + '/mfpar', 'w')
		self.run = open(dir + '/run', 'w')
	
	
	def print_subheader(self):
		"Print the sub-header for Palmer's method to screen."

		print "Palmer's method for modelfree analysis. (Mandel et al., 1995)"


	def read_file(self, file_name):
		"Attempt to read the file, or quit the script if it does not exist."

		try:
			open(file_name, 'r')
		except IOError:
			print "The file '" + file_name + "' does not exist, quitting script.\n\n"
			sys.exit()
		file = open(file_name, 'r')
		return file


	def set_run_flags(self, run):
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
		if run == "m1":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
		if run == "m2":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['te']['flag']  = '1'
		if run == "m3":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['rex']['flag'] = '1'
		if run == "m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['te']['flag']  = '1'
			self.mf.data.usr_param.md1['rex']['flag'] = '1'
		if run == "m5":
			self.mf.data.usr_param.md1['sf2']['flag'] = '1'
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['te']['flag']  = '1'

		# F-tests.
		if run == "f-m1m2":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
		if run == "f-m1m3":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['rex']['flag'] = '1'
		if run == "f-m1m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
			self.mf.data.usr_param.md2['rex']['flag'] = '1'
		if run == "f-m1m5":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['sf2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
		if run == "f-m2m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['te']['flag']  = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
			self.mf.data.usr_param.md2['rex']['flag'] = '1'
		if run == "f-m2m5":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['te']['flag']  = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['sf2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
		if run == "f-m3m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = '1'
			self.mf.data.usr_param.md1['rex']['flag'] = '1'
			self.mf.data.usr_param.md2['ss2']['flag'] = '1'
			self.mf.data.usr_param.md2['te']['flag']  = '1'
			self.mf.data.usr_param.md2['rex']['flag'] = '1'
	
	
