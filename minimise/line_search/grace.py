#! /usr/bin/python

from line_test_functions import *

for i in range(1000):
	x = float(i) / 500.0
	y = test_func3(x, deriv=1)
	print `x` + " " + `y`

