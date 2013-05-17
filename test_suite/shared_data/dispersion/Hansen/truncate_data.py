# Python script for truncating the peak intensity files to a couple of residues.

# Python module imports.
from os import listdir, sep
from re import search

# The directories to go into.
for dir in ['500_MHz', '800_MHz']:
    # Loop over the files in the directory.
    for file in listdir(dir):
        # Skip all files not ending in '.in'.
        if file[-3:] != '.in':
            continue

        # Read the file data.
        file_data = open(dir + sep + file)
        lines = file_data.readlines()
        file_data.close()

        # The output file.
        out = open(dir + sep + file + '_trunc', 'w')

        # Loop over the lines.
        for line in lines:
            # Skip almost all residues (except 70 and 71).
            if not search('^7[01]', line):
                continue

            # Write out the data.
            out.write(line)
