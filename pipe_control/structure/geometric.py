###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
from numpy import arccos, array, dot, eye, float64, transpose, zeros
from os import getcwd
from string import ascii_uppercase
from warnings import warn

# relax module imports.
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import exists_mol_res_spin_data, return_spin
from pipe_control import pipes
from pipe_control.structure.mass import pipe_centre_of_mass
from lib.geometry.rotations import two_vect_to_R
from lib.errors import RelaxNoPdbError, RelaxNoSequenceError, RelaxNoTensorError, RelaxNoVectorsError
from lib.io import get_file_path, open_write_file
from lib.structure.internal.object import Internal
from lib.structure.represent.rotor import rotor_pdb
from lib.warnings import RelaxWarning
from status import Status; status = Status()


def angles_regular(inc=None):
    """Determine the spherical angles for a regular sphere point distribution.

    @keyword inc:   The number of increments in the distribution.
    @type inc:      int
    @return:        The phi angle array and the theta angle array.
    @rtype:         array of float, array of float
    """

    # Generate the increment values of u.
    u = zeros(inc, float64)
    val = 1.0 / float(inc)
    for i in range(inc):
        u[i] = float(i) * val

    # Generate the increment values of v.
    v = zeros(inc/2+1, float64)
    val = 1.0 / float(inc/2)
    for i in range(int(inc/2+1)):
        v[i] = float(i) * val

    # Generate the distribution of spherical angles theta.
    theta = 2.0 * pi * u

    # Generate the distribution of spherical angles phi (from bottom to top).
    phi = zeros(len(v), float64)
    for i in range(len(v)):
        phi[len(v)-1-i] = pi * v[i]

    # Return the angle arrays.
    return phi, theta


def angles_uniform(inc=None):
    """Determine the spherical angles for a uniform sphere point distribution.

    @keyword inc:   The number of increments in the distribution.
    @type inc:      int
    @return:        The phi angle array and the theta angle array.
    @rtype:         array of float, array of float
    """

    # Generate the increment values of u.
    u = zeros(inc, float64)
    val = 1.0 / float(inc)
    for i in range(inc):
        u[i] = float(i) * val

    # Generate the increment values of v.
    v = zeros(inc/2+2, float64)
    val = 1.0 / float(inc/2)
    for i in range(1, int(inc/2)+1):
        v[i] = float(i-1) * val + val/2.0
    v[-1] = 1.0

    # Generate the distribution of spherical angles theta.
    theta = 2.0 * pi * u

    # Generate the distribution of spherical angles phi.
    phi = arccos(2.0 * v - 1.0)

    # Return the angle arrays.
    return phi, theta


def create_rotor_pdb(file=None, dir=None, rotor_angle=None, axis=None, axis_pt=True, centre=None, span=2e-9, blade_length=5e-10, force=False, staggered=False):
    """Create a PDB representation of a rotor motional model.

    @keyword file:          The name of the PDB file to create.
    @type file:             str
    @keyword dir:           The name of the directory to place the PDB file into.
    @type dir:              str
    @keyword rotor_angle:   The angle of the rotor motion in degrees.
    @type rotor_angle:      float
    @keyword axis:          The vector defining the rotor axis.
    @type axis:             numpy rank-1, 3D array
    @keyword axis_pt:       A point lying anywhere on the rotor axis.  This is used to define the position of the axis in 3D space.
    @type axis_pt:          numpy rank-1, 3D array
    @keyword centre:        The central point of the representation.  If this point is not on the rotor axis, then the closest point on the axis will be used for the centre.
    @type centre:           numpy rank-1, 3D array
    @keyword span:          The distance from the central point to the rotor blades (meters).
    @type span:             float
    @keyword blade_length:  The length of the representative rotor blades.
    @type blade_length:     float
    @keyword force:         A flag which if set will overwrite any pre-existing file.
    @type force:            bool
    @keyword staggered:     A flag which if True will cause the rotor blades to be staggered.  This is used to avoid blade overlap.
    @type staggered:        bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Convert the angle to radians.
    rotor_angle = rotor_angle / 360.0 * 2.0 * pi

    # Create the structural object.
    structure = Internal()

    # Generate the rotor object.
    rotor_pdb(structure=structure, rotor_angle=rotor_angle, axis=axis, axis_pt=axis_pt, centre=centre, span=span, blade_length=blade_length, staggered=staggered)

    # Print out.
    print("\nGenerating the PDB file.")

    # Open the PDB file for writing.
    tensor_pdb_file = open_write_file(file, dir, force=force)

    # Write the data.
    structure.write_pdb(tensor_pdb_file)

    # Close the file.
    tensor_pdb_file.close()

    # Add the file to the results file list.
    if not hasattr(cdp, 'result_files'):
        cdp.result_files = []
    if dir == None:
        dir = getcwd()
    cdp.result_files.append(['rotor_pdb', 'Rotor PDB', get_file_path(file, dir)])
    status.observers.result_file.notify()


def create_vector_dist(length=None, symmetry=True, file=None, dir=None, force=False):
    """Create a PDB representation of the vector distribution.

    @keyword length:    The length to set the vectors to in the PDB file.
    @type length:       float
    @keyword symmetry:  The symmetry flag which if set will create a second PDB chain 'B' which is the same as chain 'A' but with the vectors reversed.
    @type symmetry:     bool
    @keyword file:      The name of the PDB file to create.
    @type file:         str
    @keyword dir:       The name of the directory to place the PDB file into.
    @type dir:          str
    @keyword force:     Flag which if set will overwrite any pre-existing file.
    @type force:        bool
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if a structure has been loaded.
    if not hasattr(cdp, 'structure') or not cdp.structure.num_models() > 0:
        raise RelaxNoPdbError

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if unit vectors exist.
    vectors = False
    for interatom in interatomic_loop():
        if hasattr(interatom, 'vector'):
            vectors = True
            break
    if not vectors:
        raise RelaxNoVectorsError


    # Initialise.
    #############

    # Create the structural object.
    structure = Internal()

    # Add a structure.
    structure.add_molecule(name='vector_dist')

    # Alias the single molecule from the single model.
    mol = structure.structural_data[0].mol[0]

    # Initialise the residue and atom numbers.
    res_num = 1
    atom_num = 1


    # Centre of mass.
    #################

    # Calculate the centre of mass.
    R = pipe_centre_of_mass()

    # Increment the residue number.
    res_num = res_num + 1


    # The vectors.
    ##############

    # Loop over the interatomic data containers.
    for interatom in interatomic_loop():
        # Get the spins.
        spin1 = return_spin(interatom.spin_id1)
        spin2 = return_spin(interatom.spin_id2)

        # Skip deselected spin systems.
        if not spin1.select or not spin2.select:
            continue

        # Skip containers missing vectors.
        if not hasattr(interatom, 'vector'):
            continue

        # Scale the vector.
        vector = interatom.vector * length * 1e10

        # Add the first spin as the central atom.
        mol.atom_add(pdb_record='ATOM', atom_num=atom_num, atom_name=spin1.name, res_name=spin1._res_name, chain_id='A', res_num=spin1._res_num, pos=R, segment_id=None, element=spin1.element)

        # Add the second spin as the end atom.
        mol.atom_add(pdb_record='ATOM', atom_num=atom_num+1, atom_name=spin2.name, res_name=spin2._res_name, chain_id='A', res_num=spin2._res_num, pos=R+vector, segment_id=None, element=spin2.element)

        # Connect the two atoms.
        mol.atom_connect(index1=atom_num-1, index2=atom_num)

        # Increment the atom number.
        atom_num = atom_num + 2

    # Symmetry chain.
    if symmetry:
        # Loop over the interatomic data containers.
        for interatom in interatomic_loop():
            # Get the spins.
            spin1 = return_spin(interatom.spin_id1)
            spin2 = return_spin(interatom.spin_id2)

            # Skip deselected spin systems.
            if not spin1.select or not spin2.select:
                continue

            # Skip containers missing vectors.
            if not hasattr(interatom, 'vector'):
                continue

            # Scale the vector.
            vector = interatom.vector * length * 1e10

            # Add the first spin as the central atom.
            mol.atom_add(pdb_record='ATOM', atom_num=atom_num, atom_name=spin1.name, res_name=spin1._res_name, chain_id='B', res_num=spin1._res_num, pos=R, segment_id=None, element=spin1.element)

            # Add the second spin as the end atom.
            mol.atom_add(pdb_record='ATOM', atom_num=atom_num+1, atom_name=spin2.name, res_name=spin2._res_name, chain_id='B', res_num=spin2._res_num, pos=R-vector, segment_id=None, element=spin2.element)

            # Connect the two atoms.
            mol.atom_connect(index1=atom_num-1, index2=atom_num)

            # Increment the atom number.
            atom_num = atom_num + 2


    # Create the PDB file.
    ######################

    # Print out.
    print("\nGenerating the PDB file.")

    # Open the PDB file for writing.
    tensor_pdb_file = open_write_file(file, dir, force=force)

    # Write the data.
    structure.write_pdb(tensor_pdb_file)

    # Close the file.
    tensor_pdb_file.close()

    # Add the file to the results file list.
    if not hasattr(cdp, 'result_files'):
        cdp.result_files = []
    if dir == None:
        dir = getcwd()
    cdp.result_files.append(['vector_dist_pdb', 'Vector distribution PDB', get_file_path(file, dir)])
    status.observers.result_file.notify()


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
    origin_num = mol.atom_num[-1]+1
    atom_num = mol.atom_num[-1]+2
    atom_neg_num = mol.atom_num[-1]+3

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


def get_proton_name(atom_num):
    """Return a valid PDB atom name of <4 characters.

    @param atom_num:    The number of the atom.
    @type atom_num:     int
    @return:            The atom name to use in the PDB.
    @rtype:             str
    """

    # Init the proton first letters and the atom number folding limits.
    names = ['H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q']
    lims = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]

    # Loop over the proton names.
    for i in range(len(names)):
        # In the bounds.
        if atom_num >= lims[i] and atom_num < lims[i+1]:
            return names[i] + repr(atom_num - lims[i])


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
