from os import system
from re import match
from string import split
import sys


class common_ops:
	def __init__(self, mf):
		"Operations, functions, etc common to the different model-free analysis methods."

		self.mf = mf

	def extract_relax_data(self):
		"Extract the relaxation data from the files given in the file 'input'"
		print "\n[ Relaxation data extraction ]\n"
		for i in range(self.mf.data.num_ri):
			data = self.mf.file_ops.relax_data(self.mf.data.data_files[i])
			self.mf.data.relax_data.append(data)


	def fill_results(self, data, model='0'):
		"Initialise the next row of the results data structure."

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


	def log_input_info(self):
		for i in range(self.mf.data.num_ri):
			self.mf.log.write('%-25s%-20s\n' % ("Data label:", self.mf.data.data_types[i]))
			#self.mf.log.write('%-25s%-20s\n' % ("NMR frequency label:", self.mf.data.frq_label[i]))
			#self.mf.log.write('%-25s%-20s\n' % ("NMR proton frequency:", `self.mf.data.frq[i]`))
			self.mf.log.write('%-25s%-20s\n\n' % ("File name:", self.mf.data.files[i]))
		self.mf.log.write("Number of frequencies:\t" + `self.mf.data.num_frq` + "\n")
		self.mf.log.write("Number of data sets:\t" + `self.mf.data.num_ri` + "\n\n")


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
				file.write('%5.3f%1s%-5.3f  ' % ( self.mf.data.results[res]['s2'], '�', self.mf.data.results[res]['s2_err'] ))
			else:
				file.write('%13s' % '')
			if self.mf.data.results[res]['model'] in ["5"]:
				file.write('%5.3f%1s%-5.3f  ' % ( self.mf.data.results[res]['s2f'], '�', self.mf.data.results[res]['s2f_err'] ))
				file.write('%5.3f%1s%-5.3f  ' % ( self.mf.data.results[res]['s2s'], '�', self.mf.data.results[res]['s2s_err'] ))
			else:
				file.write('%26s' % '')
			if self.mf.data.results[res]['model'] in ["2", "4", "5"]:
				file.write('%8.2f%1s%-8.2f  ' % ( self.mf.data.results[res]['te'], '�', self.mf.data.results[res]['te_err'] ))
			else:
				file.write('%19s' % '')
			if self.mf.data.results[res]['model'] in ["3", "4"]:
				file.write('%5.3f%1s%-5.3f  ' % ( self.mf.data.results[res]['rex'], '�', self.mf.data.results[res]['rex_err'] ))
			else:
				file.write('%13s' % '')
			file.write('%10.3f\n' % self.mf.data.results[res]['chi2'])
		sys.stdout.write("]\n")

		file.close()


	def stage_selection(self):
		"The stage for model selection common to all techniques."

		print "\n[ Model-free data extraction ]\n"
		self.extract_mf_data()

 		print "\n[ " + self.mf.usr_param.method + " model selection ]\n"
		self.model_selection.run()

		print "\n[ Printing results ]\n"
		self.print_results()

		print "\n[ Placing data structures into \"data_all\" ]\n"
		self.print_data()

		print "\n[ Grace file creation ]\n"
		self.mf.file_ops.mkdir('grace')
		self.grace('grace/S2.agr', 'S2', subtitle="After model selection, unoptimised")
		self.grace('grace/S2f.agr', 'S2f', subtitle="After model selection, unoptimised")
		self.grace('grace/S2s.agr', 'S2s', subtitle="After model selection, unoptimised")
		self.grace('grace/te.agr', 'te', subtitle="After model selection, unoptimised")
		self.grace('grace/Rex.agr', 'Rex', subtitle="After model selection, unoptimised")
		self.grace('grace/Chi2.agr', 'Chi2', subtitle="After model selection, unoptimised")


	def update_data(self):
		"Extract all the information from the input info."


		trans_table = []
		trans_frq_table = []
		last_frq = 0.0
		self.mf.data.num_ri = len(self.mf.usr_param.input_info)

		# Create the frequency data structures.
		for i in range(self.mf.data.num_ri):
			flag = 1
			if len(self.mf.data.frq) > 0:
				for frq in range(len(self.mf.data.frq)):
					if self.mf.usr_param.input_info[i][2] == self.mf.data.frq[frq]:
						flag = 0
			# Update entries.
			if flag == 1:
				self.mf.data.num_frq = self.mf.data.num_frq + 1
				self.mf.data.frq_label.append(self.mf.usr_param.input_info[i][1])
				self.mf.data.frq.append(float(self.mf.usr_param.input_info[i][2]))
			trans_frq_table.append(self.mf.data.num_frq + 1)
			last_frq = self.mf.usr_param.input_info[i][2]

			# Fill the data structures with nothing.
			self.mf.data.data_types.append(None)
			self.mf.data.data_files.append(None)
			self.mf.data.remap_table.append(None)
			self.mf.data.noe_r1_table.append(None)
			trans_table.append(None)

		# Rearrange the data in self.mf.usr_param.input_info by creating the translation table 'trans_table'
		counter = 0
		for frq in range(len(self.mf.data.frq)):
			for i in range(self.mf.data.num_ri):
				if self.mf.data.frq[frq] == self.mf.usr_param.input_info[i][2]:
					if match('R1', self.mf.usr_param.input_info[i][0]):
						trans_table[i] = counter
						counter = counter + 1
			for i in range(self.mf.data.num_ri):
				if self.mf.data.frq[frq] == self.mf.usr_param.input_info[i][2]:
					if match('R2', self.mf.usr_param.input_info[i][0]):
						trans_table[i] = counter
						counter = counter + 1
			for i in range(self.mf.data.num_ri):
				if self.mf.data.frq[frq] == self.mf.usr_param.input_info[i][2]:
					if match('NOE', self.mf.usr_param.input_info[i][0]):
						trans_table[i] = counter
						counter = counter + 1

		# Fill the data structures using the trans_table to reorder.
		for i in range(self.mf.data.num_ri):
			self.mf.data.data_types[trans_table[i]] = self.mf.usr_param.input_info[i][0]
			self.mf.data.data_files[trans_table[i]] = self.mf.usr_param.input_info[i][3]
			for frq in range(len(self.mf.data.frq)):
				if self.mf.data.frq[frq] == self.mf.usr_param.input_info[i][2]:
					self.mf.data.remap_table[trans_table[i]] = frq
			if match('NOE', self.mf.usr_param.input_info[i][0]):
				for j in range(self.mf.data.num_ri):
					if match('R1', self.mf.usr_param.input_info[j][0]) and self.mf.usr_param.input_info[i][2] == self.mf.usr_param.input_info[j][2]:
						self.mf.data.noe_r1_table[trans_table[i]] = trans_table[j]

		if self.mf.debug == 1:
			print "%-20s%-20s" % ("Input info:", `self.mf.usr_param.input_info`)
			print "%-20s%-20s" % ("Trans frq table:", `trans_frq_table`)
			print "%-20s%-20s" % ("Trans table:", `trans_table`)
			print "%-20s%-20i" % ("Num ri:", self.mf.data.num_ri)
			print "%-20s%-20i" % ("Num frq:", self.mf.data.num_frq)
			print "%-20s%-20s" % ("Data types:", `self.mf.data.data_types`)
			print "%-20s%-20s" % ("Data files:", `self.mf.data.data_files`)
			print "%-20s%-20s" % ("Remap table:", `self.mf.data.remap_table`)
			print "%-20s%-20s" % ("NOE to R1 table:", `self.mf.data.noe_r1_table`)
			print "%-20s%-20s" % ("Frq labels:", `self.mf.data.frq_label`)
			print "%-20s%-20s" % ("Frqs:", `self.mf.data.frq`)
			print "\n"
