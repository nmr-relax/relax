import sys
from os import mkdir, chmod
from re import match
from shutil import copy

from stage_all import stage_all

class stage1(stage_all):
	def __init__(self, mf):
		"""The stage 1 class.

		Creation of the files for the modelfree calculations for models 1 to 5,
		and f-tests between them.
		"""

		self.mf = mf
		print "\n[ Stage 1 ]\n"
		for model in self.mf.data.models:
			print "Creating input files for model " + model
			self.mf.log.write("\n\n<<< Model " + model + " >>>\n\n")
			self.mkdir(model)
			self.open_files(model)
			self.set_model_flags(model)
			self.log_params()
			self.create_mfin(model)
			self.create_run(model)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
				self.mfmodel.write(text)
				self.create_mfmodel('M1', self.mf.data.usr_param.md1)
				# Mfpar.
				self.create_mfpar(res)
			self.close_files(model)

		for ftest in self.mf.data.ftests:
			print "Creating input files for the F-test " + ftest
			self.mf.log.write("\n\n<<< F-test " + ftest + " >>>\n\n")
			self.mkdir(ftest)
			self.open_files(ftest)
			self.set_ftest_flags(ftest)
			self.log_params()
			self.create_mfin(ftest)
			self.create_run(ftest)
			for res in range(len(self.mf.data.relax_data[0])):
				# Mfdata.
				self.create_mfdata(res)
				# Mfmodel.
				text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
				self.mfmodel.write(text)
				self.create_mfmodel('M1', self.mf.data.usr_param.md1)
				self.mfmodel.write('\n')
				self.create_mfmodel('M2', self.mf.data.usr_param.md2)
			self.close_files(ftest)
		print "\n[ End of Stage 1 ]\n\n"


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
		if match('2', self.mf.data.stage):
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
		if self.mf.data.stage == '1':
			algorithm = 'fix'
			diffusion_search = 'none'
			if match('^f', model):
				sel = 'ftest'
		elif self.mf.data.stage == '2':
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
		if self.mf.data.stage == 1:
			text = text + "simulations     pred    " + self.mf.data.usr_param.no_sim
			text = text + "       " + self.mf.data.usr_param.trim + "\n\n"
		elif self.mf.data.stage == 2:
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
			# Copy the pdb file to the model directory so there are no problems with the *.rotate file
			# already existing.
			copy(self.mf.data.usr_param.pdb_full, dir)
			text = text + " -s " + self.mf.data.usr_param.pdb_file
		text = text + "\n"
		self.run.write(text)


	def log_params(self):
		"Put the parameter data structures into the log file."

		self.mf.log.write("\nmd1 data structure\n")
		for param in ['tloc', 'theta', 'ss2', 'sf2', 'te', 'rex']:
			self.mf.log.write('%-10s' % ( param + ":" ))
			self.mf.log.write('%-15s' % ( "start = " + `self.mf.data.usr_param.md1[param]['start']`))
			self.mf.log.write('%-10s' % ( "flag = " + `self.mf.data.usr_param.md1[param]['flag']`))
			self.mf.log.write('%-12s' % ( "bound = " + `self.mf.data.usr_param.md1[param]['bound']`))
			self.mf.log.write('%-20s' % ( "lower = " + `self.mf.data.usr_param.md1[param]['lower']`))
			self.mf.log.write('%-20s' % ( "upper = " + `self.mf.data.usr_param.md1[param]['upper']`))
			self.mf.log.write('%-10s' % ( "steps = " + `self.mf.data.usr_param.md1[param]['steps']`))
			self.mf.log.write("\n")

		self.mf.log.write("\nmd2 data structure\n")
		for param in ['tloc', 'theta', 'ss2', 'sf2', 'te', 'rex']:
			self.mf.log.write('%-10s' % ( param + ":" ))
			self.mf.log.write('%-15s' % ( "start = " + `self.mf.data.usr_param.md2[param]['start']`))
			self.mf.log.write('%-10s' % ( "flag = " + `self.mf.data.usr_param.md2[param]['flag']`))
			self.mf.log.write('%-12s' % ( "bound = " + `self.mf.data.usr_param.md2[param]['bound']`))
			self.mf.log.write('%-20s' % ( "lower = " + `self.mf.data.usr_param.md2[param]['lower']`))
			self.mf.log.write('%-20s' % ( "upper = " + `self.mf.data.usr_param.md2[param]['upper']`))
			self.mf.log.write('%-10s' % ( "steps = " + `self.mf.data.usr_param.md2[param]['steps']`))
			self.mf.log.write("\n")


	def mkdir(self, dir):
		"Create the given directory, or exit if the directory exists."

		self.mf.log.write("Making directory " + dir + "\n")
		try:
			mkdir(dir)
		except OSError:
			print "Directory ./" + dir + " already exists, quitting script.\n"
			sys.exit()


	def open_files(self, dir):
		"Open the mfin, mfdata, mfmodel, mfpar, and run files for writing."

		mfin = dir + "/mfin"
		mfdata = dir + "/mfdata"
		mfmodel = dir + "/mfmodel"
		mfpar = dir + "/mfpar"
		run = dir + "/run"

		self.mfin = open(mfin, 'w')
		self.mfdata = open(mfdata, 'w')
		self.mfmodel = open(mfmodel, 'w')
		self.mfpar = open(mfpar, 'w')
		self.run = open(run, 'w')
	
	
	def set_ftest_flags(self, ftest):
		"Reset, and then set the flags in self.mf.data.usr_param.md1 and md2."
		
		self.mf.data.usr_param.md1['sf2']['flag'] = 0
		self.mf.data.usr_param.md1['ss2']['flag'] = 0
		self.mf.data.usr_param.md1['te']['flag']  = 0
		self.mf.data.usr_param.md1['rex']['flag'] = 0

		self.mf.data.usr_param.md2['sf2']['flag'] = 0
		self.mf.data.usr_param.md2['ss2']['flag'] = 0
		self.mf.data.usr_param.md2['te']['flag']  = 0
		self.mf.data.usr_param.md2['rex']['flag'] = 0

		if ftest == "f-m1m2":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
		if ftest == "f-m1m3":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['rex']['flag'] = 1
		if ftest == "f-m1m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
			self.mf.data.usr_param.md2['rex']['flag'] = 1
		if ftest == "f-m1m5":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['sf2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
		if ftest == "f-m2m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['te']['flag']  = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
			self.mf.data.usr_param.md2['rex']['flag'] = 1
		if ftest == "f-m2m5":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['te']['flag']  = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['sf2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
		if ftest == "f-m3m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['rex']['flag'] = 1
			self.mf.data.usr_param.md2['ss2']['flag'] = 1
			self.mf.data.usr_param.md2['te']['flag']  = 1
			self.mf.data.usr_param.md2['rex']['flag'] = 1
	
	
	def set_model_flags(self, model):
		"Reset, and then set the flags in self.mf.data.usr_param.md1"
		
		self.mf.data.usr_param.md1['sf2']['flag'] = 0
		self.mf.data.usr_param.md1['ss2']['flag'] = 0
		self.mf.data.usr_param.md1['te']['flag']  = 0
		self.mf.data.usr_param.md1['rex']['flag'] = 0

		if model == "m1":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
		if model == "m2":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['te']['flag']  = 1
		if model == "m3":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['rex']['flag'] = 1
		if model == "m4":
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['te']['flag']  = 1
			self.mf.data.usr_param.md1['rex']['flag'] = 1
		if model == "m5":
			self.mf.data.usr_param.md1['sf2']['flag'] = 1
			self.mf.data.usr_param.md1['ss2']['flag'] = 1
			self.mf.data.usr_param.md1['te']['flag']  = 1


