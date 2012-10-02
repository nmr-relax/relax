"""Script of randomising the RDC and PCS data."""

from random import gauss


# The errors.
SIGMA_RDC = 1.0
SIGMA_PCS = 0.1

# Open the noise free data files.
rdc_file = open('synth_rdc')
pcs_file = open('synth_pcs')

# Open the randomised data files.
rdc_out = open('synth_rdc_rand', 'w')
pcs_out = open('synth_pcs_rand', 'w')

# Open the Pales input file.
pales_file = open('pales_rand.in', 'w')

# The Pales header.
pales_file.write("DATA SEQUENCE ADQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLT\n")
pales_file.write("DATA SEQUENCE MMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREANIDGDGQVNYEE\n")
pales_file.write("DATA SEQUENCE FVQMMTAK\n\n")
pales_file.write("VARS   RESID_I RESNAME_I ATOMNAME_I RESID_J RESNAME_J ATOMNAME_J D      DD    W\n")
pales_file.write("FORMAT %5d     %6s       %6s        %5d     %6s       %6s    %9.3f   %9.3f %.2f\n\n")

# Loop over the RDC data.
for line in rdc_file.readlines():
    # Split the line up.
    row = line.split()

    # Randomise the value.
    val = gauss(float(row[2]), SIGMA_RDC)

    # Write the line out.
    rdc_out.write("%-20s %-20s %30.11f\n" % (row[0], row[1], val))

    # The Pales data line (equal weight, no errors).
    #pales_file.write("%5s     %6s       %6s        %5s     %6s       %6s    %9.3f   %9.3f %.2f\n" % (row[1], row[2], row[4], row[1], row[2], 'H', val, 0.0, 1.0))


# Loop over the PCS data.
for line in pcs_file.readlines():
    # Split the line up.
    row = line.split()

    # Randomise the value.
    val = gauss(float(row[5]), SIGMA_PCS)

    # Write the line out.
    pcs_out.write("%20s%10s%10s%10s%10s%30.11f\n" % (row[0], row[1], row[2], row[3], row[4], val))

# Close the files.
rdc_file.close()
rdc_out.close()
pcs_file.close()
pcs_out.close()
