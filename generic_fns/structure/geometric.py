###############################################################################
#                                                                             #
# Copyright (C) 2003-2009 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Python module imports.
from math import cos, pi, sin
from numpy import arccos, array, dot, eye, float64, zeros
from string import ascii_uppercase
from warnings import warn

# relax module imports.
from generic_fns.mol_res_spin import exists_mol_res_spin_data, spin_loop
from generic_fns import pipes
from generic_fns.structure.mass import centre_of_mass
from internal import Internal
from maths_fns.rotation_matrix import two_vect_to_R
from relax_errors import RelaxError, RelaxNoPdbError, RelaxNoSequenceError, RelaxNoTensorError, RelaxNoVectorsError
from relax_io import open_write_file
from relax_warnings import RelaxWarning



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
    for i in xrange(inc):
        u[i] = float(i) * val

    # Generate the increment values of v.
    v = zeros(inc/2+2, float64)
    val = 1.0 / float(inc/2)
    for i in xrange(1, inc/2+1):
        v[i] = float(i-1) * val + val/2.0
    v[-1] = 1.0

    # Generate the distribution of spherical angles theta.
    theta = 2.0 * pi * u

    # Generate the distribution of spherical angles phi.
    phi = arccos(2.0 * v - 1.0)

    # Return the angle arrays.
    return phi, theta


def autoscale_tensor(method='mass'):
    """Automatically determine an appropriate scaling factor for display of the diffusion tensor.

    @param method:  The method used to determine the scaling of the diffusion tensor object.
    @type method:   str
    @return:        The scaling factor.
    @rtype:         float
    """

    # Centre of mass method.
    if method == 'mass':
        com, mass = centre_of_mass(return_mass=True)
        scale = mass * 6.8e-11
        return scale

    # Autoscaling method.
    warn(RelaxWarning("Autoscale method %s not implimented. Reverting to scale=1.8e-6 A.s" % method))
    return 1.8e-6


def cone_edge(mol=None, res_name='CON', res_num=None, apex=None, axis=None, R=None, phi_max_fn=None, length=None, inc=None):
    """Add a residue to the atomic data representing a cone of the given angle.

    A series of vectors totalling the number of increments and starting at the origin are equally
    spaced around the cone axis.  The atoms representing neighbouring vectors will be directly
    bonded together.  This will generate an object representing the outer edge of a cone.


    @keyword mol:           The molecule container.
    @type mol:              MolContainer instance
    @keyword res_name:      The residue name.
    @type res_name:         str
    @keyword res_num:       The residue number.
    @type res_num:          int
    @keyword apex:          The apex of the cone.
    @type apex:             numpy array, len 3
    @keyword axis:          The central axis of the cone.  If supplied, then this arg will be used
                            to construct the rotation matrix.
    @type axis:             numpy array, len 3
    @keyword R:             A 3x3 rotation matrix.  If the axis arg supplied, then this matrix will
                            be ignored.
    @type R:                3x3 numpy array
    @keyword phi_max_fn:    A function which returns the maximum polar angle for the given azimuthal angle.
    @type phi_max_fn:       function
    @keyword length:        The cone length in meters.
    @type length:           float
    @keyword inc:           The number of increments or number of vectors used to generate the outer
                            edge of the cone.
    @type inc:              int
    """

    # The atom numbers (and indices).
    atom_num = mol.atom_num[-1]+1

    # Add an atom for the cone apex.
    mol.atom_add(pdb_record='HETATM', atom_num=atom_num, atom_name='APX', res_name=res_name, res_num=res_num, pos=apex, segment_id=None, element='H')
    origin_atom = atom_num

    # Initialise the rotation matrix.
    if R == None:
        R = eye(3)

    # Get the rotation matrix.
    if axis != None:
        two_vect_to_R(array([0, 0, 1], float64), axis, R)

    # Loop over each vector.
    for i in xrange(inc):
        # Increment the atom number.
        atom_num = atom_num + 1

        # The azimuthal angle theta.
        theta = 2.0 * pi * float(i) / float(inc)

        # Get the polar angle.
        phi = phi_max_fn(theta)

        # X coordinate.
        x = cos(theta) * sin(phi)

        # Y coordinate.
        y = sin(theta)* sin(phi)

        # Z coordinate.
        z = cos(phi)

        # The vector in the unrotated frame.
        vector = array([x, y, z], float64)

        # Rotate the vector.
        vector = dot(R, vector)

        # The atom id.
        atom_id = 'T' + repr(i)

        # The atom position.
        pos = apex+vector*length

        # Add the vector as a H atom of the cone residue.
        mol.atom_add(pdb_record='HETATM', atom_num=atom_num, atom_name=get_proton_name(atom_num), res_name=res_name, res_num=res_num, pos=pos, segment_id=None, element='H')

        # Connect across the radial array (to generate the circular cone edge).
        if i != 0:
            mol.atom_connect(index1=atom_num-1, index2=atom_num-2)

        # Connect the last radial array to the first (to zip up the circle).
        if i == inc-1:
            mol.atom_connect(index1=atom_num-1, index2=origin_atom)

        # Join the atom to the cone apex.
        mol.atom_connect(index1=origin_atom-1, index2=atom_num-1)


def create_diff_tensor_pdb(scale=1.8e-6, file=None, dir=None, force=False):
    """Create the PDB representation of the diffusion tensor.

    @param scale:   The scaling factor for the diffusion tensor.
    @type scale:    float
    @param file:    The name of the PDB file to create.
    @type file:     str
    @param dir:     The name of the directory to place the PDB file into.
    @type dir:      str
    @param force:   Flag which if set to True will overwrite any pre-existing file.
    @type force:    bool
    """

    # Arguments.
    if scale == 'mass':
        scale = autoscale_tensor(scale)

    # Test if the current data pipe exists.
    pipes.test()

    # Create an array of data pipes to loop over (hybrid support).
    if cdp.pipe_type == 'hybrid':
        pipe_list = cdp.hybrid_pipes
    else:
        pipe_list = [pipes.cdp_name()]

    # Create the structural object.
    structure = Internal()

    # Add a structure.
    structure.add_molecule(name='diff_tensor')

    # Alias the single molecule from the single model.
    mol = structure.structural_data[0].mol[0]

    # Loop over the pipes.
    for pipe_index in xrange(len(pipe_list)):
        # Get the pipe container.
        pipe = pipes.get_pipe(pipe_list[pipe_index])


        # Tests.
        ########

        # Test if the diffusion tensor data is loaded.
        if not hasattr(pipe, 'diff_tensor'):
            raise RelaxNoTensorError('diffusion')

        # Test if a structure has been loaded.
        if not hasattr(cdp, 'structure'):
            raise RelaxNoPdbError

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError


        # Initialise.
        #############

        # Initialise the residue number.
        res_num = 1

        # The chain identifier.
        chain_id = ascii_uppercase[pipe_index]

        # Atom ID extension (allow for multiple chains for hybrid data pipes).
        atom_id_ext = '_' + chain_id

        # Print out.
        print(("\nChain " + chain_id + "\n"))


        # Centre of mass.
        #################

        # Calculate the centre of mass.
        CoM = centre_of_mass()

        # Add the central atom.
        mol.atom_add(pdb_record='HETATM', atom_num=1, atom_name='R'+atom_id_ext, res_name='COM', chain_id=chain_id, res_num=res_num, pos=CoM, segment_id=None, element='C')

        # Increment the residue number.
        res_num = res_num + 1


        # Vector distribution.
        ######################

        # Print out.
        print("\nGenerating the geometric object.")

        # The distribution.
        generate_vector_dist(mol=mol, res_name='TNS', res_num=res_num, chain_id=chain_id, centre=CoM, R=pipe.diff_tensor.rotation, warp=pipe.diff_tensor.tensor, scale=scale, inc=20)

        # Increment the residue number.
        res_num = res_num + 1


        # Axes of the tensor.
        #####################

        # Create the unique axis of the spheroid.
        if pipe.diff_tensor.type == 'spheroid':
            # Print out.
            print("\nGenerating the unique axis of the diffusion tensor.")
            print(("    Scaling factor:                      " + repr(scale)))

            # Simulations.
            if hasattr(pipe.diff_tensor, 'tm_sim'):
                sim_vectors = []
                for i in range(len(pipe.diff_tensor.tm_sim)):
                    sim_vectors.append(pipe.diff_tensor.Dpar_sim[i] * pipe.diff_tensor.Dpar_unit_sim[i])
            else:
                sim_vectors = None

            # Generate the axes representation.
            res_num = generate_vector_residues(mol=mol, vector=pipe.diff_tensor.Dpar*pipe.diff_tensor.Dpar_unit, atom_name='Dpar', res_name_vect='AXS', sim_vectors=sim_vectors, chain_id=chain_id, res_num=res_num, origin=CoM, scale=scale, neg=True)


        # Create the three axes of the ellipsoid.
        if pipe.diff_tensor.type == 'ellipsoid':
            # Print out.
            print("Generating the three axes of the ellipsoid.")
            print(("    Scaling factor:                      " + repr(scale)))

            # Simulations.
            if hasattr(pipe.diff_tensor, 'tm_sim'):
                sim_Dx_vectors = []
                sim_Dy_vectors = []
                sim_Dz_vectors = []
                for i in range(len(pipe.diff_tensor.tm_sim)):
                    sim_Dx_vectors.append(pipe.diff_tensor.Dx_sim[i] * pipe.diff_tensor.Dx_unit_sim[i])
                    sim_Dy_vectors.append(pipe.diff_tensor.Dy_sim[i] * pipe.diff_tensor.Dy_unit_sim[i])
                    sim_Dz_vectors.append(pipe.diff_tensor.Dz_sim[i] * pipe.diff_tensor.Dz_unit_sim[i])
            else:
                sim_Dx_vectors = None
                sim_Dy_vectors = None
                sim_Dz_vectors = None

            # Generate the axes representation.
            res_num = generate_vector_residues(mol=mol, vector=pipe.diff_tensor.Dx*pipe.diff_tensor.Dx_unit, atom_name='Dx', res_name_vect='AXS', sim_vectors=sim_Dx_vectors, chain_id=chain_id, res_num=res_num, origin=CoM, scale=scale, neg=True)
            res_num = generate_vector_residues(mol=mol, vector=pipe.diff_tensor.Dy*pipe.diff_tensor.Dy_unit, atom_name='Dy', res_name_vect='AXS', sim_vectors=sim_Dy_vectors, chain_id=chain_id, res_num=res_num, origin=CoM, scale=scale, neg=True)
            res_num = generate_vector_residues(mol=mol, vector=pipe.diff_tensor.Dz*pipe.diff_tensor.Dz_unit, atom_name='Dz', res_name_vect='AXS', sim_vectors=sim_Dz_vectors, chain_id=chain_id, res_num=res_num, origin=CoM, scale=scale, neg=True)


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


def create_vector_dist(length=None, symmetry=True, file=None, dir=None, force=False):
    """Create a PDB representation of the XH vector distribution.

    @param length:      The length to set the vectors to in the PDB file.
    @type length:       float
    @param symmetry:    The symmetry flag which if set will create a second PDB chain 'B' which
        is the same as chain 'A' but with the XH vectors reversed.
    @type symmetry:     bool
    @param file:        The name of the PDB file to create.
    @type file:         str
    @param dir:         The name of the directory to place the PDB file into.
    @type dir:          str
    @param force:       Flag which if set will overwrite any pre-existing file.
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
    vectors = 0
    for spin in spin_loop():
        if hasattr(spin, 'xh_vect'):
            vectors = 1
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
    R = centre_of_mass()

    # Increment the residue number.
    res_num = res_num + 1


    # The XH vectors.
    #################

    # Loop over the spin systems.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Skip deselected spin systems.
        if not spin.select:
            continue

        # Skip spin systems missing the xh_vect structure.
        if not hasattr(spin, 'xh_vect'):
            continue

        # Scale the vector.
        vector = spin.xh_vect * length * 1e10

        # Add the central X atom.
        mol.atom_add(pdb_record='ATOM', atom_num=atom_num, atom_name=spin.name, res_name=res_name, chain_id='A', res_num=res_num, pos=R, segment_id=None, element=spin.element)

        # Add the H atom.
        mol.atom_add(pdb_record='ATOM', atom_num=atom_num+1, atom_name='H', res_name=res_name, chain_id='A', res_num=res_num, pos=R+vector, segment_id=None, element='H')

        # Connect the two atoms.
        mol.atom_connect(index1=atom_num-1, index2=atom_num)

        # Increment the atom number.
        atom_num = atom_num + 2

    # Symmetry chain.
    if symmetry:
        # Loop over the spin systems.
        for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
            # Skip deselected spin systems.
            if not spin.select:
                continue

            # Skip spin systems missing the xh_vect structure.
            if not hasattr(spin, 'xh_vect'):
                continue

            # Scale the vector.
            vector = spin.xh_vect * length * 1e10

            # Add the central X atom.
            mol.atom_add(pdb_record='ATOM', atom_num=atom_num, atom_name=spin.name, res_name=res_name, chain_id='B', res_num=res_num, pos=R, segment_id=None, element=spin.element)

            # Add the H atom.
            mol.atom_add(pdb_record='ATOM', atom_num=atom_num+1, atom_name='H', res_name=res_name, chain_id='B', res_num=res_num, pos=R-vector, segment_id=None, element='H')

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


def generate_vector_dist(mol=None, res_name=None, res_num=None, chain_id='', centre=zeros(3, float64), R=eye(3), warp=eye(3), limit_check=None, scale=1.0, inc=20, debug=False):
    """Generate a uniformly distributed distribution of atoms on a warped sphere.

    The vectors from the function uniform_vect_dist_spherical_angles() are used to generate the
    distribution.  These vectors are rotated to the desired frame using the rotation matrix 'R',
    then each compressed or stretched by the dot product with the 'warp' matrix.  Each vector is
    centred and at the head of the vector, a proton is placed.


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
    @keyword inc:           The number of increments or number of vectors used to generate the outer
                            edge of the cone.
    @type inc:              int
    """

    # Initial atom number.
    origin_num = mol.atom_num[-1]+1
    atom_num = origin_num

    # Get the uniform vector distribution.
    print("    Creating the uniform vector distribution.")
    vectors = uniform_vect_dist_spherical_angles(inc=inc)

    # Get the polar and azimuthal angles for the distribution.
    phi, theta = angles_uniform(inc)

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
            if not limit_check(phi[j], theta[i]):
                if debug:
                    print("%sOut of cone." % (" "*8))
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

            # Rotate the vector into the diffusion frame.
            vector = dot(R, vectors[i + j*len(theta)])

            # Set the length of the vector to its diffusion rate within the diffusion tensor geometric object.
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

    This is used to create a PDB representation of any vector, including its Monte Carlo
    simulations.

    @keyword mol:           The molecule container.
    @type mol:              MolContainer instance
    @param vector:          The vector to be represented in the PDB.
    @type vector:           numpy array, len 3
    @param atom_name:       The atom name used to label the atom representing the head of the
                            vector.
    @type atom_name:        str
    @param res_name_vect:   The 3 letter PDB residue code used to represent the vector.
    @type res_name_vect:    str
    @param sim_vectors:     The optional Monte Carlo simulation vectors to be represented in the
                            PDB.
    @type sim_vectors:      list of numpy array, each len 3
    @param res_name_sim:    The 3 letter PDB residue code used to represent the Monte Carlo
                            simulation vectors.
    @type res_name_sim:     str
    @param chain_id:        The chain identification code.
    @type chain_id:         str
    @param res_num:         The residue number.
    @type res_num:          int
    @param origin:          The origin for the axis.
    @type origin:           numpy array, len 3
    @param scale:           The scaling factor to stretch the vectors by.
    @type scale:            float
    @param label_placement: A scaling factor to multiply the pre-scaled vector by.  This is used to
                            place the vector labels a little further out from the vector itself.
    @type label_placement:  float
    @param neg:             If True, then the negative vector positioned at the origin will also be
                            included.
    @type neg:              bool
    @return:                The new residue number.
    @rtype:                 int
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
    print(("    " + atom_name + " vector (scaled + shifted to origin): " + repr(origin+vector*scale)))
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


def stitch_cone_to_edge(mol=None, cone_start=None, edge_start=None, max_angle=None, inc=None, debug=False):
    """Function for stitching the cone dome to its edge, in the PDB representations.

    @keyword mol:           The molecule container.
    @type mol:              MolContainer instance
    @keyword cone_start:    The starting atom number of the cone dome residue.
    @type cone_start:       int
    @keyword edge_start:    The starting atom number of the cone edge residue.
    @type edge_start:       int
    @keyword max_angle:     The maximal polar angle, in rad, after which all vectors are skipped.
    @type max_angle:        float
    @keyword inc:           The number of increments or number of vectors used to generate the outer
                            edge of the cone.
    @type inc:              int
    """

    # Get the polar and azimuthal angles for the distribution.
    phi, theta = angles_uniform(inc)

    # Loop over the angles and find the minimum latitudinal index.
    for j_min in xrange(len(phi)):
        if phi[j_min] < max_angle:
            break

    # The number of j increments.
    num_j = inc/2+2 - j_min

    # Loop over the radial array of vectors (change in longitude).
    for i in range(inc):
        # Cone edge atom.
        edge_atom = edge_start + i

        # Dome edge atom.
        dome_edge = cone_start + i*num_j

        # Connect the two atoms (to stitch up the 2 objects).
        mol.atom_connect(index1=dome_edge-1, index2=edge_atom-1)


def uniform_vect_dist_spherical_angles(inc=20):
    """Uniform distribution of vectors on a sphere using uniform spherical angles.

    This function returns an array of unit vectors uniformly distributed within 3D space.  To create the distribution, uniform spherical angles are used.  The two spherical angles are defined as::

        theta = 2.pi.u,
        phi = cos^-1(2v - 1),

    where::

        u in [0, 1),
        v in [0, 1].

    Because theta is defined between [0, pi] and phi is defined between [0, 2pi], for a uniform distribution u is only incremented half of 'inc'.  The unit vectors are generated using the equation::

                   | cos(theta) * sin(phi) |
        vector  =  | sin(theta) * sin(phi) |.
                   |      cos(phi)         |

    The vectors of this distribution generate both longitudinal and latitudinal lines.


    @keyword inc:   The number of increments in the distribution.
    @type inc:      int
    @return:        The distribution of vectors on a sphere.
    @rtype:         list of rank-1, 3D numpy arrays, array of float, array of float
    """

    # The inc argument must be an even number.
    if inc%2:
        raise RelaxError("The increment value of " + repr(inc) + " must be an even number.")

    # Get the polar and azimuthal angles for the distribution.
    phi, theta = angles_uniform(inc)

    # Initialise array of the distribution of vectors.
    vectors = []

    # Loop over the longitudinal lines.
    for j in xrange(len(phi)):
        # Loop over the latitudinal lines.
        for i in xrange(len(theta)):
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
