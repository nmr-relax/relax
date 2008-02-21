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
from math import sqrt, cos, pi, sin
from numpy import arccos, array, dot, float64, zeros
from os import F_OK, access
from re import compile, match
import Scientific.IO.PDB
from string import ascii_uppercase
from warnings import warn

# relax module imports.
from data import Data as relax_data_store
from generic_fns import molmol
from generic_fns.sequence import load_PDB_sequence
from generic_fns.selection import exists_mol_res_spin_data, return_molecule, return_residue, return_spin, spin_loop
from maths_fns.rotation_matrix import R_2vect
from physical_constants import ArH, ArC, ArN, ArO, ArS
from relax_errors import RelaxError, RelaxFileError, RelaxNoPdbChainError, RelaxNoPdbError, RelaxNoResError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoTensorError, RelaxNoVectorsError, RelaxPdbError, RelaxPdbLoadError, RelaxRegExpError
from relax_io import get_file_path, open_write_file
from relax_warnings import RelaxNoAtomWarning, RelaxNoPDBFileWarning, RelaxWarning, RelaxZeroVectorWarning



def atom_add(atomic_data=None, atom_id=None, record_name='', atom_name='', res_name='', chain_id='', res_num=None, pos=[None, None, None], segment_id='', element=''):
    """Function for adding an atom to the atomic_data structure.

    The atomic_data data structure is a dictionary of arrays.  The keys correspond to the
    'atom_id' strings.  The elements of the array are:

        0:  Atom number.
        1:  The record name (one of ATOM, HETATM, or TER).
        2:  Atom name.
        3:  Residue name.
        4:  Chain ID.
        5:  Residue number.
        6:  The x coordinate of the atom.
        7:  The y coordinate of the atom.
        8:  The z coordinate of the atom.
        9:  Segment ID.
        10:  Element symbol.
        11+:  The bonded atom numbers.

    This function will create the key-value pair for the given atom.


    @param atomic_data: The dictionary to place the atomic data into.
    @type atomic_data:  dict
    @param atom_id:     The atom identifier.  This is used as the key within the dictionary.
    @type atom_id:      str
    @param record_name: The record name, e.g. 'ATOM', 'HETATM', or 'TER'.
    @type record_name:  str
    @param atom_name:   The atom name, e.g. 'H1'.
    @type atom_name:    str
    @param res_name:    The residue name.
    @type res_name:     str
    @param chain_id:    The chain identifier.
    @type chain_id:     str
    @param res_num:     The residue number.
    @type res_num:      int
    @param pos:         The position vector of coordinates.
    @type pos:          list (length = 3)
    @param segment_id:  The segment identifier.
    @type segment_id:   str
    @param element:     The element symbol.
    @type element:      str
    @return:            None
    """

    # Initialise the key-value pair.
    atomic_data[atom_id] = []

    # Fill the positions.
    atomic_data[atom_id].append(len(atomic_data))
    atomic_data[atom_id].append(record_name)
    atomic_data[atom_id].append(atom_name)
    atomic_data[atom_id].append(res_name)
    atomic_data[atom_id].append(chain_id)
    atomic_data[atom_id].append(res_num)
    atomic_data[atom_id].append(pos[0])
    atomic_data[atom_id].append(pos[1])
    atomic_data[atom_id].append(pos[2])
    atomic_data[atom_id].append(segment_id)
    atomic_data[atom_id].append(element)


def atom_connect(atomic_data=None, atom_id=None, bonded_id=None):
    """Function for connecting two atoms within the atomic_data data structure.

    The atomic_data data structure is a dictionary of arrays.  The keys correspond to the
    'atom_id' strings.  The elements of the array are:

        0:  Atom number.
        1:  The record name (one of ATOM, HETATM, or TER).
        2:  Atom name.
        3:  Residue name.
        4:  Chain ID.
        5:  Residue number.
        6:  The x coordinate of the atom.
        7:  The y coordinate of the atom.
        8:  The z coordinate of the atom.
        9:  Segment ID.
        10:  Element symbol.
        11+:  The bonded atom numbers.

    This function will find the atom number corresponding to both the atom_id and bonded_id.
    The bonded_id atom number will then be appended to the atom_id array.  Because the
    connections work both ways in the PDB file, the atom_id atom number will be appended to the
    bonded_id atom array as well.


    @param atomic_data: The dictionary to place the atomic data into.
    @type atomic_data:  dict
    @param atom_id:     The atom identifier.  This is used as the key within the dictionary.
    @type atom_id:      str
    @param bonded_id:   The second atom identifier.  This is used as the key within the dictionary.
    @type bonded_id:    str
    """

    # Find the atom number corresponding to atom_id.
    if atomic_data.has_key(atom_id):
        atom_num = atomic_data[atom_id][0]
    else:
        raise RelaxError, "The atom corresponding to the atom_id " + `atom_id` + " doesn't exist."

    # Find the atom number corresponding to bonded_id.
    if atomic_data.has_key(bonded_id):
        bonded_num = atomic_data[bonded_id][0]
    else:
        raise RelaxError, "The atom corresponding to the bonded_id " + `bonded_id` + " doesn't exist."

    # Add the bonded_id to the atom_id array.
    atomic_data[atom_id].append(bonded_num)

    # Add the atom_id to the bonded_id array.
    atomic_data[bonded_id].append(atom_num)


def atomic_mass(element=None):
    """Return the atomic mass of the given element.

    @param element: The name of the element to return the atomic mass of.
    @type element:  str
    @return:        The relative atomic mass.
    @rtype:         float
    """

    # Proton.
    if element == 'H' or element == 'Q':
        return ArH

    # Carbon.
    elif element == 'C':
        return ArC

    # Nitrogen.
    elif element == 'N':
        return ArN

    # Oxygen.
    elif element == 'O':
        return ArO

    # Sulphur.
    elif element == 'S':
        return ArS

    # Unknown.
    else:
        raise RelaxError, "The mass of the element " + `element` + " has not yet been programmed into relax."


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


def centre_of_mass(return_mass=False):
    """Calculate and return the centre of mass of the structure.

    @param return_mass: A flag which if False will cause only the centre of mass to be returned, but
                        if True will cause the centre of mass and the mass itself to be returned as
                        a tuple.
    @type return_mass:  bool
    @return:            The centre of mass vector, and additionally the mass.
    @rtype:             list of 3 floats (or tuple of a list of 3 floats and one float)
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if a structure has been loaded.
    if not hasattr(cdp.structure, 'structures'):
        raise RelaxNoPdbError

    # Print out.
    print "Calculating the centre of mass."

    # Initialise the centre of mass.
    R = zeros(3, float64)

    # Initialise the total mass.
    M = 0.0

    # Loop over the structures.
    for struct in cdp.structure.structures:
        # Get the corresponding molecule container.
        if cdp.mol[0].name == None:
            mol_cont = cdp.mol[0]
        else:
            mol_cont = return_molecule('#' + struct.name)

        # Deselected molecule.
        if not mol_cont.select:
            continue

        # Protein.
        if struct.peptide_chains:
            chains = struct.peptide_chains

        # RNA/DNA.
        elif struct.nucleotide_chains:
            chains = struct.nucleotide_chains

        # Loop over the residues of the protein in the PDB file.
        for res in chains[0].residues:
            # Get the corresponding residue container.
            if mol_cont.res[0].name == None and mol_cont.res[0].num == None:
                res_cont = mol_cont.res[0]
            else:
                res_cont = return_residue(':' + `res.number`)

            # Deselected residue.
            if not res_cont.select:
                continue

            # Loop over the atoms of the residue.
            for atom in res:
                # Get the corresponding spin container.
                if res_cont.spin[0].name == None and res_cont.spin[0].num == None:
                    spin_cont = res_cont.spin[0]
                else:
                    spin_cont = return_spin('@' + `atom.properties['serial_number']`)

                # Deselected spin.
                if not spin_cont.select:
                    continue

                # Atomic mass.
                mass = atomic_mass(atom.properties['element'])

                # Total mass.
                M = M + mass

                # Sum of mass * position.
                R = R + mass * atom.position.array

    # Normalise.
    R = R / M

    # Final print out.
    print "    Total mass:      M = " + `M`
    print "    Centre of mass:  R = " + `R`

    # Return the centre of mass.
    if return_mass:
        return R,M
    else:
        return R


def cone_edge(atomic_data=None, res_num=None, apex=None, axis=None, angle=None, length=None, inc=None):
    """Add a residue to the atomic data representing a cone of the given angle.

    A series of vectors totalling the number of increments and starting at the origin are equally
    spaced around the cone axis.  The atoms representing neighbouring vectors will be directly
    bonded together.  This will generate an object representing the outer edge of a cone.


    @param atomic_data:     The dictionary to place the atomic data into.
    @type atomic_data:      dict
    @param res_num:         The residue number.
    @type res_num:          int
    @param apex:            The apex of the cone.
    @type apex:             numpy array, len 3
    @param axis:            The central axis of the cone.
    @type axis:             numpy array, len 3
    @param angle:           The cone angle in radians.
    @type angle:            float
    @param length:          The cone length in meters.
    @type length:           float
    @param inc:             The number of increments or number of vectors used to generate the outer
                            edge of the cone.
    @type inc:              int
    """

    # Initialise the rotation matrix, atom number, etc.
    R = zeros((3,3), float64)
    atom_num = 1

    # Get the rotation matrix.
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

        # Add the vector as a H atom of the CON residue.
        atom_add(atomic_data=atomic_data, atom_id=atom_id, record_name='HETATM', atom_name='H'+`atom_num`, res_name='CON', res_num=res_num, pos=pos, element='H')

        # Connect across the radial arrays (to generate the latitudinal lines).
        if i != 0:
            neighbour_id = 'T' + `i-1`
            atom_connect(atomic_data=atomic_data, atom_id=atom_id, bonded_id=neighbour_id)

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
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Create an array of data pipes to loop over (hybrid support).
    if cdp.pipe_type == 'hybrid':
        pipes = cdp.hybrid_pipes
    else:
        pipes = [relax_data_store.current_pipe]

    # Initialise the atom and atomic connections data structures.
    atomic_data = {}

    # Loop over the pipes.
    for pipe_index in xrange(len(pipes)):
        # Alias the pipe container.
        pipe = relax_data_store[pipes[pipe_index]]


        # Tests.
        ########

        # Test if the diffusion tensor data is loaded.
        if not hasattr(pipe, 'diff'):
            raise RelaxNoTensorError, 'diffusion'

        # Test if a structure has been loaded.
        if not hasattr(cdp.structure, 'structures'):
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
        R = centre_of_mass()

        # Add the central atom.
        atom_add(atomic_data=atomic_data, atom_id='R'+atom_id_ext, record_name='HETATM', atom_name='R', res_name='COM', chain_id=chain_id, res_num=res_num, pos=R, element='C')

        # Increment the residue number.
        res_num = res_num + 1


        # Vector distribution.
        ######################

        # Print out.
        print "\nGenerating the geometric object."

        # Increment value and initial atom number.
        inc = 20
        atom_num = 1

        # Get the uniform vector distribution.
        print "    Creating the uniform vector distribution."
        vectors = uniform_vect_dist_spherical_angles(inc=20)

        # Loop over the radial array of vectors (change in longitude).
        for i in range(inc):
            # Loop over the vectors of the radial array (change in latitude).
            for j in range(inc/2+2):
                # Index.
                index = i + j*inc

                # Atom id.
                atom_id = 'T' + `i` + 'P' + `j` + atom_id_ext

                # Rotate the vector into the diffusion frame.
                vector = dot(pipe.diff.rotation, vectors[index])

                # Set the length of the vector to its diffusion rate within the diffusion tensor geometric object.
                vector = dot(pipe.diff.tensor, vector)

                # Scale the vector.
                vector = vector * scale

                # Position relative to the centre of mass.
                pos = R + vector

                # Add the vector as a H atom of the TNS residue.
                atom_add(atomic_data=atomic_data, atom_id=atom_id, record_name='HETATM', atom_name='H'+`atom_num`, res_name='TNS', chain_id=chain_id, res_num=res_num, pos=pos, element='H')

                # Connect to the previous atom (to generate the longitudinal lines).
                if j != 0:
                    prev_id = 'T' + `i` + 'P' + `j-1` + atom_id_ext
                    atom_connect(atomic_data=atomic_data, atom_id=atom_id, bonded_id=prev_id)

                # Connect across the radial arrays (to generate the latitudinal lines).
                if i != 0:
                    neighbour_id = 'T' + `i-1` + 'P' + `j` + atom_id_ext
                    atom_connect(atomic_data=atomic_data, atom_id=atom_id, bonded_id=neighbour_id)

                # Connect the last radial array to the first (to zip up the geometric object and close the latitudinal lines).
                if i == inc-1:
                    neighbour_id = 'T' + `0` + 'P' + `j` + atom_id_ext
                    atom_connect(atomic_data=atomic_data, atom_id=atom_id, bonded_id=neighbour_id)

                # Increment the atom number.
                atom_num = atom_num + 1

        # Increment the residue number.
        res_num = res_num + 1


        # Axes of the tensor.
        #####################

        # Create the unique axis of the spheroid.
        if pipe.diff.type == 'spheroid':
            # Print out.
            print "\nGenerating the unique axis of the diffusion tensor."
            print "    Scaling factor:                      " + `scale`

            # Simulations.
            if hasattr(pipe.diff, 'tm_sim'):
                sim_vectors = pipe.diff.Dpar_sim * pipe.diff.Dpar_unit_sim
            else:
                sim_vectors = None
                
            # Generate the axes representation.
            res_num = generate_vector_residues(atomic_data=atomic_data, vector=pipe.diff.Dpar*pipe.diff.Dpar_unit, atom_name='Dpar', res_name_vect='AXS', sim_vectors=sim_vectors, chain_id=chain_id, res_num=res_num, origin=R, scale=scale, neg=True)


        # Create the three axes of the ellipsoid.
        if pipe.diff.type == 'ellipsoid':
            # Print out.
            print "Generating the three axes of the ellipsoid."
            print "    Scaling factor:                      " + `scale`

            # Simulations.
            if hasattr(pipe.diff, 'tm_sim'):
                sim_Dx_vectors = pipe.diff.Dx_sim * pipe.diff.Dx_unit_sim
                sim_Dy_vectors = pipe.diff.Dy_sim * pipe.diff.Dy_unit_sim
                sim_Dz_vectors = pipe.diff.Dz_sim * pipe.diff.Dz_unit_sim
            else:
                sim_Dx_vectors = None
                sim_Dy_vectors = None
                sim_Dz_vectors = None
                
            # Generate the axes representation.
            res_num = generate_vector_residues(atomic_data=atomic_data, vector=pipe.diff.Dx*pipe.diff.Dx_unit, atom_name='Dpar', res_name_vect='AXS', sim_vectors=sim_Dx_vectors, chain_id=chain_id, res_num=res_num, origin=R, scale=scale, neg=True)
            res_num = generate_vector_residues(atomic_data=atomic_data, vector=pipe.diff.Dy*pipe.diff.Dy_unit, atom_name='Dpar', res_name_vect='AXS', sim_vectors=sim_Dy_vectors, chain_id=chain_id, res_num=res_num, origin=R, scale=scale, neg=True)
            res_num = generate_vector_residues(atomic_data=atomic_data, vector=pipe.diff.Dz*pipe.diff.Dz_unit, atom_name='Dpar', res_name_vect='AXS', sim_vectors=sim_Dz_vectors, chain_id=chain_id, res_num=res_num, origin=R, scale=scale, neg=True)


        # Terminate the chain (the TER record).
        #######################################

        # The name of the last residue.
        atomic_arrays = atomic_data.values()
        atomic_arrays.sort()
        last_res = atomic_arrays[-1][3]

        # Add the TER 'atom'.
        atom_add(atomic_data=atomic_data, atom_id='TER' + atom_id_ext, record_name='TER', res_name=last_res, res_num=res_num)


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
    if not run in relax_data_store.run_names:
        raise RelaxNoPipeError, run

    # Test if the PDB file of the macromolecule has been loaded.
    if not relax_data_store.pdb.has_key(run):
        raise RelaxNoPdbError, run

    # Test if sequence data is loaded.
    if not len(relax_data_store.res[run]):
        raise RelaxNoSequenceError, run

    # Test if unit vectors exist.
    vectors = 0
    for i in xrange(len(relax_data_store.res[run])):
        if hasattr(relax_data_store.res[run][i], 'xh_vect'):
            vectors = 1
            break
    if not vectors:
        raise RelaxNoVectorsError, run


    # Initialise.
    #############

    # Initialise the atom and atomic connections data structures.
    atomic_data = {}

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
    for i in xrange(len(relax_data_store.res[run])):
        # Alias the spin system data.
        data = relax_data_store.res[run][i]

        # Skip unselected spin systems.
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
        atom_add(atomic_data=atomic_data, atom_id=X_id, record_name='ATOM', atom_name=data.heteronuc, res_name=data.name, chain_id='A', res_num=data.num, pos=R, element=data.heteronuc)

        # Add the H atom.
        atom_add(atomic_data=atomic_data, atom_id=H_id, record_name='ATOM', atom_name=data.proton, res_name=data.name, chain_id='A', res_num=data.num, pos=R+vector, element=data.proton)

        # Connect the two atoms.
        atom_connect(atomic_data=atomic_data, atom_id=X_id, bonded_id=H_id)

        # Store the terminate residue number for the TER record.
        last_res = data.num
        last_name = data.name

    # The TER record.
    atom_add(atomic_data=atomic_data, atom_id='TER' + '_A', record_name='TER', res_name=last_name, chain_id='A', res_num=last_res)

    # Symmetry chain.
    if symmetry:
        # Loop over the spin systems.
        for i in xrange(len(relax_data_store.res[run])):
            # Alias the spin system data.
            data = relax_data_store.res[run][i]

            # Skip unselected spin systems.
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
            atom_add(atomic_data=atomic_data, atom_id=X_id + '_B', record_name='ATOM', atom_name=data.heteronuc, res_name=data.name, chain_id='B', res_num=data.num, pos=R, element=data.heteronuc)

            # Add the H atom.
            atom_add(atomic_data=atomic_data, atom_id=H_id + '_B', record_name='ATOM', atom_name=data.proton, res_name=data.name, chain_id='B', res_num=data.num, pos=R-vector, element=data.proton)

            # Connect the two atoms.
            atom_connect(atomic_data=atomic_data, atom_id=X_id + '_B', bonded_id=H_id + '_B')

            # Store the terminate residue number for the TER record.
            last_res = data.num
            last_name = data.name

        # The TER record.
        atom_add(atomic_data=atomic_data, atom_id='TER' + '_B', record_name='TER', res_name=last_name, chain_id='B', res_num=last_res)



    # Create the PDB file.
    ######################

    # Print out.
    print "\nGenerating the PDB file."

    # Open the PDB file for writing.
    tensor_pdb_file = relax.IO.open_write_file(file, dir, force=force)

    # Write the data.
    write_pdb_file(tensor_pdb_file)

    # Close the file.
    tensor_pdb_file.close()


def generate_vector_residues(atomic_data=None, vector=None, atom_name=None, res_name_vect='AXS', sim_vectors=None, res_name_sim='SIM', chain_id=None, res_num=None, origin=None, scale=1.0, label_placement=1.1, neg=False):
    """Generate residue representations for the vector and the MC simulationed vectors.

    This is used to create a PDB representation of any vector, including its Monte Carlo
    simulations.

    @param atomic_data:     The dictionary to place the atomic data into.
    @type atomic_data:      dict
    @param vector:          The vector to be represented in the PDB.
    @type vector:           numpy array, len 3
    @param atom_name:       The atom name used to label the atom representing the head of the vector
                            and also used as the first part of the atom identifier key in the
                            atomic_data dictionary.
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
    atom_add(atomic_data=atomic_data, atom_id='R_vect'+atom_id_ext, record_name='HETATM', atom_name='R', res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin, element='C')

    # Create the PDB residue representing the vector.
    atom_add(atomic_data=atomic_data, atom_id=atom_name+atom_id_ext, record_name='HETATM', atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin+vector*scale, element='C')
    atom_connect(atomic_data=atomic_data, atom_id=atom_name+atom_id_ext, bonded_id='R_vect'+atom_id_ext)
    if neg:
        atom_add(atomic_data=atomic_data, atom_id=atom_name+'_neg'+atom_id_ext, record_name='HETATM', atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin-vector*scale, element='C')
        atom_connect(atomic_data=atomic_data, atom_id=atom_name+'_neg'+atom_id_ext, bonded_id='R_vect'+atom_id_ext)

    # Add another atom to allow the axis labels to be shifted just outside of the vector itself.
    atom_add(atomic_data=atomic_data, atom_id='vect label'+atom_id_ext, record_name='HETATM', atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin+label_placement*vector*scale, element='N')
    if neg:
        atom_add(atomic_data=atomic_data, atom_id='vect neg label'+atom_id_ext, record_name='HETATM', atom_name=atom_name, res_name=res_name_vect, chain_id=chain_id, res_num=res_num, pos=origin-label_placement*vector*scale, element='N')

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
            atom_add(atomic_data=atomic_data, atom_id=atom_name+atom_id_ext_sim, record_name='HETATM', atom_name=atom_name, res_name=res_name_sim, chain_id=chain_id, res_num=res_num, pos=origin+sim_vectors[i]*scale, element='C')
            atom_connect(atomic_data=atomic_data, atom_id=atom_name+atom_id_ext_sim, bonded_id='R_vect'+atom_id_ext_sim)
            if neg:
                atom_add(atomic_data=atomic_data, atom_id=atom_name+'_neg'+atom_id_ext_sim, record_name='HETATM', atom_name=atom_name, res_name=res_name_sim, chain_id=chain_id, res_num=res_num, pos=origin-sim_vectors[i]*scale, element='C')
                atom_connect(atomic_data=atomic_data, atom_id=atom_name+'_neg'+atom_id_ext_sim, bonded_id='R_vect'+atom_id_ext_sim)

    # Return the new residue number.
    return res_num


def get_chemical_name(hetID):
    """Function for returning the chemical name corresponding to the given residue ID.

    The following names are currently returned:
    ________________________________________________
    |        |                                     |
    | hetID  | Chemical name                       |
    |________|_____________________________________|
    |        |                                     |
    | TNS    | Tensor                              |
    | COM    | Centre of mass                      |
    | AXS    | Tensor axes                         |
    | SIM    | Monte Carlo simulation tensor axes  |
    |________|_____________________________________|


    @param res: The residue ID.
    @type res:  str
    @return:    The chemical name.
    @rtype:     str
    """

    # Tensor.
    if hetID == 'TNS':
        return 'Tensor'

    # Centre of mass.
    if hetID == 'COM':
        return 'Centre of mass'

    # Tensor axes.
    if hetID == 'AXS':
        return 'Tensor axes'

    # Monte Carlo simulation tensor axes.
    if hetID == 'SIM':
        return 'Monte Carlo simulation tensor axes'

    # Unknown hetID.
    raise RelaxError, "The residue ID (hetID) " + `hetID` + " is not recognised."


def load_structures(file_path, model, verbosity=False):
    """Function for loading the structures from the PDB file.

    @param file_path:   The full path of the file.
    @type file_path:    str
    @param model:       The PDB model to use.
    @type model:        int
    @param verbosity:   A flag which if True will cause messages to be printed.
    @type verbosity:    bool
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Use pointers (references) if the PDB data exists in another run.
    for data_pipe in relax_data_store:
        if hasattr(data_pipe, 'structure') and hasattr(cdp.structure, 'structures') and data_pipe.structure.file_name == file_path and data_pipe.structure.model == model:
            # Make a pointer to the data.
            cdp.structure.structures = data_pipe.structure.structures

            # Print out.
            if verbosity:
                print "Using the structures from the data pipe " + `data_pipe.pipe_name` + "."
                for i in xrange(len(cdp.structure.structures)):
                    print cdp.structure.structures[i]

            # Exit this function.
            return

    # Initialisation.
    cdp.structure.structures = []

    # Load the structure i from the PDB file.
    if type(model) == int:
        # Print out.
        if verbosity:
            print "Loading structure " + `model` + " from the PDB file."

        # Load the structure into 'str'.
        str = Scientific.IO.PDB.Structure(file_path, model)

        # Test the structure.
        if len(str) == 0:
            raise RelaxPdbLoadError, file_path

        # Print the PDB info.
        if verbosity:
            print str

        # Place the structure in 'cdp.structure'.
        cdp.structure.structures.append(str)


    # Load all structures.
    else:
        # Print out.
        if verbosity:
            print "Loading all structures from the PDB file."

        # First model.
        i = 1

        # Loop over all the other structures.
        while 1:
            # Load the pdb files.
            str = Scientific.IO.PDB.Structure(file_path, i)

            # No model 1.
            if len(str) == 0 and i == 1:
                str = Scientific.IO.PDB.Structure(file_path)
                if len(str) == 0:
                    raise RelaxPdbLoadError, file_path

            # Test if the last structure has been reached.
            if len(str) == 0:
                del str
                break

            # Print the PDB info.
            if verbosity:
                print str

            # Place the structure in 'cdp.structure'.
            cdp.structure.structures.append(str)

            # Increment i.
            i = i + 1


def read_pdb(run=None, file=None, dir=None, model=None, load_seq=1, fail=1, verbosity=1):
    """The pdb loading function."""

    # Tests.
    ########

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if PDB data corresponding to the run already exists.
    if hasattr(cdp, 'struct'):
        raise RelaxPdbError

    # Test if sequence data is loaded.
    if not load_seq and not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # The file path.
    file_path = get_file_path(file, dir)

    # Test if the file exists.
    if not access(file_path, F_OK):
        if fail:
            raise RelaxFileError, ('PDB', file_path)
        else:
            warn(RelaxNoPDBFileWarning(file_path))
            return


    # Data creation.
    ################

    # File name.
    cdp.structure.file_name = file_path

    # Model.
    cdp.structure.model = model


    # Load the structures.
    ######################

    load_structures(file_path, model, verbosity)


    # Finish.
    #########

    # Sequence loading.
    if load_seq and not exists_mol_res_spin_data():
        load_PDB_sequence()

    # Load into Molmol (if running).
    molmol.open_pdb()


def set_vector(run=None, res=None, xh_vect=None):
    """Function for setting the XH unit vectors."""

    # Place the XH unit vector in 'relax_data_store.res'.
    relax_data_store.res[run][res].xh_vect = xh_vect


def vectors(heteronuc=None, proton=None, spin_id=None, verbosity=1):
    """Function for calculating/extracting the XH unit vector from the loaded structure.

    @param heteronuc:   The name of the heteronucleus.
    @type heteronuc:    str
    @param proton:      The name of the proton.
    @type proton:       str
    @param spin_id:     The molecule, residue, and spin identifier string.
    @type spin_id:      str
    @param verbosity:   The higher the value, the more information is printed to screen.
    @type verbosity:    int
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if the PDB file has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxPdbError

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test that the nuclei have been correctly set.
    if heteronuc == proton:
        raise RelaxError, "The proton and heteronucleus are set to the same atom."

    # Number of structures.
    num_str = len(cdp.structure.structures)

    # Print out.
    if verbosity:
        if num_str > 1:
            print "\nCalculating and averaging the unit XH vectors from all structures."
        else:
            print "\nCalculating the unit XH vectors from the structure."

    # Loop over the sequence.
    for spin in spin_loop(spin_id):
        # Skip unselected residues.
        if not spin.select:
            continue

        # Set the proton and heteronucleus names.
        spin.proton = proton
        spin.heteronuc = heteronuc

        # Calculate the vector.
        vector = xh_vector(spin)

        # Set the vector.
        if vector != None:
            spin.xh_vect = vector


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
            vectors.append([x, y, z])

    # Return the array of vectors.
    return vectors


def write_pdb_file(file):
    """Function for creating a PDB file from the given data.

    Introduction
    ============

    A number of PDB records including HET, HETNAM, FORMUL, HETATM, TER, CONECT, MASTER, and END
    are created.  To create the non-standard residue records HET, HETNAM, and FORMUL, the data
    structure 'het_data' is created.  It is an array of arrays where the first dimension
    corresponds to a different residue and the second dimension has the elements:

        0:  Residue number.
        1:  Residue name.
        2:  Chain ID.
        3:  Total number of atoms in the residue.
        4:  Number of H atoms in the residue.
        5:  Number of C atoms in the residue.


    The PDB records
    ===============

    The following information about the PDB records has been taken from the "Protein Data Bank
    Contents Guide: Atomic Coordinate Entry Format Description" version 2.1 (draft), October 25
    1996.

    HET record
    ----------

    The HET record describes non-standard residues.  The format is of the record is:
    __________________________________________________________________________________________
    |         |              |              |                                                |
    | Columns | Data type    | Field        | Definition                                     |
    |_________|______________|______________|________________________________________________|
    |         |              |              |                                                |
    |  1 -  6 | Record name  | "HET   "     |                                                |
    |  8 - 10 | LString(3)   | hetID        | Het identifier, right-justified.               |
    | 13      | Character    | ChainID      | Chain identifier.                              |
    | 14 - 17 | Integer      | seqNum       | Sequence number.                               |
    | 18      | AChar        | iCode        | Insertion code.                                |
    | 21 - 25 | Integer      | numHetAtoms  | Number of HETATM records for the group present |
    |         |              |              | in the entry.                                  |
    | 31 - 70 | String       | text         | Text describing Het group.                     |
    |_________|______________|______________|________________________________________________|


    HETNAM record
    -------------

    The HETNAM associates a chemical name with the hetID from the HET record.  The format is of
    the record is:
    __________________________________________________________________________________________
    |         |              |              |                                                |
    | Columns | Data type    | Field        | Definition                                     |
    |_________|______________|______________|________________________________________________|
    |         |              |              |                                                |
    |  1 -  6 | Record name  | "HETNAM"     |                                                |
    |  9 - 10 | Continuation | continuation | Allows concatenation of multiple records.      |
    | 12 - 14 | LString(3)   | hetID        | Het identifier, right-justified.               |
    | 16 - 70 | String       | text         | Chemical name.                                 |
    |_________|______________|______________|________________________________________________|


    FORMUL record
    -------------

    The chemical formula for non-standard groups. The format is of the record is:
    __________________________________________________________________________________________
    |         |              |              |                                                |
    | Columns | Data type    | Field        | Definition                                     |
    |_________|______________|______________|________________________________________________|
    |         |              |              |                                                |
    |  1 -  6 | Record name  | "FORMUL"     |                                                |
    |  9 - 10 | Integer      | compNum      | Component number.                              |
    | 13 - 15 | LString(3)   | hetID        | Het identifier.                                |
    | 17 - 18 | Integer      | continuation | Continuation number.                           |
    | 19      | Character    | asterisk     | "*" for water.                                 |
    | 20 - 70 | String       | text         | Chemical formula.                              |
    |_________|______________|______________|________________________________________________|


    ATOM record
    -----------

    The ATOM record contains the atomic coordinates for atoms belonging to standard residues.
    The format is of the record is:
    __________________________________________________________________________________________
    |         |              |              |                                                |
    | Columns | Data type    | Field        | Definition                                     |
    |_________|______________|______________|________________________________________________|
    |         |              |              |                                                |
    |  1 -  6 | Record name  | "ATOM"       |                                                |
    |  7 - 11 | Integer      | serial       | Atom serial number.                            |
    | 13 - 16 | Atom         | name         | Atom name.                                     |
    | 17      | Character    | altLoc       | Alternate location indicator.                  |
    | 18 - 20 | Residue name | resName      | Residue name.                                  |
    | 22      | Character    | chainID      | Chain identifier.                              |
    | 23 - 26 | Integer      | resSeq       | Residue sequence number.                       |
    | 27      | AChar        | iCode        | Code for insertion of residues.                |
    | 31 - 38 | Real(8.3)    | x            | Orthogonal coordinates for X in Angstroms.     |
    | 39 - 46 | Real(8.3)    | y            | Orthogonal coordinates for Y in Angstroms.     |
    | 47 - 54 | Real(8.3)    | z            | Orthogonal coordinates for Z in Angstroms.     |
    | 55 - 60 | Real(6.2)    | occupancy    | Occupancy.                                     |
    | 61 - 66 | Real(6.2)    | tempFactor   | Temperature factor.                            |
    | 73 - 76 | LString(4)   | segID        | Segment identifier, left-justified.            |
    | 77 - 78 | LString(2)   | element      | Element symbol, right-justified.               |
    | 79 - 80 | LString(2)   | charge       | Charge on the atom.                            |
    |_________|______________|______________|________________________________________________|


    HETATM record
    -------------

    The HETATM record contains the atomic coordinates for atoms belonging to non-standard
    groups.  The format is of the record is:
    __________________________________________________________________________________________
    |         |              |              |                                                |
    | Columns | Data type    | Field        | Definition                                     |
    |_________|______________|______________|________________________________________________|
    |         |              |              |                                                |
    |  1 -  6 | Record name  | "HETATM"     |                                                |
    |  7 - 11 | Integer      | serial       | Atom serial number.                            |
    | 13 - 16 | Atom         | name         | Atom name.                                     |
    | 17      | Character    | altLoc       | Alternate location indicator.                  |
    | 18 - 20 | Residue name | resName      | Residue name.                                  |
    | 22      | Character    | chainID      | Chain identifier.                              |
    | 23 - 26 | Integer      | resSeq       | Residue sequence number.                       |
    | 27      | AChar        | iCode        | Code for insertion of residues.                |
    | 31 - 38 | Real(8.3)    | x            | Orthogonal coordinates for X.                  |
    | 39 - 46 | Real(8.3)    | y            | Orthogonal coordinates for Y.                  |
    | 47 - 54 | Real(8.3)    | z            | Orthogonal coordinates for Z.                  |
    | 55 - 60 | Real(6.2)    | occupancy    | Occupancy.                                     |
    | 61 - 66 | Real(6.2)    | tempFactor   | Temperature factor.                            |
    | 73 - 76 | LString(4)   | segID        | Segment identifier; left-justified.            |
    | 77 - 78 | LString(2)   | element      | Element symbol; right-justified.               |
    | 79 - 80 | LString(2)   | charge       | Charge on the atom.                            |
    |_________|______________|______________|________________________________________________|


    TER record
    ----------

    The end of the ATOM and HETATM records for a chain.  According to the draft atomic
    coordinate entry format description:

    "The TER record has the same residue name, chain identifier, sequence number and insertion
    code as the terminal residue. The serial number of the TER record is one number greater than
    the serial number of the ATOM/HETATM preceding the TER."

    The format is of the record is:
    __________________________________________________________________________________________
    |         |              |              |                                                |
    | Columns | Data type    | Field        | Definition                                     |
    |_________|______________|______________|________________________________________________|
    |         |              |              |                                                |
    |  1 -  6 | Record name  | "TER   "     |                                                |
    |  7 - 11 | Integer      | serial       | Serial number.                                 |
    | 18 - 20 | Residue name | resName      | Residue name.                                  |
    | 22      | Character    | chainID      | Chain identifier.                              |
    | 23 - 26 | Integer      | resSeq       | Residue sequence number.                       |
    | 27      | AChar        | iCode        | Insertion code.                                |
    |_________|______________|______________|________________________________________________|


    CONECT record
    -------------

    The connectivity between atoms.  This is required for all HET groups and for non-standard
    bonds.  The format is of the record is:
    __________________________________________________________________________________________
    |         |              |              |                                                |
    | Columns | Data type    | Field        | Definition                                     |
    |_________|______________|______________|________________________________________________|
    |         |              |              |                                                |
    |  1 -  6 | Record name  | "CONECT"     |                                                |
    |  7 - 11 | Integer      | serial       | Atom serial number                             |
    | 12 - 16 | Integer      | serial       | Serial number of bonded atom                   |
    | 17 - 21 | Integer      | serial       | Serial number of bonded atom                   |
    | 22 - 26 | Integer      | serial       | Serial number of bonded atom                   |
    | 27 - 31 | Integer      | serial       | Serial number of bonded atom                   |
    | 32 - 36 | Integer      | serial       | Serial number of hydrogen bonded atom          |
    | 37 - 41 | Integer      | serial       | Serial number of hydrogen bonded atom          |
    | 42 - 46 | Integer      | serial       | Serial number of salt bridged atom             |
    | 47 - 51 | Integer      | serial       | Serial number of hydrogen bonded atom          |
    | 52 - 56 | Integer      | serial       | Serial number of hydrogen bonded atom          |
    | 57 - 61 | Integer      | serial       | Serial number of salt bridged atom             |
    |_________|______________|______________|________________________________________________|


    MASTER record
    -------------

    The control record for bookkeeping.  The format is of the record is:
    __________________________________________________________________________________________
    |         |              |              |                                                |
    | Columns | Data type    | Field        | Definition                                     |
    |_________|______________|______________|________________________________________________|
    |         |              |              |                                                |
    |  1 -  6 | Record name  | "MASTER"     |                                                |
    | 11 - 15 | Integer      | numRemark    | Number of REMARK records                       |
    | 16 - 20 | Integer      | "0"          |                                                |
    | 21 - 25 | Integer      | numHet       | Number of HET records                          |
    | 26 - 30 | Integer      | numHelix     | Number of HELIX records                        |
    | 31 - 35 | Integer      | numSheet     | Number of SHEET records                        |
    | 36 - 40 | Integer      | numTurn      | Number of TURN records                         |
    | 41 - 45 | Integer      | numSite      | Number of SITE records                         |
    | 46 - 50 | Integer      | numXform     | Number of coordinate transformation records    |
    |         |              |              | (ORIGX+SCALE+MTRIX)                            |
    | 51 - 55 | Integer      | numCoord     | Number of atomic coordinate records            |
    |         |              |              | (ATOM+HETATM)                                  |
    | 56 - 60 | Integer      | numTer       | Number of TER records                          |
    | 61 - 65 | Integer      | numConect    | Number of CONECT records                       |
    | 66 - 70 | Integer      | numSeq       | Number of SEQRES records                       |
    |_________|______________|______________|________________________________________________|


    END record
    ----------

    The end of the PDB file.  The format is of the record is:
    __________________________________________________________________________________________
    |         |              |              |                                                |
    | Columns | Data type    | Field        | Definition                                     |
    |_________|______________|______________|________________________________________________|
    |         |              |              |                                                |
    |  1 -  6 | Record name  | "END   "     |                                                |
    |_________|______________|______________|________________________________________________|




    @param file:    The PDB file object.  This object must be writable.
    @type file:     file object
    @return:        None
    """

    # Sort the atoms.
    #################

    # Convert the atomic_data structure from a dictionary of arrays to an array of arrays and sort it by atom number.
    atomic_arrays = atomic_data.values()
    atomic_arrays.sort()


    # Collect the non-standard residue info.
    ########################################

    # Initialise some data.
    H_count = 0
    C_count = 0
    het_data = []

    # Loop over the atomic data.
    for array in atomic_arrays:
        # Skip all ATOM and TER records.
        if array[1] != 'HETATM':
            continue

        # The residue number and element.
        res_num = array[5]
        element = array[10]

        # If the residue is not already stored initialise a new het_data element.
        # (residue number, residue name, chain ID, number of atoms, number of H, number of C, number of N).
        if not het_data or not res_num == het_data[-1][0]:
            het_data.append([array[5], array[3], array[4], 0, 0, 0, 0])

        # Total atom count.
        het_data[-1][3] = het_data[-1][3] + 1

        # Proton count.
        if element == 'H':
            het_data[-1][4] = het_data[-1][4] + 1

        # Carbon count.
        elif element == 'C':
            het_data[-1][5] = het_data[-1][5] + 1

        # Nitrogen count.
        elif element == 'N':
            het_data[-1][6] = het_data[-1][6] + 1

        # Unsupported element type.
        else:
            raise RelaxError, "The element " + `element` + " was expected to be one of ['H', 'C', 'N']."


    # The HET records.
    ##################

    # Print out.
    print "Creating the HET records."

    # Write the HET records.
    for het in het_data:
        file.write("%-6s %3s  %1s%4s%1s  %5s     %-40s\n" % ('HET', het[2], het[1], het[0], '', het[3], ''))


    # The HETNAM records.
    #####################

    # Print out.
    print "Creating the HETNAM records."

    # Loop over the non-standard residues.
    residues = []
    for het in het_data:
        # Test if the residue HETNAM record as already been written (otherwise store its name).
        if het[1] in residues:
            continue
        else:
            residues.append(het[1])

        # Get the chemical name.
        chemical_name = get_chemical_name(het[1])

        # Write the HETNAM records.
        file.write("%-6s  %2s %3s %-55s\n" % ('HETNAM', '', het[1], chemical_name))


    # The FORMUL records.
    #####################

    # Print out.
    print "Creating the FORMUL records."

    # Loop over the non-standard residues and generate and write the chemical formula.
    residues = []
    for het in het_data:
        # Test if the residue HETNAM record as already been written (otherwise store its name).
        if het[1] in residues:
            continue
        else:
            residues.append(het[1])

        # Initialise the chemical formula.
        formula = ''

        # Protons.
        if het[4]:
            if formula:
                formula = formula + ' '
            formula = formula + 'H' + `het[4]`

        # Carbon.
        if het[5]:
            if formula:
                formula = formula + ' '
            formula = formula + 'C' + `het[5]`

        # Nitrogen
        if het[6]:
            if formula:
                formula = formula + ' '
            formula = formula + 'N' + `het[6]`

        # The FORMUL record (chemical formula).
        file.write("%-6s  %2s  %3s %2s%1s%-51s\n" % ('FORMUL', het[0], het[1], '', '', formula))


    # Add the atomic coordinate records (ATOM, HETATM, and TER).
    ############################################################

    # Print out.
    print "Creating the atomic coordinate records (ATOM, HETATM, and TER)."

    # Loop over the atomic data.
    for array in atomic_arrays:
        # Write the ATOM record.
        if array[1] == 'ATOM':
            file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('ATOM', array[0], array[2], '', array[3], array[4], array[5], '', array[6], array[7], array[8], 1.0, 0, array[9], array[10], ''))

        # Write the HETATM record.
        if array[1] == 'HETATM':
            file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('HETATM', array[0], array[2], '', array[3], array[4], array[5], '', array[6], array[7], array[8], 1.0, 0, array[9], array[10], ''))

        # Write the TER record.
        if array[1] == 'TER':
            file.write("%-6s%5s      %3s %1s%4s%1s\n" % ('TER', array[0], array[3], array[4], array[5], ''))


    # Create the CONECT records.
    ############################

    # Print out.
    print "Creating the CONECT records."

    connect_count = 0
    for array in atomic_arrays:
        # No bonded atoms, hence no CONECT record is required.
        if len(array) == 10:
            continue

        # The atom number.
        atom_num = array[0]

        # Initialise some data structures.
        flush = 0
        bonded_index = 0
        bonded = ['', '', '', '']

        # Loop over the bonded atoms.
        for i in xrange(len(array[11:])):
            # End of the array, hence create the CONECT record in this iteration.
            if i == len(array[11:])-1:
                flush = 1

            # Only four covalently bonded atoms allowed in one CONECT record.
            if bonded_index == 3:
                flush = 1

            # Get the bonded atom name.
            bonded[bonded_index] = array[i+11]

            # Increment the bonded_index value.
            bonded_index = bonded_index + 1

            # Generate the CONECT record and increment the counter.
            if flush:
                # Write the CONECT record.
                file.write("%-6s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('CONECT', atom_num, bonded[0], bonded[1], bonded[2], bonded[3], '', '', '', '', '', ''))

                # Increment the CONECT record count.
                connect_count = connect_count + 1

                # Reset the flush flag, the bonded atom count, and the bonded atom names.
                flush = 0
                bonded_index = 0
                bonded = ['', '', '', '']


    # MASTER record.
    ################

    # Print out.
    print "Creating the MASTER record."

    # Write the MASTER record.
    file.write("%-6s    %5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('MASTER', 0, 0, len(het_data), 0, 0, 0, 0, 0, len(atomic_data), 1, connect_count, 0))


    # END.
    ######

    # Print out.
    print "Creating the END record."

    # Write the END record.
    file.write("END\n")


def xh_vector(data, structure=None, unit=1):
    """Function for calculating/extracting the XH vector from the loaded structure.

    @param data:        The spin system data container.
    @type data:         Residue instance
    @param structure:   The structure number to get the XH vector from.  If set to None and
        multiple structures exist, then the XH vector will be averaged across all structures.
    @type structure:    int
    @param unit:        A flag which if set will cause the function to return the unit XH vector
        rather than the full vector.
    @type unit:         int
    @return:            The XH vector (or unit vector if the unit flag is set).
    @rtype:             list or None
    """

    # Initialise.
    vector_array = []
    ave_vector = zeros(3, float64)

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Number of structures.
    num_str = len(cdp.structure.structures)

    # Loop over the structures.
    for i in xrange(num_str):
        # The vectors from a specific structure.
        if structure != None and structure != i:
            continue

        # Reassign the first peptide or nucleotide chain of the first structure.
        if cdp.structure.structures[i].peptide_chains:
            pdb_residues = cdp.structure.structures[i].peptide_chains[0].residues
        elif cdp.structure.structures[i].nucleotide_chains:
            pdb_residues = cdp.structure.structures[i].nucleotide_chains[0].residues
        else:
            raise RelaxNoPdbChainError

        # Find the corresponding residue in the PDB.
        pdb_res = None
        for k in xrange(len(pdb_residues)):
            if data.num == pdb_residues[k].number:
                pdb_res = pdb_residues[k]
                break
        if pdb_res == None:
            raise RelaxNoResError, data.num

        # Test if the proton atom exists for residue i.
        if not pdb_res.atoms.has_key(data.proton):
            warn(RelaxNoAtomWarning(data.proton, data.num))

        # Test if the heteronucleus atom exists for residue i.
        elif not pdb_res.atoms.has_key(data.heteronuc):
            warn(RelaxNoAtomWarning(data.heteronuc, data.num))

        # Calculate the vector.
        else:
            # Get the proton position.
            posH = pdb_res.atoms[data.proton].position.array

            # Get the heteronucleus position.
            posX = pdb_res.atoms[data.heteronuc].position.array

            # Calculate the XH bond vector.
            vector = posH - posX

            # Unit vector.
            if unit:
                # Normalisation factor.
                norm_factor = sqrt(dot(vector, vector))

                # Test for zero length.
                if norm_factor == 0.0:
                    warn(RelaxZeroVectorWarning(data.num))

                # Calculate the normalised vector.
                else:
                    vector_array.append(vector / norm_factor)

            # Normal XH vector.
            else:
                vector_array.append(vector)

    # Return None if there are no vectors.
    if not len(vector_array):
        return

    # Sum the vectors.
    for vector in vector_array:
        # Sum.
        ave_vector = ave_vector + vector

    # Average the vector.
    ave_vector = ave_vector / len(vector_array)

    # Unit vector.
    if unit:
        ave_vector = ave_vector / sqrt(dot(ave_vector, ave_vector))

    # Return the vector.
    return ave_vector
