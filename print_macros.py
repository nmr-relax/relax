import sys


class print_macros:
	def __init__(self):
		"Macros for printing data."


	def print_seq(self, res_num=None, res_name=None):
		"Macro to print sequence data."

		try:
			self.relax.data.seq
		except AttributeError:
			print "No sequence data loaded."
			return

		if res_num and res_name:
			for i in range(len(self.relax.data.seq)):
				if res_num == self.relax.data.seq[i][0] and res_name == self.relax.data.seq[i][1]:
					print "Res num: " + `self.relax.data.seq[i][0]` + ", name: " + self.relax.data.seq[i][1]
		
		elif res_num:
			for i in range(len(self.relax.data.seq)):
				if res_num == self.relax.data.seq[i][0]:
					print "Res num: " + `self.relax.data.seq[i][0]` + ", name: " + self.relax.data.seq[i][1]
					return
		elif res_name:
			for i in range(len(self.relax.data.seq)):
				if res_name == self.relax.data.seq[i][1]:
					print "Res num: " + `self.relax.data.seq[i][0]` + ", name: " + self.relax.data.seq[i][1]
		
		else:
			for i in range(len(self.relax.data.seq)):
				print "Res num: " + `self.relax.data.seq[i][0]` + ", name: " + self.relax.data.seq[i][1]
