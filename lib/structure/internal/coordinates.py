###############################################################################
#                                                                             #
# Copyright (C) 2014-2015 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module for handling atomic coordinate information."""

# Python module imports.
from numpy import array, float64, int16, zeros

# relax module imports.
from lib.errors import RelaxFault


def assemble_atomic_coordinates(objects=None, object_names=None, molecules=None, models=None, atom_id=None):
    """Assemble the atomic coordinates of all structures.

    @keyword objects:                   The list of internal structural objects to assemble the coordinates from.
    @type objects:                      list of str
    @keyword object_names:              The list of names for each structural object to use in printouts.
    @type object_names:                 list of str
    @keyword models:                    The list of models for each structural object.  The number of elements must match the objects argument.  If set to None, then all models will be used.
    @type models:                       None or list of lists of int
    @keyword molecules:                 The list of molecules for each structural object.  The number of elements must match the objects argument.  If set to None, then all molecules will be used.
    @type molecules:                    None or list of lists of str
    @keyword atom_id:                   The molecule, residue, and atom identifier string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:                      None or str
    @return:                            The list of structure IDs for each molecule, the object ID list per molecule, the model number list per molecule, the molecule name list per molecule, the atom positions per molecule and per residue, the molecule names per molecule and per residue, the residue names per molecule and per residue, the residue numbers per molecule and per residue, the atom names per molecule and per residue, the atomic elements per molecule and per residue, the one letter codes for the residue sequence, the number of molecules.
    @rtype:                             list of str, list of str, list of int, list of str, list of list of dict of str, list of list of dict of str, list of list of dict of str, list of list of dict of str, list of list of dict of str, list of list of dict of str, list of str, int
    """

    print("Assembling all atomic coordinates:")
    ids = []
    object_id_list = []
    model_list = []
    molecule_list = []
    atom_pos = []
    mol_names = []
    res_names = []
    res_nums = []
    atom_names = []
    elements = []
    one_letter_codes = []
    for struct_index in range(len(objects)):
        # Printout.
        print("    Object ID: %s" % object_names[struct_index])

        # Validate the models.
        objects[struct_index].validate_models(verbosity=0)

        # The number of models.
        num_models = objects[struct_index].num_models()

        # The selection object.
        selection = objects[struct_index].selection(atom_id=atom_id)

        # Loop over the models.
        for model in objects[struct_index].model_loop():
            # No model match.
            if models != None and model.num not in models[struct_index]:
                continue

            # Printout.
            print("        Model: %s" % model.num)

            # Add all coordinates and elements.
            current_mol = ''
            current_res = None
            for mol_name, res_num, res_name, atom_name, elem, pos in objects[struct_index].atom_loop(selection=selection, model_num=model.num, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_name_flag=True, pos_flag=True, element_flag=True):
                # No molecule match, so skip.
                if molecules != None and mol_name not in molecules[struct_index]:
                    continue

                # A new molecule.
                if mol_name != current_mol:
                    # Printout.
                    print("            Molecule: %s" % mol_name)

                    # Change the current molecule name and residue number.
                    current_mol = mol_name
                    current_res = None

                    # Update the molecule lists.
                    object_id_list.append(object_names[struct_index])
                    model_list.append(model.num)
                    molecule_list.append(mol_name)

                    # Store the one letter codes for sequence alignment.
                    one_letter_codes.append(objects[struct_index].one_letter_codes(mol_name=mol_name, selection=selection))

                    # Extend the lists.
                    atom_names.append([])
                    atom_pos.append([])
                    mol_names.append([])
                    res_names.append([])
                    res_nums.append([])
                    elements.append([])

                    # Create a new structure ID.
                    if len(object_names) > 1 and num_models > 1:
                        ids.append('%s, model %i, %s' % (object_names[struct_index], model.num, mol_name))
                    elif len(object_names) > 1:
                        ids.append('%s, %s' % (object_names[struct_index], mol_name))
                    elif num_models > 1:
                        ids.append('model %i, %s' % (model.num, mol_name))
                    else:
                        ids.append('%s' % mol_name)

                # A new residue.
                if res_num != current_res:
                    # Change the current residue
                    current_res = res_num

                    # Extend the lists.
                    atom_names[-1].append([])
                    atom_pos[-1].append({})
                    mol_names[-1].append({})
                    res_names[-1].append({})
                    res_nums[-1].append({})
                    elements[-1].append({})

                # Store the per-structure ID and coordinate.
                atom_names[-1][-1].append(atom_name)
                atom_pos[-1][-1][atom_name] = pos[0]

                # Store the per-structure sequence information.
                mol_names[-1][-1][atom_name] = mol_name
                res_names[-1][-1][atom_name] = res_name
                res_nums[-1][-1][atom_name] = res_num
                elements[-1][-1][atom_name] = elem

    # The total number of molecules.
    num_mols = len(atom_names)

    # Return the data.
    return ids, object_id_list, model_list, molecule_list, atom_pos, mol_names, res_names, res_nums, atom_names, elements, one_letter_codes, num_mols


def assemble_coord_array(atom_pos=None, mol_names=None, res_names=None, res_nums=None, atom_names=None, elements=None, sequences=None, skip=None):
    """Assemble the atomic coordinates as a numpy array.
 
    @keyword sequences: The list of residue sequences for the alignment as one letter codes.
    @type sequences:    list of str
    @return:            The array of atomic coordinates (first dimension is the model and/or molecule, the second are the atoms, and the third are the coordinates); the common list of molecule names; the common list of residue names; the common list of residue numbers; the common list of atom names; the common list of element names.
    @rtype:             numpy rank-3 float64 array, list of str, list of str, list of int, list of str, list of str
    """

    # No data to assemble.
    if mol_names == []:
        return [], [], [], [], [], []

    # Set up the structures for common coordinates.
    num_mols = len(skip)
    coord = []
    mol_name_common = []
    res_name_common = []
    res_num_common = []
    atom_name_common = []
    element_common = []
    for mol_index in range(num_mols):
        coord.append([])

    # Find the common atoms and create the coordinate data structure.
    res_indices = [-1]*num_mols
    max_res = -1
    for mol_index in range(num_mols):
        if len(sequences[mol_index]) > max_res:
            max_res = len(sequences[mol_index])
    while 1:
        # Move to the next non-skipped residues in each molecule.
        for mol_index in range(num_mols):
            terminate = False
            while 1:
                res_indices[mol_index] += 1
                if res_indices[mol_index] >= len(skip[mol_index]):
                    terminate = True
                    break
                if not skip[mol_index][res_indices[mol_index]]:
                    break

        # Termination.
        for mol_index in range(num_mols):
            if res_indices[0] >= len(atom_names[0]):
                terminate = True
            if res_indices[mol_index] >= len(atom_names[mol_index]):
                terminate = True
        if terminate:
            break

        # Loop over the residue atoms in the first molecule.
        for atom_name in atom_names[0][res_indices[0]]:
            # Is the atom ID present in all other structures?
            present = True
            for mol_index in range(1, num_mols):
                if atom_name not in atom_names[mol_index][res_indices[mol_index]]:
                    present = False
                    break

            # Not present, so skip the atom.
            if not present:
                continue

            # Add the atomic position to the coordinate list and the element to the element list.
            for mol_index in range(num_mols):
                coord[mol_index].append(atom_pos[mol_index][res_indices[mol_index]][atom_name])

            # The common sequence information.
            mol_name_common.append(mol_names[0][res_indices[0]][atom_name])
            res_name_common.append(res_names[0][res_indices[0]][atom_name])
            res_num_common.append(res_nums[0][res_indices[0]][atom_name])
            atom_name_common.append(atom_name)
            element_common.append(elements[0][res_indices[0]][atom_name])

    # Convert to a numpy array.
    coord = array(coord, float64)

    # Return the information.
    return coord, mol_name_common, res_name_common, res_num_common, atom_name_common, element_common


def generate_id(object_id=None, model=None, molecule=None):
    """Generate a unique ID.

    @keyword object_id: The structural object ID.
    @type object_id:    str
    @keyword model:     The model number.
    @type model:        int
    @keyword molecule:  The molecule name.
    @type molecule:     str
    @return:            The unique ID constructed from the object ID, model number and molecule name.
    @rtype:             str
    """

    # Init.
    id = ''

    # The object ID.
    if object_id != None:
        id += "Object '%s'" % object_id

    # The model number.
    if model != None:
        if len(id):
            id += '; '
        id += "Model %i" % model

    # The molecule name.
    if len(id):
        id += '; '
    if molecule != None:
        id += "Molecule '%s'" % molecule

    # Sanity check.
    if not len(id):
        raise RelaxError("No alignment ID could be constructed.")

    # Return the ID.
    return id


def loop_coord_structures(objects=None, molecules=None, models=None, atom_id=None):
    """Generator function for looping over all internal structural objects, models and molecules.
 
    @keyword objects:       The list of internal structural objects to loop over.
    @type objects:          list of str
    @keyword models:        The list of models for each structural object.  The number of elements must match the objects argument.  If set to None, then all models will be used.
    @type models:           None or list of lists of int
    @keyword molecules:     The list of molecules for each structural object.  The number of elements must match the objects argument.  If set to None, then all molecules will be used.
    @type molecules:        None or list of lists of str
    @keyword atom_id:       The molecule, residue, and atom identifier string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:          None or str
    @return:                The structural object index, model number, and molecule name.
    @rtype:                 int, int or None, str
    """

    # Loop over all structural objects.
    for struct_index in range(len(objects)):
        # Validate the models.
        objects[struct_index].validate_models(verbosity=0)

        # The number of models.
        num_models = objects[struct_index].num_models()

        # The selection object.
        selection = objects[struct_index].selection(atom_id=atom_id)

        # Loop over the models.
        for model in objects[struct_index].model_loop():
            # No model match.
            if models != None and model.num not in models[struct_index]:
                continue

            # Coordinate loop.
            current_mol = ''
            for mol_name, res_num, res_name, atom_name, elem, pos in objects[struct_index].atom_loop(selection=selection, model_num=model.num, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_name_flag=True, pos_flag=True, element_flag=True):
                # No molecule match, so skip.
                if molecules != None and mol_name not in molecules[struct_index]:
                    continue

                # A new molecule.
                if mol_name != current_mol:
                    # Change the current molecule name.
                    current_mol = mol_name

                    # Yield the data.
                    yield struct_index, model.num, mol_name
