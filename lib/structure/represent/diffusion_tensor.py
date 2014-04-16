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
from numpy import array, dot, float64, transpose

# relax module imports.
from lib.structure.geometric import generate_vector_dist, generate_vector_residues


def diffusion_tensor(mol=None, tensor=None, tensor_diag=None, diff_type=None, rotation=None, axes=None, sim_axes=None, com=None, scale=1.8e-6):
    """Create the structural representation of the diffusion tensor.

    @keyword mol:           The molecule container.
    @type mol:              MolContainer instance
    @keyword tensor:        The diffusion tensor.
    @type tensor:           numpy rank-2, 3D array
    @keyword tensor_diag:   The diagonalised diffusion tensor in tensor frame.
    @type tensor_diag:      numpy rank-2, 3D array
    @keyword diff_type:     The type of diffusion tensor.  This can be one of 'sphere', 'oblate', 'prolate', 'ellipsoid'.
    @type diff_type:        str
    @keyword rotation:      The diffusion tensor rotation matrix.
    @type rotation:         numpy rank-2, 3D array
    @keyword axes:          The axis system of the tensor.  For the spheroids this is one vector, for the ellipsoid it should be three vectors.
    @type axes:             list of numpy rank-1, 3D arrays
    @keyword sim_axes:      The axis systems of the tensor for each simulation.  For the spheroids this is one vector, for the ellipsoid it should be three vectors.  The first dimension is the axis type (x, y, or z), the second is the simulation, and the third is the vector.
    @type sim_axes:         None or list of lists of numpy rank-1, 3D arrays
    @keyword com:           The centre of mass of the diffusion structure.
    @type com:              numpy rank-1, 3D array
    @keyword scale:         The scaling factor for the diffusion tensor.
    @type scale:            float
    """

    # Initialise.
    #############

    # Initialise the residue number.
    res_num = 1

    # Add the central atom.
    mol.atom_add(pdb_record='HETATM', atom_num=1, atom_name='R', res_name='COM', res_num=res_num, pos=com, segment_id=None, element='C')

    # Increment the residue number.
    res_num = res_num + 1


    # Vector distribution.
    ######################

    # Print out.
    print("\nGenerating the geometric object.")

    # Swap the x and z axes for the oblate spheroid (the vector distributions are centred on the z-axis).
    if diff_type == 'oblate':
        # 90 deg rotation about the diffusion frame y-axis.
        y_rot = array([[  0, 0,  1],
                       [  0, 1,  0],
                       [ -1, 0,  0]], float64)

        # Rotate the tensor and rotation matrix.
        rotation = dot(transpose(rotation), y_rot)
        tensor = dot(y_rot, dot(tensor_diag, transpose(y_rot)))
        tensor = dot(rotation, dot(tensor, transpose(rotation)))

    # The distribution.
    generate_vector_dist(mol=mol, res_name='TNS', res_num=res_num, centre=com, R=rotation, warp=tensor, scale=scale, inc=20)

    # Increment the residue number.
    res_num = res_num + 1


    # Axes of the tensor.
    #####################

    # Create the unique axis of the spheroid.
    if diff_type in ['oblate', 'prolate']:
        # Print out.
        print("\nGenerating the unique axis of the diffusion tensor.")
        print("    Scaling factor:                      " + repr(scale))

        # Generate the axes representation.
        res_num = generate_vector_residues(mol=mol, vector=axes[0], atom_name='Dpar', res_name_vect='AXS', sim_vectors=sim_axes[0], res_num=res_num, origin=com, scale=scale, neg=True)


    # Create the three axes of the ellipsoid.
    if diff_type == 'ellipsoid':
        # Print out.
        print("Generating the three axes of the ellipsoid.")
        print("    Scaling factor:                      " + repr(scale))

        # Generate the axes representation.
        res_num = generate_vector_residues(mol=mol, vector=axes[0], atom_name='Dx', res_name_vect='AXS', sim_vectors=sim_axes[0], res_num=res_num, origin=com, scale=scale, neg=True)
        res_num = generate_vector_residues(mol=mol, vector=axes[1], atom_name='Dy', res_name_vect='AXS', sim_vectors=sim_axes[1], res_num=res_num, origin=com, scale=scale, neg=True)
        res_num = generate_vector_residues(mol=mol, vector=axes[2], atom_name='Dz', res_name_vect='AXS', sim_vectors=sim_axes[2], res_num=res_num, origin=com, scale=scale, neg=True)
