
import sys
from re import match

class main_palmer:
	def __init__(self):
		"The top level class."

		self.version = 0.5
		self.calc_relax_data = calc_relax_data(self)
		self.calc_chi2 = calc_chi2()
		self.data = data(self)
		self.data.usr_param = usr_param()
		self.file_ops = file_ops(self)
		self.star = star(self)

		# Debugging option.
		self.debug = 0

		self.print_header()

		if not self.version == self.data.usr_param.version:
			print "The versions numbers of the program and the file 'usr_param.py' do not match."
			print "Copy the correct version to the working directory, quitting program."
			sys.exit()

		if match('^AIC$', self.data.usr_param.method):
			asymptotic(self)
		elif match('^AICc$', self.data.usr_param.method):
			asymptotic(self)
		elif match('^BIC$', self.data.usr_param.method):
			asymptotic(self)
		elif match('^Bootstrap$', self.data.usr_param.method):
			bootstrap(self)
		elif match('^CV$', self.data.usr_param.method):
			cv(self)
		elif match('^Expect$', self.data.usr_param.method):
			exp_overall_disc(self)
		elif match('^Farrow$', self.data.usr_param.method):
			farrow(self)
		elif match('^Palmer$', self.data.usr_param.method):
			palmer(self)
		elif match('^Overall$', self.data.usr_param.method):
			overall_disc(self)
		else:
			print "The model-free analysis method is not set correctly.  Check self.method in"
			print "the file 'usr_param.py', quitting program."
			sys.exit()



	def print_header(self):
		"Print the header to screen."

		print """

		                      mf v0.5

		Program to process all model-free input and output.

		"""


if __name__ == "__main__":
	mf()
