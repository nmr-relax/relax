#! /usr/bin/python

def alpha(tm, s2, tp):
	a = s2
	return a

def beta(tm, s2, tp):
	if s2 == 0.0:
		b = 1e99
	else:
		b = tp ** (1.0 / s2)
	return b

def init_mf_params():
	s2 = []
	te = []
	s2_inc = 0.0
	te_inc = 0.0
	for i in range(21):
		s2.append(s2_inc)
		te.append(te_inc)
		s2_inc = s2_inc + 0.05
		te_inc = te_inc + 5.0 * 1e-10
	return s2, te


def map(tm, s2, te):
	for i in range(21):
		for j in range(21):
			tp = t_prime(tm, te[j])
			a = alpha(tm, s2[i], tp)
			b = beta(tm, s2[i], tp)
			print "%-4s%-12g%-4s%-12g%-7s%-12g%-7s%-12g" % ("S2:", s2[i], "te:", te[j] * 1e12, "Alpha:", a, "Beta:", b)


def t_prime(tm, te):
	if te == 0:
		tp = 0.0
	else:
		tp = 1.0 / (1.0/tm + 1.0/te)
	return tp


# Main.

s2, te = init_mf_params()
print "S2: " + `s2`
print "te: " + `te`
tm = 1e-8
map(tm, s2, te)


tm = 1e-8
mf_params = [0.970, 2048.0 * 1e-12, 0.149]
low_limits = [0.0, 0.0, 0.0]
up_limits = [1e-8, 1e-8, 0.3]
incs = [20.0, 20.0, 20.0]
tp = t_prime(tm, mf_params[1])

a = alpha(tm, mf_params[0], tp)
a_inc = (a * (incs[0]-1.0)) / (up_limits[0] - low_limits[0])

b = beta(tm, mf_params[0], tp)
b_inc = (b * (incs[1]-1.0)) / (up_limits[1] - low_limits[1])

g = mf_params[2]
g_inc = (g * (incs[2]-1.0)) / (up_limits[2] - low_limits[2])

print "Alpha: " + `a * 1e12` + " inc: " + `a_inc`
print "Beta:  " + `b * 1e12` + " inc: " + `b_inc`
print "Gamma: " + `g` + " inc: " + `g_inc`
