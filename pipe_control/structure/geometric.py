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
from math import pi
from os import getcwd

# relax module imports.
from lib.errors import RelaxNoPdbError, RelaxNoSequenceError, RelaxNoVectorsError
from lib.io import get_file_path, open_write_file
from lib.structure.internal.object import Internal
from lib.structure.represent.rotor import rotor_pdb
from pipe_control import pipes
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import exists_mol_res_spin_data, return_spin
from pipe_control.structure.mass import pipe_centre_of_mass
from status import Status; status = Status()


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
