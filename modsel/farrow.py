# The method given by Farrow et al., 1994:
#
#	Stage 1:   Creation of the files for the initial model-free calculations for models 1 to 5,
#		and f-tests between them.
#	Stage 2:   Model selection.
#

import sys
from re import match

from common_ops import common_operations


class farrow(common_operations):
	def __init__(self, mf):
		"The model-free analysis of Farrow."

		self.mf = mf

		print "Farrow's method for model-free analysis. (Farrow et al., 1994)"
		self.initialize()
		self.mf.data.runs = ['m1', 'm2', 'm3', 'm4', 'm5', 'f-m1m2', 'f-m1m3']
		if self.mf.data.num_data_sets > 3:
			self.mf.data.runs.append('f-m2m4')
			self.mf.data.runs.append('f-m2m5')
			self.mf.data.runs.append('f-m3m4')
		self.goto_stage()


	def model_selection(self):
		"Farrow's model selection."

		data = self.mf.data.data

		self.mf.log.write("\n\n<<< Farrow's model selection >>>")
		for res in range(len(self.mf.data.relax_data[0])):
			self.mf.data.results.append({})
			self.mf.log.write('\n%-22s' % ( "   Checking res " + data['m1'][res]['res_num'] ))

			# Model 1 test.
			if data['m1'][res]['chi2_test'] == 1:
				self.mf.log.write('%-12s' % '[Model 1]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 2 and 3 fit!!! (Should not occur)
			elif data['m2'][res]['chi2_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1 \
				and data['m3'][res]['chi2_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2 and 3]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='2+3')

			# Model 2 test.
			elif data['m2'][res]['chi2_test'] == 1 and data['f-m1m2'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 2]')
				self.mf.data.results[res] = self.fill_results(data['m2'][res], model='2')

			# Model 3 test.
			elif data['m3'][res]['chi2_test'] == 1 and data['f-m1m3'][res]['ftest'] == 1:
				self.mf.log.write('%-12s' % '[Model 3]')
				self.mf.data.results[res] = self.fill_results(data['m3'][res], model='3')

			# Large chi squared test for model 1.
			elif data['m1'][res]['large_chi2'] == 0:
				self.mf.log.write('%-12s' % '[Model 1*]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='1')

			# Test if both model 4 and 5 fit!!! (Should not occur)
			elif data['m4'][res]['zero_chi2'] == 1 and data['m5'][res]['zero_chi2'] == 1:
				self.mf.log.write('%-12s' % '[Model 4 and 5]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='4+5')

			# Model 4 test.
			elif data['m4'][res]['zero_chi2'] == 1:
				self.mf.log.write('%-12s' % '[Model 4]')
				self.mf.data.results[res] = self.fill_results(data['m4'][res], model='4')

			# Model 5 test.
			elif data['m5'][res]['zero_chi2'] == 1:
				self.mf.log.write('%-12s' % '[Model 5]')
				self.mf.data.results[res] = self.fill_results(data['m5'][res], model='5')

			# No model fits!
			else:
				self.mf.log.write('%-12s' % '[Model 0]')
				self.mf.data.results[res] = self.fill_results(data['m1'][res], model='0')
