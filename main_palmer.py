#! /usr/bin/python


# mf v0.4            4 January 2002        Edward d'Auvergne
#
# Program to process all model-free input and output.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


import sys
from re import match

from calc_relax_data import calc_relax_data
from calc_chi2 import calc_chi2
from data import data
from file_ops import file_ops
from star import star

sys.path.append(sys.path[0])
sys.path[0] = '.'
from usr_param import usr_param

from modsel.asymptotic import asymptotic
from modsel.bootstrap import bootstrap
from modsel.cross_validation import cv
from modsel.exp_overall_disc import exp_overall_disc
from modsel.farrow import farrow
from modsel.palmer import palmer
from modsel.overall_disc import overall_disc


class mf:
	def __init__(self):
		"The top level class."

		self.version = 0.4
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
			print "The versions numbers of the program and the file usr_param.py do not match."
			print "Copy the correct version to the working directory."
			print "Quitting script!"
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
			print "the file 'usr_param.py' which should be in the working directory."
			print "Quitting script!"
			sys.exit()



	def print_header(self):
		"Print the header to screen."

		print """

		                      mf v0.4

		Program to process all model-free input and output.

		"""


if __name__ == "__main__":
	mf()
