import sys
from string import split

class file_ops:
	def __init__(self, mf):
		"Class containing the file operations"

		self.mf = mf

	def input(self):
		"Extract all the information from the input file"

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
			if row[0][0] == "NMR_frq_label":
				self.mf.data.input_info.append([])
				row.append(split(lines[i+1]))
				row.append(split(lines[i+2]))
				row.append(split(lines[i+3]))
				row.append(split(lines[i+4]))
				self.mf.data.input_info[frq].append(row[0][1])
				self.mf.data.input_info[frq].append(float(row[1][1]))
				self.mf.data.input_info[frq].append(row[2][1])
				self.mf.data.input_info[frq].append(row[3][1])
				self.mf.data.input_info[frq].append(row[4][1])
				# R1 data.
				if row[2][1] != "none":
					self.mf.data.relax_data.append([])
					self.mf.data.relax_data[num_data].append("R1")
					self.mf.data.relax_data[num_data].append(float(row[1][1]))
					self.mf.data.relax_data[num_data].append(row[2][1])
					num_data = num_data + 1
				# R2 data.
				if row[3][1] != "none":
					self.mf.data.relax_data.append([])
					self.mf.data.relax_data[num_data].append("R2")
					self.mf.data.relax_data[num_data].append(float(row[1][1]))
					self.mf.data.relax_data[num_data].append(row[3][1])
					num_data = num_data + 1
				# NOE data.
				if row[4][1] != "none":
					self.mf.data.relax_data.append([])
					self.mf.data.relax_data[num_data].append("NOE")
					self.mf.data.relax_data[num_data].append(float(row[1][1]))
					self.mf.data.relax_data[num_data].append(row[4][1])
					num_data = num_data + 1
				frq = frq + 1
		self.mf.data.num_frq = frq
		self.mf.data.num_data_sets = num_data
			

	def log_file(self):
		"Open the log file"

		file_name = "log.stage" + self.mf.data.stage
		self.mf.log = open(file_name, 'w')
		self.mf.log.write("<<< Stage " + self.mf.data.stage + " of Modelfree analysis >>>\n\n\n")

	def relax_data(self, file):
		"Open the relaxation data in the file 'file' and return a 2D array with the data."
		temp = open(file, 'r')
		temp = temp.readlines()
		data = []
		i = 0
		for line in temp:
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
