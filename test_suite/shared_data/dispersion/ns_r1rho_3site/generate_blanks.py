"""Script for generating blank input data for cpmg_fit."""

# Python module imports.
from os import sep


# The data.
frqs = [600, 800]
fields = [50, 75, 100, 200, 300, 400, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]
offsets = []
for i in range(21):
    offsets.append(i * 100.0 - 1000.0)

# Loop over the magnetic fields.
for frq in frqs:
    # Loop over the different spin-lock field strengths.
    for field in fields:
        # Open the output file.
        file_name = "%i_MHz_%i.res" % (frq, field)
        file = open('blank' + sep + file_name, 'w')

        # Loop over the offsets.
        for offset in offsets:
            # Write out the data.
            file.write("%20.12f %10.1f %10.1f\n" % (offset, 0.0, 0.5))
