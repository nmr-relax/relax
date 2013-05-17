# Python script for truncating the peak intensity files to a couple of residues.

# Python module imports.
from os import listdir, sep
from re import search

# The directories to go into.
for dir in ['500_MHz', '800_MHz']:
    # Loop over the files in the directory.
    for file in listdir(dir):
        # Skip all files not ending in '.in'.
        if not search('.in_sparky$', file):
            continue

        # Read the file data.
        file_data = open(dir + sep + file)
        lines = file_data.readlines()
        file_data.close()

        # The output file.
        out = open(dir + sep + file[:-7] + '_trunc', 'w')

        # Loop over the lines.
        for line in lines:
            # Preserve the header lines.
            if line[0] == '\n' or line[:3] == 'Ass':
                out.write(line)
                continue

            # Skip almost all residues (except 70 and 71).
            if not search('^GLY7[01]', line):
                continue

            # Write out the data.
            out.write(line)
