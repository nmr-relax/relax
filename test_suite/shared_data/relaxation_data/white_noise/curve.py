# Generate an exponential curve.

from math import exp


rx = 2.25
i0 = 10000.0
times = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

intensities = []
for i in range(len(times)):
    intensities.append(i0 * exp(-rx*times[i]))

print(intensities)
