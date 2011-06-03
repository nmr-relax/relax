###############################################################################
#                                                                             #
# Copyright (C) 2003-2010 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module containing the Scientific Python PDB specific structural object class."""

# Dependency check module.
import dep_check

# Python module imports.
from math import sqrt
from numpy import array, dot, float64, zeros
import os
from os import F_OK, access, sep
from extern.scientific_python.IO import PDB
import sys
from warnings import warn

# relax module imports.
from api_base import Base_struct_API
from data.relax_xml import fill_object_contents, xml_to_object
from generic_fns import pipes, relax_re
from generic_fns.mol_res_spin import Selection, generate_spin_id, parse_token, tokenise
from relax_errors import RelaxError, RelaxPdbLoadError
from relax_io import file_root
from relax_warnings import RelaxWarning, RelaxNoAtomWarning, RelaxNoPDBFileWarning, RelaxZeroVectorWarning


class Scientific_data(Base_struct_API):
    """The Scientific Python specific data object."""

    # Identification string.
    id = 'scientific'

    def __init__(self):
        """Initialise the class."""

        # Test for the PDB parser availability.
        if not dep_check.scientific_pdb_module:
            raise RelaxError("The Scientific python PDB module scientific_python.IO.PDB could not be imported.")

        # Execute the base class __init__() method.
        Base_struct_API.__init__(self)


    def __find_bonded_atom(self, attached_atom, mol_type, res):
        """Find the atom named attached_atom directly bonded to the desired atom.

        @param attached_atom:   The name of the attached atom to return.
        @type attached_atom:    str
        @param mol_type:        The type of the molecule.  This can be one of 'protein', 'nucleic acid',
                                or 'other'.
        @type mol_type:         str
        @param res:             The Scientific Python residue object.
        @type res:              Scientific Python residue instance
        @return:                A tuple of information about the bonded atom.
        @rtype:                 tuple consisting of the atom number (int), atom name (str), element
                                name (str), and atomic position (Numeric array of len 3)
        """

        # Init.
        bonded_found = False

        # The find the attached atom in the residue (FIXME).
        matching_list = []
        for atom in list(res.atoms.keys()):
            if relax_re.search(atom, attached_atom):
                matching_list.append(atom)
        num_attached = len(matching_list)

        # Problem.
        if num_attached > 1:
            return None, None, None, None, None, 'More than one attached atom found: ' + repr(matching_list)

        # No attached atoms.
        if num_attached == 0:
            return None, None, None, None, None, "No attached atom could be found"

        # The bonded atom object.
        bonded = res[attached_atom]

        # The bonded atom info.
        bonded_num = bonded.properties['serial_number']
        bonded_name = bonded.name
        element = bonded.properties['element']
        pos = bonded.position.array
        attached_name = matching_list[0]

        # Return the information.
        return bonded_num, bonded_name, element, pos, attached_name, None


    def __residue_loop(self, mol, sel_obj=None):
        """Generator function for looping over all residues in the Scientific PDB data objects.

        @param mol:         The individual molecule Scientific Python PDB data object.
        @type mol:          Scientific Python PDB object
        @keyword sel_obj:   The selection object.
        @type sel_obj:      instance of generic_fns.mol_res_spin.Selection
        @return:            A tuple of the Scientific Python PDB object representing a single
                            residue, the residue number, and residue name.
        @rtype:             (Scientific Python PDB object, str, str)
        """

        # Proteins, RNA, and DNA.
        if mol.mol_type != 'other':
            # Loop over the residues of the protein in the PDB file.
            res_index = -1
            for res in mol.data.residues:
                # Residue number and name.
                if mol.mol_type == 'nucleic acid':
                    res_name = res.name[-1]
                else:
                    res_name = res.name
                res_num = res.number

                # Residue index.
                res_index = res_index + 1

                # Skip non-matching residues.
                if sel_obj and not sel_obj.contains_res(res_num, res_name, mol.mol_name):
                    continue

                # Yield the residue info.
                yield res, res_num, res_name, res_index

        # Other molecules.
        else:
            res_index = -1
            for res in mol.data:
                # Residue index.
                res_index = res_index + 1

                # Skip non-matching residues.
                if sel_obj and not sel_obj.contains_res(res.number, res.name, mol.mol_name):
                    continue

                # Yield the residue info.
                yield res, res.number, res.name, res_index


    def atom_loop(self, atom_id=None, str_id=None, model_num_flag=False, mol_name_flag=False, res_num_flag=False, res_name_flag=False, atom_num_flag=False, atom_name_flag=False, element_flag=False, pos_flag=False, ave=False):
        """Generator function for looping over all atoms in the Scientific Python data objects.

        @keyword atom_id:           The molecule, residue, and atom identifier string.  Only atoms
                                    matching this selection will be yielded.
        @type atom_id:              str
        @keyword str_id:            The structure identifier.  This can be the file name, model
                                    number, or structure number.  If None, then all structures will
                                    be looped over.
        @type str_id:               str, int, or None
        @keyword model_num_flag:    A flag which if True will cause the model number to be yielded.
        @type model_num_flag:       bool
        @keyword mol_name_flag:     A flag which if True will cause the molecule name to be yielded.
        @type mol_name_flag:        bool
        @keyword res_num_flag:      A flag which if True will cause the residue number to be
                                    yielded.
        @type res_num_flag:         bool
        @keyword res_name_flag:     A flag which if True will cause the residue name to be yielded.
        @type res_name_flag:        bool
        @keyword atom_num_flag:     A flag which if True will cause the atom number to be yielded.
        @type atom_num_flag:        bool
        @keyword atom_name_flag:    A flag which if True will cause the atom name to be yielded.
        @type atom_name_flag:       bool
        @keyword element_flag:      A flag which if True will cause the element name to be yielded.
        @type element_flag:         bool
        @keyword pos_flag:          A flag which if True will cause the atomic position to be
                                    yielded.
        @type pos_flag:             bool
                                    average atom properties across all loaded structures.
        @type ave:                  bool
        @return:                    A tuple of atomic information, as described in the docstring.
        @rtype:                     tuple consisting of optional molecule name (str), residue number
                                    (int), residue name (str), atom number (int), atom name(str),
                                    element name (str), and atomic position (array of len 3).
        """

        # Generate the selection object.
        sel_obj = Selection(atom_id)

        # Model loop.
        for model in self.model_loop():
            # Loop over the molecules.
            for mol_index in range(len(model.mol)):
                mol = model.mol[mol_index]

                # Skip non-matching molecules.
                if sel_obj and not sel_obj.contains_mol(mol.mol_name):
                    continue

                # Loop over the residues.
                for res, res_num, res_name, res_index in self.__residue_loop(mol, sel_obj):
                    # Loop over the atoms of the residue.
                    atom_index = -1
                    for atom in res:
                        # Atom number, name, index, and element type.
                        atom_num = atom.properties['serial_number']
                        atom_name = atom.name
                        element = atom.properties['element']
                        atom_index = atom_index + 1

                        # Skip non-matching atoms.
                        if sel_obj and not sel_obj.contains_spin(atom_num, atom_name, res_num, res_name, mol.mol_name):
                            continue

                        # The atom position.
                        if ave:
                            pos = self.__ave_atom_pos(mol_index, res_index, atom_index)
                        else:
                            pos = atom.position.array

                        # The molecule name.
                        mol_name = mol.mol_name

                        # Replace empty variables with None.
                        if not mol.mol_name:
                            mol_name = None
                        if not res_num:
                            res_num = None
                        if not res_name:
                            res_name = None
                        if not atom_num:
                            atom_num = None
                        if not atom_name:
                            atom_name = None

                        # Build the tuple to be yielded.
                        atomic_tuple = ()
                        if model_num_flag:
                            if ave:
                                atomic_tuple = atomic_tuple + (None,)
                            else:
                                atomic_tuple = atomic_tuple + (model.num,)
                        if mol_name_flag:
                            atomic_tuple = atomic_tuple + (mol_name,)
                        if res_num_flag:
                            atomic_tuple = atomic_tuple + (res_num,)
                        if res_name_flag:
                            atomic_tuple = atomic_tuple + (res_name,)
                        if atom_num_flag:
                            atomic_tuple = atomic_tuple + (atom_num,)
                        if atom_name_flag:
                            atomic_tuple = atomic_tuple + (atom_name,)
                        if element_flag:
                            atomic_tuple = atomic_tuple + (element,)
                        if pos_flag:
                            atomic_tuple = atomic_tuple + (pos,)

                        # Yield the information.
                        yield atomic_tuple

            # Break out of the loop if the ave flag is set, as data from only one model is used.
            if ave:
                break


    def attached_atom(self, atom_id=None, attached_atom=None, model=None):
        """Find the atom corresponding to 'attached_atom' which is bonded to the atom of 'atom_id'.

        @keyword atom_id:       The molecule, residue, and atom identifier string.  This must
                                correspond to a single atom in the system.
        @type atom_id:          str
        @keyword attached_atom: The name of the attached atom to return.
        @type attached_atom:    str
        @keyword model:         The model to return the positional information from.  If not
                                supplied and multiple models exist, then the returned atomic
                                position will be a list of the positions in each model.
        @type model:            None or int
        @return:                A tuple of information about the bonded atom.
        @rtype:                 tuple consisting of the atom number (int), atom name (str), element
                                name (str), and atomic positions for each model (list of numpy
                                arrays)
        """

        # Generate the selection object.
        sel_obj = Selection(atom_id)

        # Initialise some objects.
        bonded_num = None
        bonded_name = None
        element = None
        pos_array = []

        # Loop over the models.
        for model in self.model_loop(model):
            # Init.
            atom_found = False

            # Loop over each individual molecule.
            for mol in model.mol:
                # Loop over the residues of the protein in the PDB file.
                for res, res_num, res_name, res_index in self.__residue_loop(mol, sel_obj):
                    # Loop over the atoms of the residue.
                    for atom in res:
                        # Atom number, name, and position.
                        atom_num = atom.properties['serial_number']
                        atom_name = atom.name

                        # Skip non-matching atoms.
                        if sel_obj and not sel_obj.contains_spin(atom_num, atom_name, res_num, res_name, mol.mol_name):
                            continue

                        # More than one matching atom!
                        if atom_found:
                            raise RelaxError("The atom_id argument " + repr(atom_id) + " must correspond to a single atom.")

                        # The atom has been found, so store some info.
                        atom_found = True
                        atom_num_match = atom_num
                        atom_name_match = atom_name
                        mol_type_match = mol.mol_type
                        res_match = res

            # Found the atom.
            if atom_found:
                # Find the atom bonded to this model/molecule/residue/atom.
                bonded_num, bonded_name, element, pos = self.__find_bonded_atom(attached_atom, mol_type_match, res_match)

                # Append the position to the position array (converting from a Numeric array to a numpy array).
                pos_array.append(array(pos, float64))

        # Return the atom info.
        return bonded_num, bonded_name, element, pos_array


    def __ave_atom_pos(self, mol_index, res_index, atom_index):
        """Determine the average atom position across all models.

        @param mol_index:   The molecule index.
        @type mol_index:    int
        @param res_index:   The residue index.
        @type res_index:    int
        @param atom_index:  The atom index.
        @type atom_index:   int
        """

        # Init.
        pos = zeros(3, float64)

        # Loop over the models.
        for model in self.model_loop():
            # The exact molecule.
            mol = model.mol[mol_index]

            # The residue.
            if mol.mol_type != 'other':
                res = mol.data.residues[res_index]
            else:
                res = mol.data[res_index]

            # The atom.
            atom = res[atom_index]

            # Sum the position.
            pos = pos + atom.position.array

        # Average the position array.
        pos = pos / len(self.structural_data)

        # Return the ave position.
        return pos


    def bond_vectors(self, attached_atom=None, model_num=None, mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None, return_name=False, return_warnings=False):
        """Find the bond vectors between the atoms of 'attached_atom' and 'atom_id'.

        @keyword attached_atom:     The name of the bonded atom.
        @type attached_atom:        str
        @keyword model_num:         The model of which to return the vectors from.  If not supplied
                                    and multiple models exist, then vectors from all models will be
                                    returned.
        @type model_num:            None or int
        @keyword mol_name:          The name of the molecule that attached_atom belongs to.
        @type mol_name:             str
        @keyword res_num:           The number of the residue that attached_atom belongs to.
        @type res_num:              str
        @keyword res_name:          The name of the residue that attached_atom belongs to.
        @type res_name:             str
        @keyword spin_num:          The number of the spin that attached_atom is attached to.
        @type spin_num:             str
        @keyword spin_name:         The name of the spin that attached_atom is attached to.
        @type spin_name:            str
        @keyword return_name:       A flag which if True will cause the name of the attached atom to
                                    be returned together with the bond vectors.
        @type return_name:          bool
        @keyword return_warnings:   A flag which if True will cause warning messages to be returned.
        @type return_warnings:      bool
        @return:                    The list of bond vectors for each structure.
        @rtype:                     list of numpy arrays
        """

        # Generate the selection object.
        sel_obj = Selection(generate_spin_id(mol_name, res_num, res_name, spin_num, spin_name))

        # Initialise some objects.
        vectors = []
        attached_name = None
        warnings = None

        # Loop over the models.
        for model in self.model_loop(model_num):
            # Init.
            atom_found = False

            # Loop over each individual molecule.
            for mol in model.mol:
                # Loop over the residues of the protein in the PDB file.
                for res, res_num, res_name, res_index in self.__residue_loop(mol, sel_obj):
                    # Loop over the atoms of the residue.
                    for atom in res:
                        # Atom number, name, and position.
                        atom_num = atom.properties['serial_number']
                        atom_name = atom.name

                        # Skip non-matching atoms.
                        if sel_obj and not sel_obj.contains_spin(atom_num, atom_name, res_num, res_name, mol.mol_name):
                            continue

                        # More than one matching atom!
                        if atom_found:
                            raise RelaxError("The atom_id argument " + repr(atom_id) + " must correspond to a single atom.")

                        # The atom has been found, so store some info.
                        atom_found = True
                        pos_match = atom.position.array
                        mol_type_match = mol.mol_type
                        res_match = res

            # Found the atom.
            if atom_found:
                # Find the atom bonded to this structure/molecule/residue/atom.
                bonded_num, bonded_name, element, pos, attached_name, warnings = self.__find_bonded_atom(attached_atom, mol_type_match, res_match)

                # No bonded atom.
                if (bonded_num, bonded_name, element) == (None, None, None):
                    continue

                # The bond vector.
                vector = pos - pos_match

                # Append the vector to the vectors array (converting from a Numeric array to a numpy array).
                vectors.append(array(vector, float64))

        # Build the tuple to be yielded.
        data = (vectors,)
        if return_name:
            data = data + (attached_name,)
        if return_warnings:
            data = data + (warnings,)

        # Return the data.
        return data


    def load_pdb(self, file_path, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, verbosity=False):
        """Function for loading the structures from the PDB file.

        @param file_path:       The full path of the file.
        @type file_path:        str
        @keyword read_mol:      The molecule(s) to read from the file, independent of model.  The
                                molecules are determined differently by the different parsers, but
                                are numbered consecutively from 1.  If set to None, then all
                                molecules will be loaded.
        @type read_mol:         None, int, or list of int
        @keyword set_mol_name:  Set the names of the molecules which are loaded.  If set to None,
                                then the molecules will be automatically labelled based on the file
                                name or other information.
        @type set_mol_name:     None, str, or list of str
        @keyword read_model:    The PDB model to extract from the file.  If set to None, then all
                                models will be loaded.
        @type read_model:       None, int, or list of int
        @keyword set_model_num: Set the model number of the loaded molecule.  If set to None, then
                                the PDB model numbers will be preserved, if they exist.
        @type set_model_num:    None, int, or list of int
        @keyword verbosity:     A flag which if True will cause messages to be printed.
        @type verbosity:        bool
        @return:                The status of the loading of the PDB file.
        @rtype:                 bool
        """

        # Initial print out.
        if verbosity:
            print("\nScientific Python PDB parser.")

        # Test if the file exists.
        if not access(file_path, F_OK):
            # Exit indicating failure.
            return False

        # Separate the file name and path.
        path, file = os.path.split(file_path)

        # Convert the structure reading args into lists.
        if read_mol and not isinstance(read_mol, list):
            read_mol = [read_mol]
        if set_mol_name and not isinstance(set_mol_name, list):
            set_mol_name = [set_mol_name]
        if read_model and not isinstance(read_model, list):
            read_model = [read_model]
        if set_model_num and not isinstance(set_model_num, list):
            set_model_num = [set_model_num]

        # Load all models.
        model_flag = True
        model_num = 1
        model_load_num = 1
        orig_model_num = []
        mol_conts = []
        while True:
            # Only load the desired model.
            if read_model:
                # No more models to read.
                if model_num > max(read_model):
                    break

                # Skip the model if not in the list.
                if model_num not in read_model:
                    # Increment the model counter.
                    model_num = model_num + 1

                    # Jump to the next model.
                    continue

            # Load the PDB file.
            model = PDB.Structure(file_path, model_num)

            # No model 1.
            if not len(model) and not len(mol_conts):
                # Load the PDB without a model number.
                model = PDB.Structure(file_path)
                model_flag = False

                # Ok, nothing is loadable from this file.
                if not len(model):
                    raise RelaxPdbLoadError(file_path)

            # Test if the last structure has been reached.
            if not len(model):
                del model
                break

            # Append an empty list to the molecule container structure for a new model, set the molecule index, and initialise the target name structure.
            mol_conts.append([])
            mol_index = 0
            new_mol_name = []

            # Set the target molecule number offset (if molecules already exist).
            mol_offset = 0
            for i in range(len(self.structural_data)):
                model_index = model_load_num - 1
                if not set_model_num or (model_index <= len(set_model_num) and set_model_num[model_index] == self.structural_data[i].num):
                    mol_offset = len(self.structural_data[i].mol)

            # Store the original model number.
            orig_model_num.append(model_num)

            # Print the PDB info.
            if verbosity:
                print(model)

            # First add the peptide chains (generating the molecule names and incrementing the molecule index).
            if hasattr(model, 'peptide_chains'):
                for mol in model.peptide_chains:
                    # Only read the required molecule.
                    if read_mol and mol_index+1 not in read_mol:
                        mol_index = mol_index + 1
                        continue

                    mol.mol_type = 'protein'
                    mol_conts[-1].append(MolContainer())
                    mol_conts[-1][-1].data = mol
                    mol_conts[-1][-1].mol_type = 'protein'
                    self.target_mol_name(set=set_mol_name, target=new_mol_name, index=mol_index, mol_num=mol_index+1+mol_offset, file=file)
                    mol_index = mol_index + 1

            # Then the nucleotide chains (generating the molecule names and incrementing the molecule index).
            if hasattr(model, 'nucleotide_chains'):
                for mol in model.nucleotide_chains:
                    # Only read the required molecule.
                    if read_mol and mol_index+1 not in read_mol:
                        mol_index = mol_index + 1
                        continue

                    mol_conts[-1].append(MolContainer())
                    mol_conts[-1][-1].data = mol
                    mol_conts[-1][-1].mol_type = 'nucleic acid'
                    self.target_mol_name(set=set_mol_name, target=new_mol_name, index=mol_index, mol_num=mol_index+1+mol_offset, file=file)
                    mol_index = mol_index + 1

            # Finally all other molecules (generating the molecule names and incrementing the molecule index).
            if hasattr(model, 'molecules'):
                for key in list(model.molecules.keys()):
                    # Only read the required molecule.
                    if read_mol and mol_index+1 not in read_mol:
                        mol_index = mol_index + 1
                        continue

                    # Add an empty list-type container.
                    mol_conts[-1].append(MolContainer())
                    mol_conts[-1][-1].mol_type = 'other'

                    # Loop over the molecules.
                    mol_conts[-1][-1].data = []
                    for mol in model.molecules[key]:
                        mol_conts[-1][-1].data.append(mol)

                    # Check.
                    if set_mol_name and mol_index >= len(set_mol_name):
                        raise RelaxError("The %s molecules read exceeds the number of molecule names supplied in %s." % (mol_index+1, set_mol_name))

                    # Update structures.
                    self.target_mol_name(set=set_mol_name, target=new_mol_name, index=mol_index, mol_num=mol_index+1+mol_offset, file=file)
                    mol_index = mol_index + 1

            # Increment the model counters.
            model_num = model_num + 1
            model_load_num = model_load_num + 1

        # Create the structural data data structures.
        self.pack_structs(mol_conts, orig_model_num=orig_model_num, set_model_num=set_model_num, orig_mol_num=range(1, len(mol_conts[0])+1), set_mol_name=new_mol_name, file_name=file, file_path=path)

        # Loading worked.
        return True


class MolContainer:
    """The empty list-type container for the non-protein and non-RNA molecular information."""


    def from_xml(self, mol_node):
        """Recreate the MolContainer from the XML molecule node.

        @param mol_node:    The molecule XML node.
        @type mol_node:     xml.dom.minicompat.NodeList instance
        """

        # Recreate the current molecule container.
        xml_to_object(mol_node, self)

        # Re-load the data.
        self.reload_pdb()


    def reload_pdb(self):
        """Reload the PDB from the original file."""

        # The file path.
        if self.file_path:
            file_path = self.file_path + sep + self.file_name
        else:
            file_path = self.file_name

        # Test if the file exists.
        if not access(file_path, F_OK):
            found = False

            # Try finding the file in the path.
            for dir in sys.path:
                if access(dir + sep + file_path, F_OK):
                    # Prepend the file path, and break out.
                    file_path = dir + sep + file_path
                    found = True
                    break

            # Throw a warning, then exit the function.
            if not found:
                warn(RelaxNoPDBFileWarning(file_path))
                return

        # Load the PDB file.
        model = PDB.Structure(file_path, self.file_model)

        # Print out.
        print(("\n" + repr(model)))

        # Counter for finding the molecule.
        mol_num = 1

        # First add the peptide chains.
        if hasattr(model, 'peptide_chains'):
            for mol in model.peptide_chains:
                # Pack if the molecule index matches.
                if mol_num == self.file_mol_num:
                    self.data = mol
                    return

                mol_num = mol_num + 1

        # Then the nucleotide chains.
        if hasattr(model, 'nucleotide_chains'):
            for mol in model.nucleotide_chains:
                # Pack if the molecule index matches.
                if mol_num == self.file_mol_num:
                    self.data = mol
                    return

                mol_num = mol_num + 1

        # Finally all other molecules.
        if hasattr(model, 'molecules'):
            for key in list(model.molecules.keys()):
                # Pack if the molecule index matches.
                if mol_num == self.file_mol_num:
                    # Loop over the molecules.
                    self.data = []
                    for mol in model.molecules[key]:
                        self.data.append(mol)
                    return

                mol_num = mol_num + 1


    def to_xml(self, doc, element):
        """Create XML elements for the contents of this molecule container.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the molecule XML elements to.
        @type element:  XML element object
        """

        # Create an XML element for this molecule and add it to the higher level element.
        mol_element = doc.createElement('mol_cont')
        element.appendChild(mol_element)

        # Set the molecule attributes.
        mol_element.setAttribute('desc', 'Molecule container')
        mol_element.setAttribute('name', str(self.mol_name))

        # Add all simple python objects within the MolContainer to the XML element.
        fill_object_contents(doc, mol_element, object=self, blacklist=['data'] + list(self.__class__.__dict__.keys()))
