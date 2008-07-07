###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import exists_mol_res_spin_data
from generic_fns.structure.mass import centre_of_mass
from internal import Internal
from maths_fns.rotation_matrix import R_2vect
from relax_errors import RelaxError, RelaxNoPdbError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoTensorError, RelaxNoVectorsError
from relax_io import open_write_file
from relax_warnings import RelaxWarning



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


def cone_edge(structure=None, res_name='CON', res_num=None, apex=None, axis=None, R=None, angle=None, length=None, inc=None):
    """Add a residue to the atomic data representing a cone of the given angle.

    A series of vectors totalling the number of increments and starting at the origin are equally
    spaced around the cone axis.  The atoms representing neighbouring vectors will be directly
    bonded together.  This will generate an object representing the outer edge of a cone.


    @param structure:       The structural data object.
    @type structure:        instance of class derived from Base_struct_API
    @param res_name:        The residue name.
    @type res_name:         str
    @param res_num:         The residue number.
    @type res_num:          int
    @param apex:            The apex of the cone.
    @type apex:             numpy array, len 3
    @param axis:            The central axis of the cone.  If supplied, then this arg will be used
                            to construct the rotation matrix.
    @type axis:             numpy array, len 3
    @param R:               A 3x3 rotation matrix.  If the axis arg supplied, then this matrix will
                            be ignored.
    @type R:                3x3 numpy array
    @param angle:           The cone angle in radians.
    @type angle:            float
    @param length:          The cone length in meters.
    @type length:           float
    @param inc:             The number of increments or number of vectors used to generate the outer
                            edge of the cone.
    @type inc:              int
    """

    # Add an atom for the cone apex.
    structure.atom_add(pdb_record='HETATM', atom_num=Apex, atom_name='APX', res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=apex, segment_id=None, element='H', struct_index=None)

    # Initialise the rotation matrix, atom number, etc.
    if R == None:
        R = eye(3)
    atom_num = 1

    # Get the rotation matrix.
    if axis != None:
        R_2vect(R, array([0,0,1], float64), axis)

    # Loop over each vector.
    for i in xrange(inc):
        # The azimuthal angle theta.
        theta = 2.0 * pi * float(i) / float(inc)

        # X coordinate.
        x = cos(theta) * sin(angle)

        # Y coordinate.
        y = sin(theta)* sin(angle)

        # Z coordinate.
        z = cos(angle)

        # The vector in the unrotated frame.
        vector = array([x, y, z], float64)

        # Rotate the vector.
        vector = dot(R, vector)

        # The atom id.
        atom_id = 'T' + `i`

        # The atom position.
        pos = apex+vector*length

        # Add the vector as a H atom of the cone residue.
        structure.atom_add(pdb_record='HETATM', atom_num=atom_id, atom_name='H'+`atom_num`, res_name=res_name, chain_id=chain_id, res_num=res_num, pos=pos, segment_id=None, element='H', struct_index=None)

        # Connect across the radial array (to generate the circular cone edge).
        if i != 0:
            neighbour_id = 'T' + `i-1`
            structure.atom_connect(atom_id=atom_id, bonded_id=neighbour_id)

        # Connect the last radial array to the first (to zip up the circle).
        if i == inc-1:
            neighbour_id = 'T' + `0`
            structure.atom_connect(atom_id=atom_id, bonded_id=neighbour_id)

        # Join the atom to the cone apex.
        structure.atom_connect(atom_id=atom_id, bonded_id='Apex')

        # Increment the atom number.
        atom_num = atom_num + 1


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
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = ds[ds.current_pipe]

    # Create an array of data pipes to loop over (hybrid support).
    if cdp.pipe_type == 'hybrid':
        pipes = cdp.hybrid_pipes
    else:
        pipes = [ds.current_pipe]

    # Create the structural object.
    structure = Internal()

    # Loop over the pipes.
    for pipe_index in xrange(len(pipes)):
        # Alias the pipe container.
        pipe = ds[pipes[pipe_index]]


        # Tests.
        ########

        # Test if the diffusion tensor data is loaded.
        if not hasattr(pipe, 'diff_tensor'):
            raise RelaxNoTensorError, 'diffusion'

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

        # Atom ID extension (allow for multiple chains for hybrid runs).
        atom_id_ext = '_' + chain_id

        # Print out.
        print "\nChain " + chain_id + "\n"


        # Centre of mass.
        #################

        # Calculate the centre of mass.
        CoM = centre_of_mass()

        # Add the central atom.
        structure.atom_add(pdb_record='HETATM', atom_num=None, atom_name='R'+atom_id_ext, res_name='COM', chain_id=chain_id, res_num=res_num, pos=CoM, segment_id=None, element='C', struct_index=None)

        # Increment the residue number.
        res_num = res_num + 1


        # Vector distribution.
        ######################

        # Print out.
        print "\nGenerating the geometric object."

        # The distribution.
        generate_vector_dist(structure=structure, atom_id_ext=atom_id_ext, res_name='TNS', res_num=res_num, chain_id=chain_id, centre=CoM, R=pipe.diff_tensor.rotation, warp=pipe.diff_tensor.tensor, scale=scale, inc=20)

        # Increment the residue number.
        res_num = res_num + 1


        # Axes of the tensor.
        #####################

        # Create the unique axis of the spheroid.
        if pipe.diff_tensor.type == 'spheroid':
            # Print out.
            print "\nGenerating the unique axis of the diffusion tensor."
            print "    Scaling factor:                      " + `scale`

            # Simulations.
            if hasattr(pipe.diff_tensor, 'tm_sim'):
                sim_vectors = pipe.diff_tensor.Dpar_sim * pipe.diff_tensor.Dpar_unit_sim
            else:
                sim_vectors = None
                
            # Generate the axes representation.
            res_num = generate_vector_residues(structure=structure, vector=pipe.diff_tensor.Dpar*pipe.diff_tensor.Dpar_unit, atom_name='Dpar', res_name_vect='AXS', sim_vectors=sim_vectors, chain_id=chain_id, res_num=res_num, origin=R, scale=scale, neg=True)


        # Create the three axes of the ellipsoid.
        if pipe.diff_tensor.type == 'ellipsoid':
            # Print out.
            print "Generating the three axes of the ellipsoid."
            print "    Scaling factor:                      " + `scale`

            # Simulations.
            if hasattr(pipe.diff_tensor, 'tm_sim'):
                sim_Dx_vectors = pipe.diff_tensor.Dx_sim * pipe.diff_tensor.Dx_unit_sim
                sim_Dy_vectors = pipe.diff_tensor.Dy_sim * pipe.diff_tensor.Dy_unit_sim
                sim_Dz_vectors = pipe.diff_tensor.Dz_sim * pipe.diff_tensor.Dz_unit_sim
            else:
                sim_Dx_vectors = None
                sim_Dy_vectors = None
                sim_Dz_vectors = None
                
            # Generate the axes representation.
            res_num = generate_vector_residues(structure=structure, vector=pipe.diff_tensor.Dx*pipe.diff_tensor.Dx_unit, atom_name='Dpar', res_name_vect='AXS', sim_vectors=sim_Dx_vectors, chain_id=chain_id, res_num=res_num, origin=R, scale=scale, neg=True)
            res_num = generate_vector_residues(structure=structure, vector=pipe.diff_tensor.Dy*pipe.diff_tensor.Dy_unit, atom_name='Dpar', res_name_vect='AXS', sim_vectors=sim_Dy_vectors, chain_id=chain_id, res_num=res_num, origin=R, scale=scale, neg=True)
            res_num = generate_vector_residues(structure=structure, vector=pipe.diff_tensor.Dz*pipe.diff_tensor.Dz_unit, atom_name='Dpar', res_name_vect='AXS', sim_vectors=sim_Dz_vectors, chain_id=chain_id, res_num=res_num, origin=R, scale=scale, neg=True)


    # Create the PDB file.
    ######################

    # Print out.
    print "\nGenerating the PDB file."

    # Open the PDB file for writing.
    tensor_pdb_file = open_write_file(file, dir, force=force)

    # Write the data.
    write_pdb_file(tensor_pdb_file)

    # Close the file.
    tensor_pdb_file.close()


def create_vector_dist(run=None, length=None, symmetry=1, file=None, dir=None, force=0):
    """Create a PDB representation of the XH vector distribution.

    @param run:         The run.
    @type run:          str
    @param length:      The length to set the vectors to in the PDB file.
    @type length:       float
    @param symmetry:    The symmetry flag which if set will create a second PDB chain 'B' which
        is the same as chain 'A' but with the XH vectors reversed.
    @type symmetry:     int
    @param file:        The name of the PDB file to create.
    @type file:         str
    @param dir:         The name of the directory to place the PDB file into.
    @type dir:          str
    @param force:       Flag which if set will overwrite any pre-existing file.
    @type force:        int
    """

    # Arguments.
    run = run

    # Test if the run exists.
    if not run in ds.run_names:
        raise RelaxNoPipeError, run

    # Test if the PDB file of the macromolecule has been loaded.
    if not ds.pdb.has_key(run):
        raise RelaxNoPdbError, run

    # Test if sequence data is loaded.
    if not len(ds.res[run]):
        raise RelaxNoSequenceError, run

    # Test if unit vectors exist.
    vectors = 0
    for i in xrange(len(ds.res[run])):
        if hasattr(ds.res[run][i], 'xh_vect'):
            vectors = 1
            break
    if not vectors:
        raise RelaxNoVectorsError, run


    # Initialise.
    #############

    # Create the structural object.
    structure = Internal()

    # Initialise the residue number.
    res_num = 1


    # Centre of mass.
    #################

    # Calculate the centre of mass.
    R = centre_of_mass()

    # Increment the residue number.
    res_num = res_num + 1


    # The XH vectors.
    #################

    # Loop over the spin systems.
    for i in xrange(len(ds.res[run])):
        # Alias the spin system data.
        data = ds.res[run][i]

        # Skip deselected spin systems.
        if not data.select:
            continue

        # Skip spin systems missing the xh_vect structure.
        if not hasattr(data, 'xh_vect'):
            continue

        # Scale the vector.
        vector = data.xh_vect * length * 1e10

        # The atom ids.
        end = '_' + `data.num` + '_' + data.name
        X_id = data.heteronuc + end
        H_id = data.proton + end

        # Add the central X atom.
        structure.atom_add(pdb_record='ATOM', atom_num=X_id, atom_name=data.heteronuc, res_name=data.name, chain_id='A', res_num=data.num, pos=R, segment_id=None, element=data.heteronuc, struct_index=None)

        # Add the H atom.
        structure.atom_add(pdb_record='ATOM', atom_num=H_id, atom_name=data.proton, res_name=data.name, chain_id='A', res_num=data.num, pos=R+vector, segment_id=None, element=data.proton, struct_index=None)

        # Connect the two atoms.
        structure.atom_connect(atom_id=X_id, bonded_id=H_id)

        # Store the terminate residue number for the TER record.
        last_res = data.num
        last_name = data.name

    # The TER record.
    structure.atom_add(pdb_record='TER', atom_num=None, atom_name='TER' + '_A', res_name=last_name, chain_id='A', res_num=last.res, pos=R, segment_id=None, element=None, struct_index=None)

    # Symmetry chain.
    if symmetry:
        # Loop over the spin systems.
        for i in xrange(len(ds.res[run])):
            # Alias the spin system data.
            data = ds.res[run][i]

            # Skip deselected spin systems.
            if not data.select:
                continue

            # Skip spin systems missing the xh_vect structure.
            if not hasattr(data, 'xh_vect'):
                continue

            # Scale the vector.
            vector = data.xh_vect * length * 1e10

            # The atom ids.
            end = '_' + `data.num` + '_' + data.name
            X_id = data.heteronuc + end
            H_id = data.proton + end

            # Add the central X atom.
            structure.atom_add(pdb_record='ATOM', atom_num=X_id + 'B', atom_name=data.heteronuc, res_name=data.name, chain_id='B', res_num=data.num, pos=R, segment_id=None, element=data.heteronuc, struct_index=None)

            # Add the H atom.
            structure.atom_add(pdb_record='ATOM', atom_num=H_id + 'B', atom_name=data.proton, res_name=data.name, chain_id='B', res_num=data.num, pos=R+vector, segment_id=None, element=data.proton, struct_index=None)

            # Connect the two atoms.
            structure.atom_connect(atom_id=X_id + '_B', bonded_id=H_id + '_B')

            # Store the terminate residue number for the TER record.
            last_res = data.num
            last_name = data.name

        # The TER record.
        structure.atom_add(pdb_record='TER', atom_num=None, atom_name='TER' + '_B', res_name=last_name, chain_id='B', res_num=last.res, pos=R, segment_id=None, element=None, struct_index=None)



    # Create the PDB file.
    ######################

    # Print out.
    print "\nGenerating the PDB file."

    # Open the PDB file for writing.
    tensor_pdb_file = open_write_file(file, dir, force=force)

    # Write the data.
    write_pdb_file(tensor_pdb_file)

    # Close the file.
    tensor_pdb_file.close()


def generate_vector_dist(structure=None, atom_id_ext='', res_name=None, res_num=None, chain_id='', centre=zeros(3, float64), R=eye(3), warp=eye(3), max_angle=None, scale=1.0, inc=20):
    """Generate a uniformly distributed distribution of atoms on a warped sphere.

    The vectors from the function uniform_vect_dist_spherical_angles() are used to generate the
    distribution.  These vectors are rotated to the desired frame using the rotation matrix 'R',
    then each compressed or stretched by the dot product with the 'warp' matrix.  Each vector is
    centred and at the head of the vector, a proton is placed.


    @param structure:       The structural data object.
    @type structure:        instance of class derived from Base_struct_API
    @param atom_id_ext:     The atom identifier extension.
    @type atom_id_ext:      str
    @param res_name:        The residue name.
    @type res_name:         str
    @param res_num:         The residue number.
    @type res_num:          int
    @param chain_id:        The chain identifier.
    @type chain_id:         str
    @param centre:          The centre of the distribution.
    @type centre:           numpy array, len 3
    @param R:               The optional 3x3 rotation matrix.
    @type R:                3x3 numpy array
    @param warp:            The optional 3x3 warping matrix.
    @type warp:             3x3 numpy array
    @param max_angle:       The maximal polar angle, in rad, after which all vectors are skipped.
    @type max_angle:        float
    @param scale:           The scaling factor to stretch all rotated and warped vectors by.
    @type scale:            float
    @param inc:             The number of increments or number of vectors used to generate the outer
                            edge of the cone.
    @type inc:              int
    """

    # Initial atom number.
    atom_num = 1

    # Get the uniform vector distribution.
    print "    Creating the uniform vector distribution."
    vectors = uniform_vect_dist_spherical_angles(inc=inc)

    # Generate the increment values of v.
    v = zeros(inc/2+2, float64)
    val = 1.0 / float(inc/2)
    for i in xrange(1, inc/2+1):
        v[i] = float(i-1) * val + val/2.0
    v[-1] = 1.0

    # Generate the distribution of spherical angles phi.
    phi = arccos(2.0 * v - 1.0)

    # Loop over the angles and find the minimum latitudinal index.
    for j_min in xrange(len(phi)):
        if phi[j_min] < max_angle:
            break

    # Loop over the radial array of vectors (change in longitude).
    for i in range(inc):
        # Loop over the vectors of the radial array (change in latitude).
        for j in range(inc/2+2):
            # Skip the vector if the polar angle is greater than max_angle.
            if j < j_min:
                continue

            # Index.
            index = i + j*inc

            # Atom id.
            atom_id = 'T' + `i` + 'P' + `j` + atom_id_ext

            # Rotate the vector into the diffusion frame.
            vector = dot(R, vectors[index])

            # Set the length of the vector to its diffusion rate within the diffusion tensor geometric object.
            vector = dot(warp, vector)

            # Scale the vector.
            vector = vector * scale

            # Position relative to the centre of mass.
            pos = centre + vector

            # Add the vector as a H atom of the TNS residue.
            structure.atom_add(pdb_record='HETATM', atom_num=None, atom_name='H'+atom_id_ext, res_name=res_name, chain_id=chain_id, res_num=res_num, pos=pos, segment_id=None, element='H', struct_index=None)

            # Connect to the previous atom (to generate the longitudinal lines).
            if j > j_min:
                prev_id = 'T' + `i` + 'P' + `j-1` + atom_id_ext
                structure.atom_connect(atom_id=atom_id, bonded_id=prev_id)

            # Connect across the radial arrays (to generate the latitudinal lines).
            if i != 0:
                neighbour_id = 'T' + `i-1` + 'P' + `j` + atom_id_ext
                structure.atom_connect(atom_id=atom_id, bonded_id=neighbour_id)

            # Connect the last radial array to the first (to zip up the geometric object and close the latitudinal lines).
            if i == inc-1:
                neighbour_id = 'T' + `0` + 'P' + `j` + atom_id_ext
                structure.atom_connect(atom_id=atom_id, bonded_id=neighbour_id)

            # Increment the atom number.
            atom_num = atom_num + 1


def generate_vector_residues(structure=None, vector=None, atom_name=None, res_name_vect='AXS', sim_vectors=None, res_name_sim='SIM', chain_id='', res_num=None, origin=None, scale=1.0, label_placement=1.1, neg=False):
    """Generate residue representations for the vector and the MC simulationed vectors.

    This is used to create a PDB representation of any vector, including its Monte Carlo
    simulations.

    @param structure:       The structural data object.
    @type structure:        instance of class derived from Base_struct_API
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

    # The atom ID extension.
    if chain_id:
        atom_id_ext = '_' + chain_id
    else:
        atom_id_ext = ''

    # The origin atom.
    structure.atom_add(pdb_record='HETATM', atom_num='R_vect'+atom_id_ext, atom_name=R, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin, segment_id=None, element='C', struct_index=None)

    # Create the PDB residue representing the vector.
    structure.atom_add(pdb_record='HETATM', atom_num=atom_name+atom_id_ext, atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin+vector*scale, segment_id=None, element='C', struct_index=None)
    structure.atom_connect(atom_id=atom_name+atom_id_ext, bonded_id='R_vect'+atom_id_ext)
    if neg:
        structure.atom_add(pdb_record='HETATM', atom_num=atom_name+'_neg'+atom_id_ext, atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin+vector*scale, segment_id=None, element='C', struct_index=None)
        structure.atom_connect(atom_id=atom_name+'_neg'+atom_id_ext, bonded_id='R_vect'+atom_id_ext)

    # Add another atom to allow the axis labels to be shifted just outside of the vector itself.
    structure.atom_add(pdb_record='HETATM', atom_num='vect label'+atom_id_ext, atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin+label_placement*vector*scale, segment_id=None, element='N', struct_index=None)
    if neg:
        structure.atom_add(pdb_record='HETATM', atom_num='vect neg label'+atom_id_ext, atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin-label_placement*vector*scale, segment_id=None, element='N', struct_index=None)

    # Print out.
    print "    " + atom_name + " vector (scaled + shifted to origin): " + `origin+vector*scale`
    print "    Creating the MC simulation vectors."

    # Monte Carlo simulations.
    if sim_vectors:
        for i in xrange(sim_vectors):
            # Increment the residue number, so each simulation is a new residue.
            res_num = res_num + 1

            # Modify the atom_id for each simulation.
            atom_id_ext_sim = atom_id_ext + '_sim' + `i`

            # Create the PDB residue representing the vector.
            structure.atom_add(pdb_record='HETATM', atom_num=atom_name+atom_id_ext_sim, atom_name=atom_name, res_name=res_name_sim, chain_id=chain_id, res_num=res_num, pos=origin+sim_vectors[i]*scale, segment_id=None, element='C', struct_index=None)
            structure.atom_connect(atom_id=atom_name+atom_id_ext_sim, bonded_id='R_vect'+atom_id_ext_sim)
            if neg:
                structure.atom_add(pdb_record='HETATM', atom_num=atom_name+'_neg'+atom_id_ext_sim, atom_name=atom_name, res_name=res_name_sim, chain_id=chain_id, res_num=res_num, pos=origin-sim_vectors[i]*scale, segment_id=None, element='C', struct_index=None)
                structure.atom_connect(atom_id=atom_name+'_neg'+atom_id_ext_sim, bonded_id='R_vect'+atom_id_ext_sim)

    # Return the new residue number.
    return res_num


def stitch_cap_to_cone(structure=None, atom_id_ext='', max_angle=None, inc=None):
    """Function for stitching the cap of a cone to the cone edge, in the PDB representations.

    @param structure:       The structural data object.
    @type structure:        instance of class derived from Base_struct_API
    @param atom_id_ext:     The atom identifier extension.
    @type atom_id_ext:      str
    @param max_angle:       The maximal polar angle, in rad, after which all vectors are skipped.
    @type max_angle:        float
    @param inc:             The number of increments or number of vectors used to generate the outer
                            edge of the cone.
    @type inc:              int
    """

    # Generate the increment values of v.
    v = zeros(inc/2+2, float64)
    val = 1.0 / float(inc/2)
    for i in xrange(1, inc/2+1):
        v[i] = float(i-1) * val + val/2.0
    v[-1] = 1.0

    # Generate the distribution of spherical angles phi.
    phi = arccos(2.0 * v - 1.0)

    # Loop over the angles and find the minimum latitudinal index.
    for j_min in xrange(len(phi)):
        if phi[j_min] < max_angle:
            break

    # Loop over the radial array of vectors (change in longitude).
    for i in range(inc):
        # Cap atom id.
        cap_atom_id = 'T' + `i` + 'P' + `j_min` + atom_id_ext

        # Cone edge atom id.
        edge_atom_id = 'T' + `i` + atom_id_ext

        # Connect the two atoms (to stitch up the 2 objects).
        structure.atom_connect(atom_id=edge_atom_id, bonded_id=cap_atom_id)


def uniform_vect_dist_spherical_angles(inc=20):
    """Uniform distribution of vectors on a sphere using uniform spherical angles.

    This function returns an array of unit vectors uniformly distributed within 3D space.  To
    create the distribution, uniform spherical angles are used.  The two spherical angles are
    defined as

        theta = 2.pi.u,
        phi = cos^-1(2v - 1),

    where

        u in [0, 1),
        v in [0, 1].

    Because theta is defined between [0, pi] and phi is defined between [0, 2pi], for a uniform
    distribution u is only incremented half of 'inc'.  The unit vectors are generated using the
    equation

                   | cos(theta) * sin(phi) |
        vector  =  | sin(theta) * sin(phi) |.
                   |      cos(phi)         |

    The vectors of this distribution generate both longitudinal and latitudinal lines.
    """

    # The inc argument must be an even number.
    if inc%2:
        raise RelaxError, "The increment value of " + `inc` + " must be an even number."

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

    # Initialise array of the distribution of vectors.
    vectors = []

    # Loop over the longitudinal lines.
    for j in xrange(len(v)):
        # Loop over the latitudinal lines.
        for i in xrange(len(u)):
            # X coordinate.
            x = cos(theta[i]) * sin(phi[j])

            # Y coordinate.
            y =  sin(theta[i])* sin(phi[j])

            # Z coordinate.
            z = cos(phi[j])

            # Append the vector.
            vectors.append(array([x, y, z], float64))

    # Return the array of vectors.
    return vectors
