#! /usr/bin/python
real = [ 0.8289, 0.8926, 1.1880, 1.4585, 14.5899, 13.2717]
real_err = [ 0.04880, 0.08054, 0.0227, 0.0283, 0.2524, 0.4148]
back = [0.83060, 0.81200, 1.14339, 1.48044, 14.72210, 13.75411 ]
sum = 0
chi = []
for i in range(len(real)):
	chi.append((( real[i] - back[i] ) ** 2)/(real_err[i]**2))
	sum = sum + chi[i]
print "Chi2 = " + `sum`
