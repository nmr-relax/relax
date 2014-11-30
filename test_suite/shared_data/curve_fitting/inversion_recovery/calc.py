# Python module imports.
from math import exp


# Data.
relax_times = [0.2, 0.45, 0.75, 0.75, 1.1, 1.5, 1.95, 1.95, 2.45]
rx = 1.2
i0 = 30
iinf = 22

# Calculate I(t) for each t.
for time in relax_times:
    print("%.3f, %.15f" % (time, iinf - i0 * exp(-rx*time)))
