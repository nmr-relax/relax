"""Format the input files."""

from re import search


files = ['600_MHz_1000.res', '600_MHz_100.res', '600_MHz_1500.res', '600_MHz_2000.res', '600_MHz_200.res', '600_MHz_2500.res', '600_MHz_3000.res', '600_MHz_300.res', '600_MHz_3500.res', '600_MHz_4000.res', '600_MHz_400.res', '600_MHz_4500.res', '600_MHz_5000.res', '600_MHz_500.res', '600_MHz_50.res', '600_MHz_5500.res', '600_MHz_6000.res', '600_MHz_75.res', '800_MHz_1000.res', '800_MHz_100.res', '800_MHz_1500.res', '800_MHz_2000.res', '800_MHz_200.res', '800_MHz_2500.res', '800_MHz_3000.res', '800_MHz_300.res', '800_MHz_3500.res', '800_MHz_4000.res', '800_MHz_400.res', '800_MHz_4500.res', '800_MHz_5000.res', '800_MHz_500.res', '800_MHz_50.res', '800_MHz_5500.res', '800_MHz_6000.res', '800_MHz_75.res']

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
        file.write("%20s %20s %20s\n" % (row[5], row[9], row[8]))

    # Close the file.
    file.close()
