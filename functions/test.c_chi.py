echo_on()
from c_chi2 import chi2
a, b, c = [1.6, 5.6], [1.3, 5.9], [0.3, 0.9]
d = chi2(a, b, c)
print "d: " + `d`
