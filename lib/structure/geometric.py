###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
from math import cos, pi, sin
from numpy import arccos, array, dot, eye, float64, zeros

# relax module imports.
from lib.structure.angles import angles_regular, angles_uniform
from lib.structure.conversion import get_proton_name


def generate_vector_dist(mol=None, res_name=None, res_num=None, chain_id='', centre=zeros(3, float64), R=eye(3), warp=eye(3), limit_check=None, scale=1.0, inc=20, distribution='uniform', debug=False):
    """Generate a uniformly distributed distribution of atoms on a warped sphere.

    The vectors from the function vect_dist_spherical_angles() are used to generate the distribution.  These vectors are rotated to the desired frame using the rotation matrix 'R', then each compressed or stretched by the dot product with the 'warp' matrix.  Each vector is centred and at the head of the vector, a proton is placed.


    @keyword mol:           The molecule container.
    @type mol:              MolContainer instance
    @keyword res_name:      The residue name.
    @type res_name:         str
    @keyword res_num:       The residue number.
    @type res_num:          int
    @keyword chain_id:      The chain identifier.
    @type chain_id:         str
    @keyword centre:        The centre of the distribution.
    @type centre:           numpy array, len 3
    @keyword R:             The optional 3x3 rotation matrix.
    @type R:                3x3 numpy array
    @keyword warp:          The optional 3x3 warping matrix.
    @type warp:             3x3 numpy array
    @keyword limit_check:   A function with determines the limits of the distribution.  It should accept two arguments, the polar angle phi and the azimuthal angle theta, and return True if the point is in the limits or False if outside.
    @type limit_check:      function
    @keyword scale:         The scaling factor to stretch all rotated and warped vectors by.
    @type scale:            float
    @keyword inc:           The number of increments or number of vectors.
    @type inc:              int
    @keyword distribution:  The type of point distribution to use.  This can be 'uniform' or 'regular'.
    @type distribution:     str
    """

    # Initial atom number.
    if len(mol.atom_num) == 0:
        origin_num = 1
    else:
        origin_num = mol.atom_num[-1]+1
    atom_num = origin_num

    # Get the uniform vector distribution.
    print("    Creating the uniform vector distribution.")
    vectors = vect_dist_spherical_angles(inc=inc, distribution=distribution)

    # Get the polar and azimuthal angles for the distribution.
    if distribution == 'uniform':
        phi, theta = angles_uniform(inc)
    else:
        phi, theta = angles_regular(inc)

    # Init the arrays for stitching together.
    edge = zeros(len(theta))
    edge_index = zeros(len(theta), int)
    edge_phi = zeros(len(theta), float64)
    edge_atom = zeros(len(theta))

    # Loop over the radial array of vectors (change in longitude).
    for i in range(len(theta)):
        # Debugging.
        if debug:
            print("i: %s; theta: %s" % (i, theta[i]))

        # Loop over the vectors of the radial array (change in latitude).
        for j in range(len(phi)):
            # Debugging.
            if debug:
                print("%sj: %s; phi: %s" % (" "*4, j, phi[j]))

            # Skip the vector if the point is outside of the limits.
            if limit_check and not limit_check(phi[j], theta[i]):
                if debug:
                    print("%sOut of limits." % (" "*8))
                continue

            # Update the edge for this longitude.
            if not edge[i]:
                edge[i] = 1
                edge_index[i] = j
                edge_phi[i] = phi[j]
                edge_atom[i] = atom_num

                # Debugging.
                if debug:
                    print("%sEdge detected." % (" "*8))
                    print("%sEdge index: %s" % (" "*8, edge_index[i]))
                    print("%sEdge phi pos: %s" % (" "*8, edge_phi[i]))
                    print("%sEdge atom: %s" % (" "*8, edge_atom[i]))

            # Rotate the vector into the frame.
            vector = dot(R, vectors[i + j*len(theta)])

            # Warp the vector.
            vector = dot(warp, vector)

            # Scale the vector.
            vector = vector * scale

            # Position relative to the centre of mass.
            pos = centre + vector

            # Debugging.
            if debug:
                print("%sAdding atom %s." % (" "*8, get_proton_name(atom_num)))

            # Add the vector as a H atom of the TNS residue.
            mol.atom_add(pdb_record='HETATM', atom_num=atom_num, atom_name=get_proton_name(atom_num), res_name=res_name, chain_id=chain_id, res_num=res_num, pos=pos, segment_id=None, element='H')

            # Connect to the previous atom to generate the longitudinal lines (except for the first point).
            if j > edge_index[i]:
                # Debugging.
                if debug:
                    print("%sLongitude line, connecting %s to %s" % (" "*8, get_proton_name(atom_num), get_proton_name(atom_num-1)))

                mol.atom_connect(index1=atom_num-1, index2=atom_num-2)

            # Connect across the radial arrays (to generate the latitudinal lines).
            if i != 0 and j >= edge_index[i-1]:
                # The number of atoms back to the previous longitude.
                num = len(phi) - edge_index[i]

                # Debugging.
                if debug:
                    print("%sLatitude line, connecting %s to %s" % (" "*8, get_proton_name(atom_num), get_proton_name(atom_num-num)))

                mol.atom_connect(index1=atom_num-1, index2=atom_num-1-num)

            # Connect the last radial array to the first (to zip up the geometric object and close the latitudinal lines).
            if i == len(theta)-1 and j >= edge_index[0]:
                # The number of atom in the first longitude line.
                num = origin_num + j - edge_index[0]

                # Debugging.
                if debug:
                    print("%sZipping up, connecting %s to %s" % (" "*8, get_proton_name(atom_num), get_proton_name(num)))

                mol.atom_connect(index1=atom_num-1, index2=num-1)

            # Increment the atom number.
            atom_num = atom_num + 1


def generate_vector_residues(mol=None, vector=None, atom_name=None, res_name_vect='AXS', sim_vectors=None, res_name_sim='SIM', chain_id='', res_num=None, origin=None, scale=1.0, label_placement=1.1, neg=False):
    """Generate residue representations for the vector and the MC simulationed vectors.

    This is used to create a PDB representation of any vector, including its Monte Carlo simulations.

    @keyword mol:               The molecule container.
    @type mol:                  MolContainer instance
    @keyword vector:            The vector to be represented in the PDB.
    @type vector:               numpy array, len 3
    @keyword atom_name:         The atom name used to label the atom representing the head of the vector.
    @type atom_name:            str
    @keyword res_name_vect:     The 3 letter PDB residue code used to represent the vector.
    @type res_name_vect:        str
    @keyword sim_vectors:       The optional Monte Carlo simulation vectors to be represented in the PDB.
    @type sim_vectors:          list of numpy array, each len 3
    @keyword res_name_sim:      The 3 letter PDB residue code used to represent the Monte Carlo simulation vectors.
    @type res_name_sim:         str
    @keyword chain_id:          The chain identification code.
    @type chain_id:             str
    @keyword res_num:           The residue number.
    @type res_num:              int
    @keyword origin:            The origin for the axis.
    @type origin:               numpy array, len 3
    @keyword scale:             The scaling factor to stretch the vectors by.
    @type scale:                float
    @keyword label_placement:   A scaling factor to multiply the pre-scaled vector by.  This is used to place the vector labels a little further out from the vector itself.
    @type label_placement:      float
    @keyword neg:               If True, then the negative vector positioned at the origin will also be included.
    @type neg:                  bool
    @return:                    The new residue number.
    @rtype:                     int
    """

    # The atom numbers (and indices).
    origin_num = len(mol.atom_num)+1
    atom_num = len(mol.atom_num)+2
    atom_neg_num = len(mol.atom_num)+3

    # The origin atom.
    mol.atom_add(pdb_record='HETATM', atom_num=origin_num, atom_name='R', res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin, segment_id=None, element='C')

    # Create the PDB residue representing the vector.
    mol.atom_add(pdb_record='HETATM', atom_num=atom_num, atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin+vector*scale, segment_id=None, element='C')
    mol.atom_connect(index1=atom_num-1, index2=origin_num-1)
    num = 1
    if neg:
        mol.atom_add(pdb_record='HETATM', atom_num=atom_neg_num, atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin-vector*scale, segment_id=None, element='C')
        mol.atom_connect(index1=atom_neg_num-1, index2=origin_num-1)
        num = 2

    # Add another atom to allow the axis labels to be shifted just outside of the vector itself.
    mol.atom_add(pdb_record='HETATM', atom_num=atom_num+num, atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin+label_placement*vector*scale, segment_id=None, element='N')
    if neg:
        mol.atom_add(pdb_record='HETATM', atom_num=atom_neg_num+num, atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin-label_placement*vector*scale, segment_id=None, element='N')

    # Print out.
    print("    " + atom_name + " vector (scaled + shifted to origin): " + repr(origin+vector*scale))
    print("    Creating the MC simulation vectors.")

    # Monte Carlo simulations.
    if sim_vectors != None:
        for i in range(len(sim_vectors)):
            # Increment the residue number, so each simulation is a new residue.
            res_num = res_num + 1

            # The atom numbers (and indices).
            atom_num = mol.atom_num[-1]+1
            atom_neg_num = mol.atom_num[-1]+2

            # Create the PDB residue representing the vector.
            mol.atom_add(pdb_record='HETATM', atom_num=atom_num, atom_name=atom_name, res_name=res_name_sim, chain_id=chain_id, res_num=res_num, pos=origin+sim_vectors[i]*scale, segment_id=None, element='C')
            mol.atom_connect(index1=atom_num-1, index2=origin_num-1)
            if neg:
                mol.atom_add(pdb_record='HETATM', atom_num=atom_num+1, atom_name=atom_name, res_name=res_name_sim, chain_id=chain_id, res_num=res_num, pos=origin-sim_vectors[i]*scale, segment_id=None, element='C')
                mol.atom_connect(index1=atom_neg_num-1, index2=origin_num-1)

    # Return the new residue number.
    return res_num


def vect_dist_spherical_angles(inc=20, distribution='uniform'):
    """Create a distribution of vectors on a sphere using a distribution of spherical angles.

    This function returns an array of unit vectors distributed within 3D space.  The unit vectors are generated using the equation::

                   | cos(theta) * sin(phi) |
        vector  =  | sin(theta) * sin(phi) |.
                   |      cos(phi)         |

    The vectors of this distribution generate both longitudinal and latitudinal lines.


    @keyword inc:           The number of increments in the distribution.
    @type inc:              int
    @keyword distribution:  The type of point distribution to use.  This can be 'uniform' or 'regular'.
    @type distribution:     str
    @return:                The distribution of vectors on a sphere.
    @rtype:                 list of rank-1, 3D numpy arrays
    """

    # Get the polar and azimuthal angles for the distribution.
    if distribution == 'uniform':
        phi, theta = angles_uniform(inc)
    else:
        phi, theta = angles_regular(inc)

    # Initialise array of the distribution of vectors.
    vectors = []

    # Loop over the longitudinal lines.
    for j in range(len(phi)):
        # Loop over the latitudinal lines.
        for i in range(len(theta)):
            # X coordinate.
            x = cos(theta[i]) * sin(phi[j])

            # Y coordinate.
            y =  sin(theta[i])* sin(phi[j])

            # Z coordinate.
            z = cos(phi[j])

            # Append the vector.
            vectors.append(array([x, y, z], float64))

    # Return the array of vectors and angles.
    return vectors
