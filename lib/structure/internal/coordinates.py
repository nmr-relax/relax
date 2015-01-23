###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
from numpy import array, float64


def assemble_coord_array(objects=None, object_names=None, molecules=None, models=None, atom_id=None, algorithm='NW70', matrix='BLOSUM62', gap_open_penalty=1.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0, seq_info_flag=False):
    """Assemble the atomic coordinates 
 
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
    @keyword algorithm:                 The pairwise sequence alignment algorithm to use.
    @type algorithm:                    str
    @keyword matrix:                    The substitution matrix to use.
    @type matrix:                       str
    @keyword gap_open_penalty:          The penalty for introducing gaps, as a positive number.
    @type gap_open_penalty:             float
    @keyword gap_extend_penalty:        The penalty for extending a gap, as a positive number.
    @type gap_extend_penalty:           float
    @keyword end_gap_open_penalty:      The optional penalty for opening a gap at the end of a sequence.
    @type end_gap_open_penalty:         float
    @keyword end_gap_extend_penalty:    The optional penalty for extending a gap at the end of a sequence.
    @type end_gap_extend_penalty:       float
    @keyword seq_info_flag:             A flag which if True will cause the atomic sequence information to be assembled and returned.  This includes the molecule names, residue names, residue numbers, atom names, and elements.
    @type seq_info_flag:                bool
    @return:                            The array of atomic coordinates (first dimension is the model and/or molecule, the second are the atoms, and the third are the coordinates); a list of unique IDs for each structural object, model, and molecule; the common list of molecule names (if the seq_info_flag is set); the common list of residue names (if the seq_info_flag is set); the common list of residue numbers (if the seq_info_flag is set); the common list of atom names (if the seq_info_flag is set); the common list of element names (if the seq_info_flag is set).
    @rtype:                             numpy rank-3 float64 array, list of str, list of str, list of str, list of int, list of str, list of str
    """

    # Assemble the atomic coordinates of all structures.
    print("Assembling all atomic coordinates:")
    ids = []
    atom_ids = []
    atom_pos = []
    mol_names = []
    res_names = []
    res_nums = []
    atom_names = []
    elements = []
    for struct_index in range(len(objects)):
        # Printout.
        print("    Data pipe: %s" % object_names[struct_index])

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

            # Create a new structure ID for all the molecules of this model (if the molecules argument is not supplied).
            if molecules == None:
                if len(object_names) > 1 and num_models > 1:
                    ids.append('%s, model %i' % (object_names[struct_index], model.num))
                elif len(object_names) > 1:
                    ids.append('%s' % (object_names[struct_index]))
                elif num_models > 1:
                    ids.append('model %i' % (model.num))
                else:
                    ids.append(None)

            # Extend the lists.
            if molecules == None:
                atom_ids.append([])
                atom_pos.append({})
                if seq_info_flag:
                    mol_names.append({})
                    res_names.append({})
                    res_nums.append({})
                    atom_names.append({})
                    elements.append({})

            # Add all coordinates and elements.
            current_mol = ''
            for mol_name, res_num, res_name, atom_name, elem, pos in objects[struct_index].atom_loop(selection=selection, model_num=model.num, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_name_flag=True, pos_flag=True, element_flag=True):
                # No molecule match, so skip.
                if molecules != None and mol_name not in molecules[struct_index]:
                    continue

                # A new molecule.
                if mol_name != current_mol:
                    # Printout.
                    print("            Molecule: %s" % mol_name)

                    # Change the current molecule name.
                    current_mol = mol_name

                    # Extend the lists.
                    if molecules != None:
                        atom_ids.append([])
                        atom_pos.append({})
                        if seq_info_flag:
                            mol_names.append({})
                            res_names.append({})
                            res_nums.append({})
                            atom_names.append({})
                            elements.append({})

                    # Create a new structure ID.
                    if molecules != None:
                        if len(object_names) > 1 and num_models > 1:
                            ids.append('%s, model %i, %s' % (object_names[struct_index], model.num, mol_name))
                        elif len(object_names) > 1:
                            ids.append('%s, %s' % (object_names[struct_index], mol_name))
                        elif num_models > 1:
                            ids.append('model %i, %s' % (model.num, mol_name))
                        else:
                            ids.append('%s' % mol_name)

                # A unique identifier.
                if molecules != None:
                    id = ":%s&%s@%s" % (res_num, res_name, atom_name)
                else:
                    id = "#%s:%s&%s@%s" % (mol_name, res_num, res_name, atom_name)

                # Store the per-structure ID and coordinate.
                atom_ids[-1].append(id)
                atom_pos[-1][id] = pos[0]

                # Store the per-structure sequence information.
                if seq_info_flag:
                    mol_names[-1][id] = mol_name
                    res_names[-1][id] = res_name
                    res_nums[-1][id] = res_num
                    atom_names[-1][id] = atom_name
                    elements[-1][id] = elem

    # Set up the structures for the superimposition algorithm.
    num = len(atom_ids)
    coord = []
    mol_name_common = []
    res_name_common = []
    res_num_common = []
    atom_name_common = []
    element_common = []
    for i in range(num):
        coord.append([])

    # Find the common atoms and create the coordinate data structure.
    for id in atom_ids[0]:
        # Is the atom ID present in all other structures?
        present = True
        for i in range(num):
            if id not in atom_ids[i]:
                present = False
                break

        # Not present, so skip the atom.
        if not present:
            continue

        # Add the atomic position to the coordinate list and the element to the element list.
        for i in range(num):
            coord[i].append(atom_pos[i][id])

        # The common sequence information.
        if seq_info_flag:
            mol_name_common.append(mol_names[0][id])
            res_name_common.append(res_names[0][id])
            res_num_common.append(res_nums[0][id])
            atom_name_common.append(atom_names[0][id])
            element_common.append(elements[0][id])

    # Convert to a numpy array.
    coord = array(coord, float64)

    # Return the information.
    if seq_info_flag:
        return coord, ids, mol_name_common, res_name_common, res_num_common, atom_name_common, element_common
    else:
        return coord, ids


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
