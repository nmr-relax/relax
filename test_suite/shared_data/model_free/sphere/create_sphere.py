# relax script for creating the spherical PDB file.
# Copyright 2004-2014, Edward d'Auvergne

# Python module imports.
from math import acos, cos, pi, sin, sqrt

# relax module imports.
from lib.structure.pdb_write import atom, conect, ter


# Number of increments.
number = 3

# U and V.
u = []
val = 1.0 / float(number)
for i in range(number):
    u.append(float(i) * val)


# Generate the spherical angles theta and phi.
##############################################

theta = []
phi = []
for i in range(len(u)):
    theta.append(acos(2.0 * (u[i] + val/2.0) - 1.0))
    phi.append(2.0 * pi * u[i])
    print("\ni: %s" % i)
    print("u: %s" % u[i])
    print("v: %s" % (u[i] + val/2.0))
    print("theta: %s" % theta[i])
    print("phi: %s" % phi[i])


# Generate the vectors:
#
#                 | sin(theta) * cos(phi) |
#      vector  =  | sin(theta) * sin(phi) |
#                 |      cos(theta)       |
#
###########################################

vectors = []
for i in range(len(u)):
    for j in range(len(u)):
        # X coordinate.
        x = sin(theta[i]) * cos(phi[j])

        # Y coordinate.
        y = sin(theta[i]) * sin(phi[j])

        # Z coordinate.
        z = cos(theta[i])

        # Append the vector.
        vectors.append([x, y, z])


# Create the PDB file.
######################

# PDB file.
file = open('sphere.pdb', 'w')

# Atom number and residue number.
atom_num = 1
res_num = 1

# Used vectors.
used = []

# Loop over the vectors. 
for i in range(len(vectors)):
    # Test if the vector has already been used.
    if vectors[i] in used:
        print("Vector %s already used." % vectors[i])
        continue

    # Nitrogen line.
    atom(file=file, serial=atom_num, name='N', res_seq=res_num, res_name='GLY', x=0.0, y=0.0, z=0.0)

    # Hydrogen line.
    atom(file=file, serial=atom_num+1, name='H', res_seq=res_num, res_name='GLY', x=vectors[i][0], y=vectors[i][1], z=vectors[i][2])

    # Increment the atom number and residue number.
    atom_num = atom_num + 2
    res_num = res_num + 1

    # Add the vector to the used vector list.
    used.append(vectors[i])

# Add a Trp indole NH for luck ;)
atom(file=file, serial=atom_num, name='NE1', res_seq=res_num-1, res_name='GLY', x=0.0, y=0.0, z=0.0)
atom(file=file, serial=atom_num+1, name='HE1', res_seq=res_num-1, res_name='GLY', x=1/sqrt(3), y=1/sqrt(3), z=1/sqrt(3))

# Add a TER record.
ter(file=file, serial=atom_num+2, res_name='GLY')

# Connect everything.
atom_num = 1
for i in range(len(vectors)):
    conect(file=file, serial=atom_num, bonded1=atom_num+1)
    conect(file=file, serial=atom_num+1, bonded1=atom_num)
    atom_num = atom_num + 2
conect(file=file, serial=atom_num, bonded1=atom_num+1)
conect(file=file, serial=atom_num+1, bonded1=atom_num)

# End of PDB.
file.write('END\n')
