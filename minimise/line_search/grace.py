#! /usr/bin/python

from test_functions import *

for i in range(1000):
	x = [float(i) / 500.0]
	y = func3(x)
	print `x` + " " + `y`

