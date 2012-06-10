#! /usr/bin/env python

from string import split, strip


# The file data.
file = open('testNOE.txt')
lines = file.readlines()
file.close()

# Get the data.
data = []
in_data = False
index = 0
for line in lines:
    # Split the line.
    row = split(line, "\t")

    # Strip the rubbish.
    for j in range(len(row)):
        row[j] = strip(row[j])

    # Empty line.
    if len(row) == 0:
        continue

    # The section.
    if row[0] == 'SECTION:' and row[1] == 'results':
        in_data = True
        continue

    # Not in the data section.
    if not in_data:
        continue

    # The header line.
    if row[0] == 'Peak name':
        continue

    # The residue name and number.
    res_name, res_num = split(row[0])

    # The values.
    data.append([])
    data[index].append(res_name)
    data[index].append(int(res_num[1:-1]))
    data[index].append(float(row[3]))
    data[index].append(float(row[4]))

    # Increment the residue index.
    index += 1

noe = []
noe_err = []
for i in range(len(data)):
    noe.append(data[i][2])
    noe_err.append(data[i][3])

print("\nnoe = %s" % noe)
print("\nnoe_err = %s" % noe_err)
