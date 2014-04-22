"""Script for generating blank input data for cpmg_fit."""

# Python module imports.
from os import sep


# The data.
data = [
    ['NS', 'S', 'N15', 0.04, 1000.0],
    ['HS', 'S', 'H1', 0.03, 2667.0],
    ['DQ', 'D', 'H1/N15', 0.03, 1067.0],
    ['ZQ', 'Z', 'H1/N15', 0.03, 1067.0],
    ['NM', 'M', 'N15/H1', 0.02, 1000.0],
    ['HM', 'M', 'H1/N15', 0.02, 2500.0],
]

# Loop over the data.
for file_root, Q, nuc, time, max_frq in data:
    # Loop over some magnetic field strengths.
    for mag_frq in [400, 600, 800, 1000]:
        # Open the output file.
        file_name = "%s_%i.res" % (file_root, mag_frq)
        file = open('blank' + sep + file_name, 'w')

        # The minimum nu value.
        nu = 1.0 / time

        # Loop over nu until the max is reached.
        i = 0
        while True:
            # The CPMG frequency.
            frq = nu*(i+1)

            # Max reached.
            if frq > max_frq:
                break

            # Write out the data.
            file.write("%20.12f %10.1f %10.1f\n" % (frq, 0.0, 0.5))

            # Increment the nu counter.
            i += 1
