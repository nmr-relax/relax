"""Format the input files."""

from re import search


files = ['DQ_1000.res', 'DQ_400.res', 'DQ_600.res', 'DQ_800.res', 'HM_1000.res', 'HM_400.res', 'HM_600.res', 'HM_800.res', 'HS_1000.res', 'HS_400.res', 'HS_600.res', 'HS_800.res', 'NM_1000.res', 'NM_400.res', 'NM_600.res', 'NM_800.res', 'NS_1000.res', 'NS_400.res', 'NS_600.res', 'NS_800.res', 'ZQ_1000.res', 'ZQ_400.res', 'ZQ_600.res', 'ZQ_800.res']

# Loop over the files.
for file_name in files:
    # Open the original.
    file = open('../%s'%file_name)
    lines = file.readlines()
    file.close()

    # Open the new file.
    file = open(file_name, 'w')

    # Loop over the lines.
    for line in lines:
        # Skip the header.
        if search('^#', line):
            continue

        # Split the line.
        row = line.split()

        # Write out the data.
        file.write("%20s %20s %20s\n" % (row[6], row[9], row[8]))

    # Close the file.
    file.close()
