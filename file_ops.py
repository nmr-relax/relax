import sys
from re import match
from string import split

class file_ops:
	def __init__(self, mf):
		"Class containing the file operations"

		self.mf = mf

	def input(self):
		"Extract all the information from the input file"
		### Change structure so data is returned, ie no refs to self.mf ###

		try:
			open("input", 'r')
		except IOError:
			print "Input file \"input\" does not exist, quitting script!\n"
			sys.exit()
		input = open("input", 'r')
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
					self.mf.data.input_info.append([])
					self.mf.data.relax_data.append([])
					self.mf.data.input_info[num_data].append("R1")
					self.mf.data.input_info[num_data].append(row[0][1])
					self.mf.data.input_info[num_data].append(float(row[1][1]))
					self.mf.data.input_info[num_data].append(row[2][1])
					num_data = num_data + 1
				# R2 data.
				if not match('none', row[3][1]):
					self.mf.data.input_info.append([])
					self.mf.data.relax_data.append([])
					self.mf.data.input_info[num_data].append("R2")
					self.mf.data.input_info[num_data].append(row[0][1])
					self.mf.data.input_info[num_data].append(float(row[1][1]))
					self.mf.data.input_info[num_data].append(row[3][1])
					num_data = num_data + 1
				# NOE data.
				if not match('none', row[4][1]):
					self.mf.data.input_info.append([])
					self.mf.data.relax_data.append([])
					self.mf.data.input_info[num_data].append("NOE")
					self.mf.data.input_info[num_data].append(row[0][1])
					self.mf.data.input_info[num_data].append(float(row[1][1]))
					self.mf.data.input_info[num_data].append(row[4][1])
					num_data = num_data + 1
				frq = frq + 1
		self.mf.data.num_frq = frq
		self.mf.data.num_data_sets = num_data


	def relax_data(self, file):
		"Open the relaxation data in the file 'file' and return a 2D array with the data."
		lines = open(file, 'r')
		lines = lines.readlines()
		data = []
		i = 0
		for line in lines:
			if i != 0:
				j = i - 1
				row = split(line)
				data.append([])
				data[j].append(row[0])
				data[j].append(row[1])
				data[j].append(float(row[2]))
				data[j].append(float(row[3]))
			i = i + 1
		return data
