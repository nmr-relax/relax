"""Script of randomising the RDC and PCS data."""

from random import gauss
from string import split


# The errors.
SIGMA_RDC = 1.0
SIGMA_PCS = 0.1

# Open the noise free data files.
rdc_file = open('synth_rdc')
pcs_file = open('synth_pcs')

# Open the randomised data files.
rdc_out = open('synth_rdc_rand', 'w')
pcs_out = open('synth_pcs_rand', 'w')

# Loop over the RDC data.
for line in rdc_file.readlines():
    # Split the line up.
    row = split(line)

    # Randomise the value.
    val = gauss(float(row[5]), SIGMA_RDC)

    # Write the line out.
    rdc_out.write("%20s%10s%10s%10s%10s%30.11f\n" % (row[0], row[1], row[2], row[3], row[4], val))

# Loop over the PCS data.
for line in pcs_file.readlines():
    # Split the line up.
    row = split(line)

    # Randomise the value.
    val = gauss(float(row[5]), SIGMA_PCS)

    # Write the line out.
    pcs_out.write("%20s%10s%10s%10s%10s%30.11f\n" % (row[0], row[1], row[2], row[3], row[4], val))

# Close the files.
rdc_file.close()
rdc_out.close()
pcs_file.close()
pcs_out.close()
