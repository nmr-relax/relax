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


def assemble_coord_array(objects=None, object_names=None, molecules=None, models=None, atom_id=None, elements_flag=False):
    """Assemble the atomic coordinates 
 
    @keyword objects:       The list of internal structural objects to assemble the coordinates from.
    @type objects:          list of str
    @keyword object_names:  The list of names for each structural object to use in printouts.
    @type object_names:     list of str
    @keyword models:        The list of models for each structural object.  The number of elements must match the objects argument.  If set to None, then all models will be used.
    @type models:           None or list of lists of int
    @keyword molecules:     The list of molecules for each structural object.  The number of elements must match the objects argument.  If set to None, then all molecules will be used.
    @type molecules:        None or list of lists of str
    @keyword atom_id:       The molecule, residue, and atom identifier string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:          None or str
    @return:                The array of atomic coordinates (first dimension is the model and/or molecule, the second are the atoms, and the third are the coordinates); a list of unique IDs for each structural object, model, and molecule; the list of element names for each atom (if the elements flag is set).
    @rtype:                 numpy rank-3 float64 array, list of str, list of str
    """

    # Assemble the atomic coordinates of all structures.
    print("Assembling all atomic coordinates:")
    ids = []
    atom_ids = []
    atom_pos = []
    atom_elem = []
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

            # Extend the lists.
            if molecules == None:
                atom_ids.append([])
                atom_pos.append({})
                atom_elem.append({})

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
                        atom_elem.append({})

                    # Create a new structure ID.
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

                atom_ids[-1].append(id)
                atom_pos[-1][id] = pos[0]
                atom_elem[-1][id] = elem

    # Set up the structures for the superimposition algorithm.
    num = len(atom_ids)
    coord = []
    elements = []
    for i in range(num):
        coord.append([])
        elements.append([])

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
            elements[i].append(atom_elem[i][id])

    # Convert to a numpy array.
    coord = array(coord, float64)

    # Return the information.
    if elements_flag:
        return coord, ids, elements
    else:
        return coord, ids
