import sys
from re import match
from string import split

class star:
	def __init__(self):
		"Class to extract modelfree data from the STAR formatted mfout file."


	def extract(self, mfout, num_res, ftest='n'):
		"Extract the data from the mfout file and Return it as a 2D data structure."

		self.mfout = mfout
		self.num_res = num_res

		self.data = []
		for i in range(self.num_res):
			self.data.append({})

		for self.line in range(len(self.mfout)):
			self.row = [[]]
			self.row[0] = split(self.mfout[self.line])

			try:
				self.row[0][0]
			except IndexError:
				continue
			try:
				self.row[0][1]
			except IndexError:
				self.row[0].append('')

			if match('S2$', self.row[0][0]) and match('\(\)', self.row[0][1]):
				self.get_s2()
			if match('S2f', self.row[0][0]) and match('\(\)', self.row[0][1]):
				self.get_s2f()
			if match('S2s', self.row[0][0]) and match('\(\)', self.row[0][1]):
				self.get_s2s()
			if match('te', self.row[0][0]) and match('\(ps\)', self.row[0][1]):
				self.get_te()
			if match('Rex', self.row[0][0]) and match('\(1\/s\)', self.row[0][1]):
				self.get_rex()
			if match('data_sse', self.row[0][0]):
				self.get_sse()
				break
			if match('y', ftest):
				self.get_ftest()
		print "\nData:\n" + `self.data[0]`
		return self.data


	def get_ftest(self):
		return


	def get_rex(self):
		print "Match Rex " + `self.row[0]`
		self.split_rows()
		for i in range(self.num_res):
			j = i + 1
			self.data[i]['rex'] = self.row[j][1]
			self.data[i]['rex_err'] = self.row[j][5]


	def get_s2(self):
		print "Match S2 " + `self.row[0]`
		self.split_rows()
		for i in range(self.num_res):
			j = i + 1
			self.data[i]['res_num'] = self.row[j][0]
			self.data[i]['s2'] = self.row[j][1]
			self.data[i]['s2_err'] = self.row[j][5]


	def get_s2f(self):
		print "Match S2f " + `self.row[0]`
		self.split_rows()
		for i in range(self.num_res):
			j = i + 1
			self.data[i]['s2f'] = self.row[j][1]
			self.data[i]['s2f_err'] = self.row[j][5]


	def get_s2s(self):
		print "Match S2s " + `self.row[0]`
		self.split_rows()
		for i in range(self.num_res):
			j = i + 1
			self.data[i]['s2s'] = self.row[j][1]
			self.data[i]['s2s_err'] = self.row[j][5]


	def get_sse(self):
		print "Match SSE " + `self.row[0]`
		self.row[0] = split(self.mfout[self.line + 5])
		line_num = self.line + 5
		for i in range(self.num_res):
			for j in range(20):
				self.row.append(split(self.mfout[line_num + j]))
			self.data[i]['sse'] = self.row[0][1]


	def get_te(self):
		print "Match te " + `self.row[0]`
		self.split_rows()
		for i in range(self.num_res):
			j = i + 1
			self.data[i]['te'] = self.row[j][1]
			self.data[i]['te_err'] = self.row[j][5]


	def split_rows(self):
		"Get the next 'num_res' lines after a match."

		for i in range(self.num_res):
			j = i + 1
			self.row.append(split(self.mfout[self.line + j]))
