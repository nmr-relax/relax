#!/usr/bin/python

# Copyright 2004, Edward d'Auvergne

from math import acos, cos, pi, sin


def pdb_line(file=None, atom_num=0, atom=None, res_num=0, res_name=None, vector=None):
    """Function for adding a line to the PDB file."""

    # ATOM.
    file.write('%-4s' % 'ATOM')

    # Atom number and type.
    file.write('%7i' % atom_num)
    file.write('  %-4s' % atom)

    # Residue number and name.
    file.write('%-4s' % res_name)
    file.write('%5i    ' % res_num)

    # Vector.
    file.write('%8.3f' % vector[0])
    file.write('%8.3f' % vector[1])
    file.write('%8.3f' % vector[2])

    # I don't know what.
    file.write('%6.2f' % 1.0)
    file.write('%6.2f' % 0.0)

    # End of line.
    file.write('\n')


# Number of increments.
number = 20

# U and V.
u = []
val = 1.0 / float(number)
for i in xrange(number):
    u.append(float(i) * val)


# Generate the spherical angles theta and phi.
##############################################

theta = []
phi = []
for i in xrange(len(u)):
    theta.append(acos(2.0 * (u[i] + val/2.0) - 1.0))
    phi.append(2.0 * pi * u[i])
    print "\ni: " + `i`
    print "u: " + `u[i]`
    print "v: " + `u[i] + val/2.0`
    print "theta: " + `theta[i]`
    print "phi: " + `phi[i]`


# Generate the vectors:
#
#                 | sin(theta) * cos(phi) |
#      vector  =  | sin(theta) * sin(phi) |
#                 |      cos(theta)       |
#
###########################################

vectors = []
for i in xrange(len(u)):
    for j in xrange(len(u)):
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
for i in xrange(len(vectors)):
    # Test if the vector has already been used.
    if vectors[i] in used:
        print "Vector " + `vectors[i]` + " already used."
        continue

    # Nitrogen line.
    pdb_line(file=file, atom_num=atom_num, atom='N', res_num=res_num, res_name='GLY', vector=[0.0, 0.0, 0.0])

    # Hydrogen line.
    pdb_line(file=file, atom_num=atom_num+1, atom='H', res_num=res_num, res_name='GLY', vector=vectors[i])

    # Increment the atom number and residue number.
    atom_num = atom_num + 2
    res_num = res_num + 1

    # Add the vector to the used vector list.
    used.append(vectors[i])

# End of PDB.
file.write('END\n')
