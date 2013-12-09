"""Script for splitting up the all.res file."""

# Open the file and extract the data.
file = open('all.res')
lines = file.readlines()
file.close()

# Separate the header.
head = lines[0]
lines = lines[1:]

# Loop over the data.
file = None
old_name = None
for line in lines:
    # Split up.
    row = line.split()

    # The file name.
    file_name = "%s_MHz_%i.res" % (row[2], float(row[6]))

    # A new file name.
    if file_name != old_name:
        # Close the old file.
        if file != None:
            file.close()

        # Open the new.
        file = open(file_name, 'w')

        # Write the header.
        file.write(head)

    # Write out the line.
    file.write(line)

    # Update the file name.
    old_name = file_name
