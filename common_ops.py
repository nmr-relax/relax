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


	def create_mfdata(self, res, flag='1'):
		"Create the Modelfree input file mfdata"

		text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
		k = 0
		for i in range(len(self.mf.data.nmr_frq)):
			for j in range(3):
				if match('1', self.mf.data.nmr_frq[i][j+2]):
					text = text + '%-7s' % self.mf.data.input_info[k][0]
					text = text + '%-10s' % self.mf.data.input_info[k][1]
					text = text + '%10s' % self.mf.data.relax_data[k][res][2]
					text = text + '%10s' % self.mf.data.relax_data[k][res][3]
					text = text + ' %-3s\n' % flag
					k = k + 1
				else:
					if j == 0:
						text = text + '%-7s' % 'R1'
					if j == 1:
						text = text + '%-7s' % 'R2'
					if j == 2:
						text = text + '%-7s' % 'NOE'
					text = text + '%-10s' % self.mf.data.nmr_frq[i][0]
					text = text + '%10s' % '0.000'
					text = text + '%10s' % '0.000'
					text = text + ' %-3s\n' % '0'
		self.mf.mfdata.write(text)


	def create_mfin(self, sel='none', algorithm='fix', diffusion_search='none', sims='n', sim_type='pred'):
		"Create the Modelfree input file mfin"

		text = ""
		text = text + "optimization    tval\n\n"
		text = text + "seed            0\n\n"
		text = text + "search          grid\n\n"
		text = text + "diffusion       " + self.mf.data.usr_param.diff + " " + diffusion_search + "\n\n"
		text = text + "algorithm       " + algorithm + "\n\n"
		if match('y', sims):
			text = text + "simulations     " + sim_type + "    " + self.mf.data.usr_param.no_sim
			text = text + "       " + self.mf.data.usr_param.trim + "\n\n"
		elif match('n', sims):
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
		
		self.mf.mfin.write(text)


	def create_mfmodel(self, res, md, type='M1'):
		"Create the M1 or M2 section of the Modelfree input file mfmodel"

		if match('M1', type):
			text = "\nspin     " + self.mf.data.relax_data[0][res][1] + "_" + self.mf.data.relax_data[0][res][0] + "\n"
		else:
			text = "\n"

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

		self.mf.mfmodel.write(text)


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

		self.mf.mfpar.write(text)


	def create_run(self, dir):
		"Create the file 'run' to execute the model-free run"

		text = "modelfree4 -i mfin -d mfdata -p mfpar -m mfmodel -o mfout -e out"
		if self.mf.data.usr_param.diff == 'axial':
			# Copy the pdb file to the model directory so there are no problems with the *.rotate
			# file already existing.
			copy(self.mf.data.usr_param.pdb_full, dir)
			text = text + " -s " + self.mf.data.usr_param.pdb_file
		text = text + "\n"
		self.mf.run.write(text)


	def extract_input(self, input):
		"Extract all the information from the input file."

		lines = input.readlines()
		frq = 0
		num_data = 0
		for i in range(len(lines)):
			row = [[]]
			row[0] = split(lines[i])
			try:
				row[0][0]
			except IndexError:
				continue
			if match('NMR_frq_label', row[0][0]):
				self.mf.data.nmr_frq.append([])
				row.append(split(lines[i+1]))
				row.append(split(lines[i+2]))
				row.append(split(lines[i+3]))
				row.append(split(lines[i+4]))
				# NMR data.
				self.mf.data.nmr_frq[frq].append(row[0][1])
				self.mf.data.nmr_frq[frq].append(row[1][1])
				# R1 data.
				if not match('none', row[2][1]):
					self.mf.data.nmr_frq[frq].append('1')
					self.mf.data.input_info.append([])
					self.mf.data.relax_data.append([])
					self.mf.data.input_info[num_data].append("R1")
					self.mf.data.input_info[num_data].append(row[0][1])
					self.mf.data.input_info[num_data].append(float(row[1][1]))
					self.mf.data.input_info[num_data].append(row[2][1])
					num_data = num_data + 1
				else:
					self.mf.data.nmr_frq[frq].append('0')
				# R2 data.
				if not match('none', row[3][1]):
					self.mf.data.nmr_frq[frq].append('1')
					self.mf.data.input_info.append([])
					self.mf.data.relax_data.append([])
					self.mf.data.input_info[num_data].append("R2")
					self.mf.data.input_info[num_data].append(row[0][1])
					self.mf.data.input_info[num_data].append(float(row[1][1]))
					self.mf.data.input_info[num_data].append(row[3][1])
					num_data = num_data + 1
				else:
					self.mf.data.nmr_frq[frq].append('0')
				# NOE data.
				if not match('none', row[4][1]):
					self.mf.data.nmr_frq[frq].append('1')
					self.mf.data.input_info.append([])
					self.mf.data.relax_data.append([])
					self.mf.data.input_info[num_data].append("NOE")
					self.mf.data.input_info[num_data].append(row[0][1])
					self.mf.data.input_info[num_data].append(float(row[1][1]))
					self.mf.data.input_info[num_data].append(row[4][1])
					num_data = num_data + 1
				else:
					self.mf.data.nmr_frq[frq].append('0')
				frq = frq + 1
		self.mf.data.num_frq = frq
		self.mf.data.num_data_sets = num_data


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


	def final_run(self):
		"""Model selection and the creation of the final run.
		
		Monte Carlo simulations are used to find errors, and the diffusion tensor is unoptimized.
		Files are placed in the directory 'final'.
		"""

		self.mf.file_ops.open_mf_files(dir='final')
		self.create_mfin(sims='y')

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


	def final_run_optimized(self):
		"""The final optimization run.
		
		Create the modelfree4 files for the optimization of the diffusion tensor together with
		the model free parameters for the selected models.
		"""

		self.mf.file_ops.open_mf_files(dir='final')
		if match('isotropic', self.mf.data.usr_param.diff):
			self.create_mfin(algorithm='brent', diffusion_search='grid')
		elif match('axial', self.mf.data.usr_param.diff):
			self.create_mfin(algorithm='powell')

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


	def grace(self, file_name, type, subtitle):
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

		file = open(file_name, 'w')
		file.write(text)
		file.close()


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


	def log_input_info(self):
		self.mf.log.write("The input info data structure is:\n" + `self.mf.data.input_info` + "\n\n")
		for i in range(len(self.mf.data.input_info)):
			text = ""
			text = text + '%-25s%-20s\n' % ("Data label:", self.mf.data.input_info[i][0])
			text = text + '%-25s%-20s\n' % ("NMR frequency label:", self.mf.data.input_info[i][1])
			text = text + '%-25s%-20s\n' % ("NMR proton frequency:", `self.mf.data.input_info[i][2]`)
			text = text + '%-25s%-20s\n\n' % ("File name:", self.mf.data.input_info[i][3])
			self.mf.log.write(text)
		self.mf.log.write("Number of frequencies:\t" + `self.mf.data.num_frq` + "\n")
		self.mf.log.write("Number of data sets:\t" + `self.mf.data.num_data_sets` + "\n\n")


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


	def print_data(self, ftests='n'):
		"Print the results into the results file."

		text = ''
		for res in range(len(self.mf.data.results)):
			text = text + "<<< Residue " + self.mf.data.results[res]['res_num']
			text = text + ", Model " + self.mf.data.results[res]['model'] + " >>>\n"
			text = text + '%-10s' % ''
			text = text + '%-8s%-8s%-8s%-8s' % ( 'S2', 'S2_err', 'S2f', 'S2f_err' )
			text = text + '%-8s%-8s' % ( 'S2s', 'S2s_err' )
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
					text = text + '%-8s' % self.mf.data.data[run][res]['s2s']
					text = text + '%-8s' % self.mf.data.data[run][res]['s2s_err']
					text = text + '%-10s' % self.mf.data.data[run][res]['te']
					text = text + '%-10s' % self.mf.data.data[run][res]['te_err']
					text = text + '%-8s' % self.mf.data.data[run][res]['rex']
					text = text + '%-8s' % self.mf.data.data[run][res]['rex_err']
					text = text + '%-10s' % self.mf.data.data[run][res]['sse']
					text = text + '%-10s' % self.mf.data.data[run][res]['sse_lim']
					text = text + '%-10s' % self.mf.data.data[run][res]['sse_test']
					text = text + '%-10s' % self.mf.data.data[run][res]['large_sse']
					text = text + '%-10s\n' % self.mf.data.data[run][res]['zero_sse']
			if match('y', ftests):
				text = text + '%-10s' % ''
				text = text + '%-18s' % 'F-stat'
				text = text + '%-18s' % 'F-stat limit'
				text = text + '%-18s\n' % 'F-test result'
				for run in self.mf.data.runs:
					if match('^f', run):
						text = text + '%-10s' % run
						text = text + '%-18s' % self.mf.data.data[run][res]['fstat']
						text = text + '%-18s' % self.mf.data.data[run][res]['fstat_lim']
						text = text + '%-18s\n' % self.mf.data.data[run][res]['ftest']
			text = text + '\n'

		self.data_file = open('data_all', 'w')
		self.data_file.write(text)
		self.data_file.close()


	def print_results(self):
		"Print the results into the results file."
		
		text = '%-6s%-6s%-13s%-13s%-13s' % ( 'ResNo', 'Model', '    S2', '    S2f', '    S2s' )
		text = text + '%-19s%-13s%-10s\n' % ( '       te', '    Rex', '    SSE' )
		for res in range(len(self.mf.data.results)):
			text = text + '%-6s' % self.mf.data.results[res]['res_num']
			text = text + '%-6s' % self.mf.data.results[res]['model']
			
			if match('[1,2,3,4,5]', self.mf.data.results[res]['model']):
				text = text + '%5s%1s%-5s  ' % ( self.mf.data.results[res]['s2'], '±', self.mf.data.results[res]['s2_err'] )
			else:
				text = text + '%13s' % ''
			if match('5', self.mf.data.results[res]['model']):
				text = text + '%5s%1s%-5s  ' % ( self.mf.data.results[res]['s2f'], '±', self.mf.data.results[res]['s2f_err'] )
				text = text + '%5s%1s%-5s  ' % ( self.mf.data.results[res]['s2s'], '±', self.mf.data.results[res]['s2s_err'] )
			else:
				text = text + '%26s' % ''
			if match('[2,4,5]', self.mf.data.results[res]['model']):
				text = text + '%8s%1s%-8s  ' % ( self.mf.data.results[res]['te'], '±', self.mf.data.results[res]['te_err'] )
			else:
				text = text + '%19s' % ''
			if match('[3,4]', self.mf.data.results[res]['model']):
				text = text + '%5s%1s%-5s  ' % ( self.mf.data.results[res]['rex'], '±', self.mf.data.results[res]['rex_err'] )
			else:
				text = text + '%13s' % ''
			text = text + '%10s\n' % self.mf.data.results[res]['sse']

		self.results_file = open('results', 'w')
		self.results_file.write(text)
		self.results_file.close()


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


	def stage3(self):
		print "Stage 3 not implemented yet.\n"
		sys.exit()


	def start_up(self, stage, title):
		"A few operations to start up the program."

		self.mf.file_ops.init_log_file(stage, title)
		input = self.mf.file_ops.open_input()
		self.extract_input(input)
		self.extract_relax_data()
		self.log_input_info()
