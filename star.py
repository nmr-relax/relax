import sys
from re import match
from string import split

class star:
	def __init__(self):
		"Class to extract modelfree data from the STAR formatted mfout file."


	def extract(self, mfout, num_res, sse_lim='0.90', ftest_lim='0.80', large_sse=20, ftest='n'):
		"Extract the data from the mfout file and Return it as a 2D data structure."

		self.mfout = mfout
		self.num_res = num_res
		self.sse_lim = sse_lim
		self.ftest_lim = ftest_lim
		self.large_sse = large_sse

		self.data = []
		for i in range(self.num_res):
			self.data.append({})
		self.line_num = 0

		if match('n', ftest):
			# Jump to first line of data.
			for line in range(len(self.mfout)):
				self.row = [[]]
				self.row[0] = split(self.mfout[line])
				try:
					self.row[0][1]
				except IndexError:
					continue
				if match('S2$', self.row[0][0]) and match('\(\)', self.row[0][1]):
					self.line_num = line
					break
			self.get_s2()
			self.get_s2f()
			self.get_s2s()
			self.get_te()
			self.get_rex()
			self.get_sse()

		if match('y', ftest):
			# Jump to first line of data.
			for line in range(len(self.mfout)):
				self.row = [[]]
				self.row[0] = split(self.mfout[line])
				try:
					self.row[0][0]
				except IndexError:
					continue
				if match('data_F_dist', self.row[0][0]):
					self.line_num = line
					break
			self.get_ftest()

		return self.data


	def get_ftest(self):
		self.line_num = self.line_num + 5
		for i in range(self.num_res):
			self.row = [[]]
			self.row[0] = split(self.mfout[self.line_num])
			percentile = int(float(self.ftest_lim) * 100 / 5)
			self.line_num = self.line_num + percentile
			self.row.append(split(self.mfout[self.line_num]))
			lines_next_res = 2 + ( 20 - percentile )
			self.line_num = self.line_num + lines_next_res
			self.data[i]['res_num'] = self.row[0][0]
			self.data[i]['fstat'] = float(self.row[0][1])
			self.data[i]['fstat_lim'] = float(self.row[1][1])
			if self.data[i]['fstat_lim'] > 1.5 and self.data[i]['fstat'] < self.data[i]['fstat_lim']:
				self.data[i]['ftest'] = 1
			elif self.data[i]['fstat_lim'] < 1.5 and self.data[i]['fstat'] > 1.5:
				self.data[i]['ftest'] = 1
			else:
				self.data[i]['ftest'] = 0


	def get_rex(self):
		self.line_num = self.line_num + self.num_res + 3
		self.row = [[]]
		self.row[0] = split(self.mfout[self.line_num])
		self.split_rows(self.line_num, self.num_res)
		for i in range(self.num_res):
			j = i + 1
			self.data[i]['rex'] = self.row[j][1]
			self.data[i]['rex_err'] = self.row[j][5]


	def get_s2(self):
		self.split_rows(self.line_num, self.num_res)
		for i in range(self.num_res):
			j = i + 1
			self.data[i]['res_num'] = self.row[j][0]
			self.data[i]['s2'] = self.row[j][1]
			self.data[i]['s2_err'] = self.row[j][5]


	def get_s2f(self):
		self.line_num = self.line_num + self.num_res + 3
		self.row = [[]]
		self.row[0] = split(self.mfout[self.line_num])
		self.split_rows(self.line_num, self.num_res)
		for i in range(self.num_res):
			j = i + 1
			self.data[i]['s2f'] = self.row[j][1]
			self.data[i]['s2f_err'] = self.row[j][5]


	def get_s2s(self):
		self.line_num = self.line_num + self.num_res + 3
		self.row = [[]]
		self.row[0] = split(self.mfout[self.line_num])
		self.split_rows(self.line_num, self.num_res)
		for i in range(self.num_res):
			j = i + 1
			self.data[i]['s2s'] = self.row[j][1]
			self.data[i]['s2s_err'] = self.row[j][5]


	def get_sse(self):
		self.line_num = self.line_num + self.num_res + 8
		for i in range(self.num_res):
			self.row = [[]]
			self.row[0] = split(self.mfout[self.line_num])
			percentile = int(float(self.sse_lim) * 100 / 5)
			self.line_num = self.line_num + percentile
			self.row.append(split(self.mfout[self.line_num]))
			lines_next_res = 2 + ( 20 - percentile )
			self.line_num = self.line_num + lines_next_res
			self.data[i]['sse'] = float(self.row[0][1])
			self.data[i]['sse_lim'] = float(self.row[1][1])

			# Chi-squared test.
			if self.data[i]['sse'] <= self.data[i]['sse_lim']:
				self.data[i]['sse_test'] = 1
			else:
				self.data[i]['sse_test'] = 0

			# Large SSE test.
			if self.data[i]['sse'] >= self.large_sse:
				self.data[i]['large_sse'] = 1
			else:
				self.data[i]['large_sse'] = 0

			# Zero SSE test.
			if self.data[i]['sse'] == 0:
				self.data[i]['zero_sse'] = 1
			else:
				self.data[i]['zero_sse'] = 0


	def get_te(self):
		self.line_num = self.line_num + self.num_res + 3
		self.row = [[]]
		self.row[0] = split(self.mfout[self.line_num])
		self.split_rows(self.line_num, self.num_res)
		for i in range(self.num_res):
			j = i + 1
			self.data[i]['te'] = self.row[j][1]
			self.data[i]['te_err'] = self.row[j][5]


	def split_rows(self, line_num, num_lines):
		"Get the next 'num_res' lines after a match."

		for i in range(num_lines):
			j = i + 1
			self.row.append(split(self.mfout[line_num + j]))
