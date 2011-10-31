###############################################################################
#                                                                             #
# Copyright (C) 2003-2011 Edward d'Auvergne                                   #
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
"""Module containing the internal relax structural object."""

# Python module imports.
from numpy import array, dot, float64, linalg, zeros
import os
from os import F_OK, access
from re import search
from string import digits, split, strip, upper
from warnings import warn

# relax module imports.
from api_base import Base_struct_API, ModelList, Displacements
from data.relax_xml import fill_object_contents, xml_to_object
from generic_fns import pipes, relax_re
from generic_fns.mol_res_spin import spin_loop
from generic_fns.mol_res_spin import Selection
from relax_errors import RelaxError, RelaxNoPdbError
from relax_io import file_root, open_read_file
from relax_warnings import RelaxWarning



class Internal(Base_struct_API):
    """The internal relax structural data object.

    The structural data object for this class is a container possessing a number of different arrays
    corresponding to different structural information.  These objects are described in the
    structural container docstring.
    """

    # Identification string.
    id = 'internal'


    def add_molecule(self, name=None, model=None):
        """Add a new molecule to the store.

        @keyword name:          The molecule identifier string.
        @type name:             str
        @keyword model:         The number of the model to add the molecule to.
        @type model:            int or None
        """

        # Create the structural data data structures.
        self.pack_structs([[MolContainer()]], orig_model_num=[model], orig_mol_num=[None], set_mol_name=[name])


    def __bonded_atom(self, attached_atom, index, mol):
        """Find the atom named attached_atom directly bonded to the atom located at the index.

        @param attached_atom:   The name of the attached atom to return.
        @type attached_atom:    str
        @param index:           The index of the atom which the attached atom is attached to.
        @type index:            int
        @param mol:             The molecule container.
        @type mol:              MolContainer instance
        @return:                A tuple of information about the bonded atom.
        @rtype:                 tuple consisting of the atom number (int), atom name (str), element
                                name (str), and atomic position (Numeric array of len 3)
        """

        # Init.
        bonded_found = False

        # No bonded atoms, so determine the connectivities.
        if not mol.bonded[index]:
            # Determine the molecule type if needed.
            if not hasattr(mol, 'type'):
                self._mol_type(mol)

            # Protein.
            if mol.type == 'protein':
                self._protein_connect(mol)

            # Find everything within 2 Angstroms and say they are bonded.
            else:
                self.__find_bonded_atoms(index, mol, radius=2)

        # Loop over the bonded atoms.
        matching_list = []
        for bonded_index in mol.bonded[index]:
            if relax_re.search(mol.atom_name[bonded_index], attached_atom):
                matching_list.append(bonded_index)
        num_attached = len(matching_list)

        # Problem.
        if num_attached > 1:
            # Get the atom names.
            matching_names = []
            for i in matching_list:
                matching_names.append(mol.atom_name[i])

            # Return nothing but a warning.
            return None, None, None, None, None, 'More than one attached atom found: ' + repr(matching_names)

        # No attached atoms.
        if num_attached == 0:
            if relax_re.search('@*', attached_atom):
                matching_list = []
                bonded_num=[]
                bonded_name=[]
                element=[]
                pos=[]
                for spin, mol_name, res_num, res_name in spin_loop(selection=attached_atom, full_info=True):
                    bonded_num.append(spin.num)
                    bonded_name.append(spin.name)
                    element.append(spin.element)
                    pos.append(spin.pos)
                if len(bonded_num) == 1:
                    return bonded_num[0], bonded_name[0], element[0], pos[0], attached_atom, None
                elif len(bonded_num) > 1:
                    # Return nothing but a warning.
                    return None, None, None, None, None, 'More than one attached atom found: ' + repr(matching_names)
                elif len(bonded_num) > 1:
                    # Return nothing but a warning.
                    return None, None, None, None, None, "No attached atom could be found"
            else:
                return None, None, None, None, None, "No attached atom could be found"

        # The bonded atom info.
        index = matching_list[0]
        bonded_num = mol.atom_num[index]
        bonded_name = mol.atom_name[index]
        element = mol.element[index]
        pos = [mol.x[index], mol.y[index], mol.z[index]]
        attached_name = mol.atom_name[index]

        # Return the information.
        return bonded_num, bonded_name, element, pos, attached_name, None


    def __find_bonded_atoms(self, index, mol, radius=1.2):
        """Find all atoms within a sphere and say that they are attached to the central atom.

        The found atoms will be added to the 'bonded' data structure.


        @param index:           The index of the central atom.
        @type index:            int
        @param mol:             The molecule container.
        @type mol:              MolContainer instance
        """

        # Central atom info.
        centre = array([mol.x[index], mol.y[index], mol.z[index]], float64)

        # Atom loop.
        dist_list = []
        connect_list = {}
        element_list = {}
        for i in xrange(len(mol.atom_num)):
            # Skip proton to proton bonds!
            if mol.element[index] == 'H' and mol.element[i] == 'H':
                continue

            # The atom's position.
            pos = array([mol.x[i], mol.y[i], mol.z[i]], float64)

            # The distance from the centre.
            dist = linalg.norm(centre-pos)

            # The atom is within the radius.
            if dist < radius:
                # Store the distance.
                dist_list.append(dist)

                # Store the atom index.
                connect_list[dist] = i

                # Store the element type.
                element_list[dist] = mol.element[i]

        # The maximum number of allowed covalent bonds.
        max_conn = 1000   # Ridiculous default!
        if mol.element[index] == 'H':
            max_conn = 1
        elif mol.element[index] == 'O':
            max_conn = 2
        elif mol.element[index] == 'N':
            max_conn = 3
        elif mol.element[index] == 'C':
            max_conn = 4

        # Sort.
        dist_list.sort()

        # Loop over the max number of connections (or the number of connected atoms, if less).
        for i in range(min(max_conn, len(dist_list))):
            mol.atom_connect(index, connect_list[dist_list[i]])


    def __get_chemical_name(self, hetID):
        """Return the chemical name corresponding to the given residue ID.

        The following names are currently returned::
         ________________________________________________
         |        |                                     |
         | hetID  | Chemical name                       |
         |________|_____________________________________|
         |        |                                     |
         | TNS    | Tensor                              |
         | COM    | Centre of mass                      |
         | AXS    | Tensor axes                         |
         | SIM    | Monte Carlo simulation tensor axes  |
         | PIV    | Pivot point                         |
         | CON    | Cone object                         |
         | AVE    | Average vector                      |
         |________|_____________________________________|

        For any other residues, no description is returned.

        @param hetID:   The residue ID.
        @type hetID:    str
        @return:        The chemical name.
        @rtype:         str or None
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

        # Pivot point.
        if hetID == 'PIV':
            return 'Pivot point'

        # Cone object.
        if hetID == 'CON':
            return 'Cone'

        # Average vector.
        if hetID == 'AVE':
            return 'Average vector'


    def __parse_models_pdb(self, file_path):
        """Generator function for looping over the models in the PDB file.

        @param file_path:   The full path of the PDB file.
        @type file_path:    str
        @return:            The model number and all the records for that model.
        @rtype:             tuple of int and array of str
        """

        # Open the file.
        file = open_read_file(file_path)
        lines = file.readlines()
        file.close()

        # Check for empty files.
        if lines == []:
            raise RelaxError("The PDB file is empty.")

        # Init.
        model = None
        records = []

        # Loop over the data.
        for i in xrange(len(lines)):
            # A new model record.
            if search('^MODEL', lines[i]):
                try:
                    model = int(split(lines[i])[1])
                except:
                    raise RelaxError("The MODEL record " + repr(lines[i]) + " is corrupt, cannot read the PDB file.")

            # Skip all records prior to the first ATOM or HETATM record.
            if not (search('^ATOM', lines[i]) or search('^HETATM', lines[i])) and not len(records):
                continue

            # End of the model.
            if search('^ENDMDL', lines[i]):
                # Yield the info.
                yield model, records

                # Reset the records.
                records = []

                # Skip the rest of this loop.
                continue

            # Append the line as a record of the model.
            records.append(lines[i])

        # If records is not empty then there are no models, so yield the lot.
        if len(records):
            yield model, records


    def __parse_models_xyz(self, file_path):
        """Generator function for looping over the models in the XYZ file.

        @param file_path:   The full path of the XYZ file.
        @type file_path:    str
        @return:            The model number and all the records for that model.
        @rtype:             tuple of int and array of str
        """

        # Open the file.
        file = open_read_file(file_path)
        lines = file.readlines()
        file.close()

        # Check for empty files.
        if lines == []:
            raise RelaxError("The XYZ file is empty.")

        # Init.
        total_atom = 0
        model = 0
        records = []

        # Loop over the data.
        for i in xrange(len(lines)):
            num=0
            word=split(lines[i])
            # Find the total atom number and the first model.
            if (i==0) and (len(word)==1):
                try:
                    total_atom = int(word[0])
                    num = 1
                except:
                    raise RelaxError("The MODEL record " + repr(lines[i]) + " is corrupt, cannot read the XYZ file.")

            # End of the model.
            if (len(records) == total_atom):
              # Yield the info
              yield records

              # Reset the records.
              records = []

            # Skip all records prior to atom coordinates record.
            if (len(word) != 4):
                continue

            # Append the line as a record of the model.
            records.append(lines[i])

        # If records is not empty then there are no models, so yield the lot.
        if len(records):
            yield records


    def __parse_mols(self, records):
        """Generator function for looping over the molecules in the PDB records of a model.

        @param records:     The list of PDB records for the model, or if no models exist the entire
                            PDB file.
        @type records:      list of str
        @return:            The molecule number and all the records for that molecule.
        @rtype:             tuple of int and list of str
        """

        # Check for empty records.
        if records == []:
            raise RelaxError("There are no PDB records for this model.")

        # Init.
        mol_num = 1
        mol_records = []
        end = False

        # Loop over the data.
        for i in range(len(records)):
            # A PDB termination record.
            if search('^END', records[i]):
                break

            # A model termination record.
            if search('^ENDMDL', records[i]):
                end = True

            # A molecule termination record with no trailing HETATM.
            elif i < len(records)-1 and search('^TER', records[i]) and not search('^HETATM', records[i+1]):
                end = True

            # A HETATM followed by an ATOM record.
            elif i < len(records)-1 and search('^HETATM', records[i]) and search('^ATOM', records[i+1]):
                end = True

            # End.
            if end:
                # Yield the info.
                yield mol_num, mol_records

                # Reset the records.
                mol_records = []

                # Increment the molecule number.
                mol_num = mol_num + 1

                # Reset the flag.
                end = False

                # Skip the rest of this loop.
                continue

            # Append the line as a record of the molecule.
            mol_records.append(records[i])

        # If records is not empty then there is only a single molecule, so yield the lot.
        if len(mol_records):
            yield mol_num, mol_records


    def __validate_data_arrays(self, struct):
        """Check the validity of the data arrays in the given structure object.

        @param struct:  The structural object.
        @type struct:   Structure_container instance
        """

        # The number of atoms.
        num = len(struct.atom_name)

        # Check the other lengths.
        if len(struct.bonded) != num and len(struct.chain_id) != num and len(struct.element) != num and len(struct.pdb_record) != num and len(struct.res_name) != num and len(struct.res_num) != num and len(struct.seg_id) != num and len(struct.x) != num and len(struct.y) != num and len(struct.z) != num:
            raise RelaxError("The structural data is invalid.")


    def _mol_type(self, mol):
        """Determine the type of molecule.

        @param mol:     The molecule data container.
        @type mol:      MolContainer instance
        """

        # Amino acids.
        aa = ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLU', 'GLN', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL']

        # Set the molecule type to default to 'other'.
        mol.type = 'other'

        # Loop over the residues.
        for res in mol.res_name:
            # Protein.
            if res in aa:
                # Set the molecule type and return.
                mol.type = 'protein'
                return


    def _protein_connect(self, mol):
        """Set up the connectivities for the protein.

        @param mol:     The molecule data container.
        @type mol:      MolContainer instance
        """

        # Initialise some residue data.
        curr_res_num = None
        res_atoms = []

        # Loop over all atoms.
        for i in range(len(mol.atom_num)):
            # New residue.
            if mol.res_num[i] != curr_res_num:
                # Intra-residue connectivites.
                if len(res_atoms):
                    self._protein_intra_connect(mol, res_atoms)

                # Update the residue number.
                curr_res_num = mol.res_num[i]

                # Reset the residue atom index list.
                res_atoms = []

            # Add the atom index to the list.
            res_atoms.append(i)

            # Last atom.
            if i == len(mol.atom_num) - 1 and len(res_atoms):
                self._protein_intra_connect(mol, res_atoms)


    def _protein_intra_connect(self, mol, res_atoms):
        """Set up the connectivities for the protein.

        @param mol:         The molecule data container.
        @type mol:          MolContainer instance
        @param res_atoms:   The list of atom indices corresponding to the residue.
        @type res_atoms:    list of int
        """

        # Back bond connectivity.
        indices = {
            'N': None,
            'C': None,
            'O': None,
            'CA': None,
            'HN': None,
            'H': None,  # Same as HN.
            'HA': None
        }

        # Loop over all atoms to find the indices.
        for index in res_atoms:
            if indices.has_key(mol.atom_name[index]):
                indices[mol.atom_name[index]] = index

        # Connect the atom pairs.
        pairs = [
            ['N', 'HN'],
            ['N', 'H'],
            ['N', 'CA'],
            ['CA', 'HA'],
            ['CA', 'C'],
            ['C', 'O']
        ]

        # Loop over the atoms pairs and connect them.
        for pair in pairs:
            if indices[pair[0]] != None and indices[pair[1]] != None:
                mol.atom_connect(indices[pair[0]], indices[pair[1]])


    def _translate(self, data, format='str'):
        """Convert the data into a format for writing to file.

        @param data:        The data to convert to the required format.
        @type data:         anything
        @keyword format:    The format to convert to.  This can be 'str', 'float', or 'int'.
        @type format:       str
        @return:            The converted version of the data.
        @rtype:             str
        """

        # Conversion to string.
        if format == 'str':
            # None values.
            if data == None:
                data = ''

            # Force convert to string.
            if not isinstance(data, str):
                data = repr(data)

        # Conversion to float.
        if format == 'float':
            # None values.
            if data == None:
                data = 0.0

            # Force convert to float.
            if not isinstance(data, float):
                data = float(data)

         # Return the converted data.
        return data


    def add_atom(self, mol_name=None, atom_name=None, res_name=None, res_num=None, pos=[None, None, None], element=None, atom_num=None, chain_id=None, segment_id=None, pdb_record=None):
        """Add a new atom to the structural data object.

        @keyword mol_name:      The name of the molecule.
        @type mol_name:         str
        @keyword atom_name:     The atom name, e.g. 'H1'.
        @type atom_name:        str or None
        @keyword res_name:      The residue name.
        @type res_name:         str or None
        @keyword res_num:       The residue number.
        @type res_num:          int or None
        @keyword pos:           The position vector of coordinates.
        @type pos:              list (length = 3)
        @keyword element:       The element symbol.
        @type element:          str or None
        @keyword atom_num:      The atom number.
        @type atom_num:         int or None
        @keyword chain_id:      The chain identifier.
        @type chain_id:         str or None
        @keyword segment_id:    The segment identifier.
        @type segment_id:       str or None
        @keyword pdb_record:    The optional PDB record name, e.g. 'ATOM' or 'HETATM'.
        @type pdb_record:       str or None
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Add the molecule, if it does not exist.
        if cdp.structure.get_molecule(mol_name) == None:
            cdp.structure.add_molecule(name=mol_name)

        # Loop over each model.
        for model in self.structural_data:
            # Specific molecule.
            mol = cdp.structure.get_molecule(mol_name)

            # Add the atom.
            mol.atom_add(atom_name=atom_name, res_name=res_name, res_num=res_num, pos=pos, element=element, atom_num=atom_num, chain_id=chain_id, segment_id=segment_id, pdb_record=pdb_record)


    def atom_loop(self, atom_id=None, str_id=None, model_num=None, model_num_flag=False, mol_name_flag=False, res_num_flag=False, res_name_flag=False, atom_num_flag=False, atom_name_flag=False, element_flag=False, pos_flag=False, ave=False):
        """Generator function for looping over all atoms in the internal relax structural object.

        @keyword atom_id:           The molecule, residue, and atom identifier string.  Only atoms matching this selection will be yielded.
        @type atom_id:              str
        @keyword str_id:            The structure identifier.  This can be the file name, model number, or structure number.  If None, then all structures will be looped over.
        @type str_id:               str, int, or None
        @keyword model_num:         Only loop over a specific model.
        @type model_num:            int or None
        @keyword model_num_flag:    A flag which if True will cause the model number to be yielded.
        @type model_num_flag:       bool
        @keyword mol_name_flag:     A flag which if True will cause the molecule name to be yielded.
        @type mol_name_flag:        bool
        @keyword res_num_flag:      A flag which if True will cause the residue number to be yielded.
        @type res_num_flag:         bool
        @keyword res_name_flag:     A flag which if True will cause the residue name to be yielded.
        @type res_name_flag:        bool
        @keyword atom_num_flag:     A flag which if True will cause the atom number to be yielded.
        @type atom_num_flag:        bool
        @keyword atom_name_flag:    A flag which if True will cause the atom name to be yielded.
        @type atom_name_flag:       bool
        @keyword element_flag:      A flag which if True will cause the element name to be yielded.
        @type element_flag:         bool
        @keyword pos_flag:          A flag which if True will cause the atomic position to be yielded.
        @type pos_flag:             bool
        @keyword ave:               A flag which if True will result in this method returning the average atom properties across all loaded structures.
        @type ave:                  bool
        @return:                    A tuple of atomic information, as described in the docstring.
        @rtype:                     tuple consisting of optional molecule name (str), residue number (int), residue name (str), atom number (int), atom name(str), element name (str), and atomic position (array of len 3).
        """

        # Check that the structure is loaded.
        if not len(self.structural_data):
            raise RelaxNoPdbError

        # Generate the selection object.
        sel_obj = Selection(atom_id)

        # Model loop.
        for model in self.model_loop(model_num):
            # Loop over the molecules.
            for mol_index in range(len(model.mol)):
                mol = model.mol[mol_index]

                # Skip non-matching molecules.
                if sel_obj and not sel_obj.contains_mol(mol.mol_name):
                    continue

                # Loop over all atoms.
                for i in xrange(len(mol.atom_name)):
                    # Skip non-matching atoms.
                    if sel_obj and not sel_obj.contains_spin(mol.atom_num[i], mol.atom_name[i], mol.res_num[i], mol.res_name[i], mol.mol_name):
                        continue

                    # Initialise.
                    res_num = mol.res_num[i]
                    res_name = mol.res_name[i]
                    atom_num = mol.atom_num[i]
                    atom_name = mol.atom_name[i]
                    element = mol.element[i]
                    pos = zeros(3, float64)

                    # The atom position.
                    if ave:
                        # Loop over the models.
                        for model in self.model_loop():
                            # Alias.
                            mol = model.mol[mol_index]

                            # Some sanity checks.
                            if mol.atom_num[i] != atom_num:
                                raise RelaxError("The loaded structures do not contain the same atoms.  The average structural properties can not be calculated.")

                            # Sum the atom positions.
                            pos = pos + array([mol.x[i], mol.y[i], mol.z[i]], float64)

                        # Average the position array (divide by the number of models).
                        pos = pos / len(self.structural_data)
                    else:
                        pos = array([mol.x[i], mol.y[i], mol.z[i]], float64)

                    # The molecule name.
                    mol_name = mol.mol_name

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


    def bond_vectors(self, attached_atom=None, model_num=None, mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None, return_name=False, return_warnings=False):
        """Find the bond vector between the atoms of 'attached_atom' and 'atom_id'.

        @keyword attached_atom:     The name of the bonded atom.
        @type attached_atom:        str
        @keyword model_num:         The model of which to return the vectors from.  If not supplied and multiple models exist, then vectors from all models will be returned.
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
        @keyword return_name:       A flag which if True will cause the name of the attached atom to be returned together with the bond vectors.
        @type return_name:          bool
        @keyword return_warnings:   A flag which if True will cause warning messages to be returned.
        @type return_warnings:      bool
        @return:                    The list of bond vectors for each model.
        @rtype:                     list of numpy arrays (or a tuple if return_name or return_warnings are set)
        """

        # Initialise some objects.
        vectors = []
        attached_name = None
        warnings = None

        # Loop over the models.
        for model in self.model_loop(model_num):
            # Loop over the molecules.
            for mol in model.mol:
                # Skip non-matching molecules.
                if mol_name and mol_name != mol.mol_name:
                    continue

                # Find the atomic index of the base atom.
                index = None
                for i in range(len(mol.atom_name)):
                    # Residues don't match.
                    if (res_num != None and mol.res_num[i] != res_num) or (res_name != None and mol.res_name[i] != res_name):
                        continue

                    # Atoms don't match.
                    if (spin_num != None and mol.atom_num[i] != spin_num) or (spin_name != None and mol.atom_name[i] != spin_name):
                        continue

                    # Update the index and stop searching.
                    index = i
                    break

                # Found the atom.
                if index != None:
                    # Get the atom bonded to this model/molecule/residue/atom.
                    bonded_num, bonded_name, element, pos, attached_name, warnings = self.__bonded_atom(attached_atom, index, mol)

                    # No bonded atom.
                    if (bonded_num, bonded_name, element) == (None, None, None):
                        continue

                    # The bond vector.
                    vector = array(pos, float64) - array([mol.x[index], mol.y[index], mol.z[index]], float64)

                    # Append the vector to the vectors array.
                    vectors.append(vector)

                # Not found.
                else:
                    warnings = "Cannot find the atom in the structure"

        # Build the tuple to be yielded.
        data = (vectors,)
        if return_name:
            data = data + (attached_name,)
        if return_warnings:
            data = data + (warnings,)

        # Return the data.
        return data


    def connect_atom(self, mol_name=None, index1=None, index2=None):
        """Connect two atoms in the structural data object.

        @keyword mol_name:  The name of the molecule.
        @type mol_name:     str
        @keyword index1:    The global index of the first atom.
        @type index1:       str
        @keyword index2:    The global index of the first atom.
        @type index2:       str
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Add the molecule, if it does not exist.
        if cdp.structure.get_molecule(mol_name) == None:
            cdp.structure.add_molecule(name=mol_name)

        # Loop over each model.
        for model in self.structural_data:
            # Specific molecule.
            mol = cdp.structure.get_molecule(mol_name)

            # Add the atom.
            mol.atom_connect(index1=index1, index2=index2)


    def delete(self):
        """Delete all the structural information."""

        # Print out.
        print("Deleting the following structural data:\n")
        print(self.structural_data)

        # Delete the structural data.
        del self.structural_data

        # Initialise the empty model list.
        self.structural_data = ModelList()


    def get_molecule(self, molecule, model=None):
        """Return the molecule.

        Only one model can be specified.


        @param molecule:    The molecule name.
        @type molecule:     int or None
        @keyword model:     The model number.
        @type model:        int or None
        @raises RelaxError: If the model is not specified and there is more than one model loaded.
        @return:            The MolContainer corresponding to the molecule name and model number.
        @rtype:             MolContainer instance or None
        """

        # Check if the target is a single molecule.
        if model == None and self.num_models() > 1:
            raise RelaxError("The target molecule cannot be determined as there are %s models already present." % self.num_modes())

        # No models.
        if not len(self.structural_data):
            return

        # Loop over the models.
        for model_cont in self.model_loop(model):
            # Loop over the molecules.
            for mol in model_cont.mol:
                # Return the matching molecule.
                if mol.mol_name == molecule:
                    return mol


    def load_pdb(self, file_path, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, verbosity=False):
        """Method for loading structures from a PDB file.

        @param file_path:       The full path of the PDB file.
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
            print("\nInternal relax PDB parser.")

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

        # Loop over all models in the PDB file.
        model_index = 0
        orig_model_num = []
        mol_conts = []
        for model_num, model_records in self.__parse_models_pdb(file_path):
            # Only load the desired model.
            if read_model and model_num not in read_model:
                continue

            # Store the original model number.
            orig_model_num.append(model_num)

            # Loop over the molecules of the model.
            mol_conts.append([])
            mol_index = 0
            orig_mol_num = []
            new_mol_name = []
            for mol_num, mol_records in self.__parse_mols(model_records):
                # Only load the desired model.
                if read_mol and mol_num not in read_mol:
                    continue

                # Set the target molecule name.
                if set_mol_name:
                    new_mol_name.append(set_mol_name[mol_index])
                else:
                    # Number of structures already present for the model.
                    num_struct = 0
                    for model in self.structural_data:
                        if not set_model_num or (model_index <= len(set_model_num) and set_model_num[model_index] == model.num):
                            num_struct = len(model.mol)

                    # Set the name to the file name plus the structure number.
                    new_mol_name.append(file_root(file) + '_mol' + repr(mol_num+num_struct))

                # Store the original mol number.
                orig_mol_num.append(mol_num)

                # Generate the molecule container.
                mol = MolContainer()

                # Fill the molecular data object.
                mol.fill_object_from_pdb(mol_records)

                # Store the molecule container.
                mol_conts[model_index].append(mol)

                # Increment the molecule index.
                mol_index = mol_index + 1

            # Increment the model index.
            model_index = model_index + 1

        # No data, so throw a warning and exit.
        if not len(mol_conts):
            warn(RelaxWarning("No structural data could be read from the file '%s'." % file_path))
            return False

        # Create the structural data data structures.
        self.pack_structs(mol_conts, orig_model_num=orig_model_num, set_model_num=set_model_num, orig_mol_num=orig_mol_num, set_mol_name=new_mol_name, file_name=file, file_path=path)

        # Loading worked.
        return True


    def load_xyz(self, file_path, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, verbosity=False):
        """Method for loading structures from a XYZ file.

        @param file_path:       The full path of the XYZ file.
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
        @keyword read_model:    The XYZ model to extract from the file.  If set to None, then all
                                models will be loaded.
        @type read_model:       None, int, or list of int
        @keyword set_model_num: Set the model number of the loaded molecule.  If set to None, then
                                the XYZ model numbers will be preserved, if they exist.
        @type set_model_num:    None, int, or list of int
        @keyword verbosity:     A flag which if True will cause messages to be printed.
        @type verbosity:        bool
        @return:                The status of the loading of the XYZ file.
        @rtype:                 bool
        """

        # Initial print out.
        if verbosity:
            print("\nInternal relax XYZ parser.")

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

        # Loop over all models in the XYZ file.
        mol_index=0
        model_index = 0
        xyz_model_increment = 0
        orig_model_num = []
        mol_conts = []
        orig_mol_num = []
        new_mol_name = []
        for model_records in self.__parse_models_xyz(file_path):
            # Increment the xyz_model_increment
            xyz_model_increment = xyz_model_increment +1

            # Only load the desired model.
            if read_model and xyz_model_increment not in read_model:
                continue

            # Store the original model number.
            orig_model_num.append(model_index)

            # Loop over the molecules of the model.
            if read_mol and mol_index not in read_mol:
                continue

            # Set the target molecule name.
            if set_mol_name:
                new_mol_name.append(set_mol_name[mol_index])
            else:
                if mol_index==0:
                   #Set the name to the file name plus the structure number.
                   new_mol_name.append(file_root(file) + '_mol' + repr(mol_index+1))

            # Store the original mol number.
            orig_mol_num.append(mol_index)

            # Generate the molecule container.
            mol = MolContainer()

            # Fill the molecular data object.
            mol.fill_object_from_xyz(model_records)

            # Store the molecule container.
            mol_conts.append([])
            mol_conts[model_index].append(mol)

            # Increment the molecule index.
            mol_index = mol_index + 1

            # Increment the model index.
            model_index = model_index + 1

        orig_mol_num=[0]
        # Create the structural data data structures.
        self.pack_structs(mol_conts, orig_model_num=orig_model_num, set_model_num=set_model_num, orig_mol_num=orig_mol_num, set_mol_name=new_mol_name, file_name=file, file_path=path)

        # Loading worked.
        return True


    def rotate(self, R=None, origin=None, model=None):
        """Rotate the structural information about the given origin.

        @keyword R:         The forwards rotation matrix.
        @type R:            numpy 3D, rank-2 array
        @keyword origin:    The origin of the rotation.
        @type origin:       numpy 3D, rank-1 array
        @keyword model:     The model to rotate.  If None, all models will be rotated.
        @type model:        int
        """

        # Loop over the models.
        for model_cont in self.model_loop(model):
            # Loop over the molecules.
            for mol in model_cont.mol:
                # Loop over the atoms.
                for i in range(len(mol.atom_num)):
                    # The origin to atom vector.
                    vect = array([mol.x[i], mol.y[i], mol.z[i]], float64) - origin

                    # Rotation.
                    rot_vect = dot(R, vect)

                    # The new position.
                    pos = rot_vect + origin
                    mol.x[i] = pos[0]
                    mol.y[i] = pos[1]
                    mol.z[i] = pos[2]


    def translate(self, T=None, model=None):
        """Displace the structural information by the given translation vector.

        @keyword T:         The translation vector.
        @type T:            numpy 3D, rank-1 array
        @keyword model:     The model to rotate.  If None, all models will be rotated.
        @type model:        int
        """

        # Loop over the models.
        for model_cont in self.model_loop(model):
            # Loop over the molecules.
            for mol in model_cont.mol:
                # Loop over the atoms.
                for i in range(len(mol.atom_num)):
                    # Translate.
                    mol.x[i] = mol.x[i] + T[0]
                    mol.y[i] = mol.y[i] + T[1]
                    mol.z[i] = mol.z[i] + T[2]


    def write_pdb(self, file, model_num=None):
        """Method for the creation of a PDB file from the structural data.

        A number of PDB records including HET, HETNAM, FORMUL, HETATM, TER, CONECT, MASTER, and END
        are created.  To create the non-standard residue records HET, HETNAM, and FORMUL, the data
        structure 'het_data' is created.  It is an array of arrays where the first dimension
        corresponds to a different residue and the second dimension has the elements:

            0.  Residue number.
            1.  Residue name.
            2.  Chain ID.
            3.  Total number of atoms in the residue.
            4.  Number of H atoms in the residue.
            5.  Number of C atoms in the residue.


        @param file:            The PDB file object.  This object must be writable.
        @type file:             file object
        @keyword model_num:     The model to place into the PDB file.  If not supplied, then all
                                models will be placed into the file.
        @type model_num:        None or int
        """

        # Validate the structural data.
        self.validate()

        # Initialise record counts.
        num_hetatm = 0
        num_atom = 0
        num_ter = 0
        num_conect = 0

        # Print out.
        print("\nCreating the PDB records\n")

        # Write some initial remarks.
        print("REMARK")
        file.write("REMARK   4 THIS FILE COMPLIES WITH FORMAT V. 3.1, 1-AUG-2007\n")
        file.write("REMARK  40 CREATED BY RELAX (HTTP://NMR-RELAX.COM)\n")
        num_remark = 2

        # Determine if model records will be created.
        model_records = False
        for model in self.model_loop():
            if hasattr(model, 'num') and model.num != None:
                model_records = True


        ####################
        # Hetrogen section #
        ####################

        # Initialise the hetrogen info array.
        het_data = []
        het_data_coll = []

        # Loop over the molecules of the first model.
        index = 0
        for mol in self.structural_data[0].mol:
            # Check the validity of the data.
            self.__validate_data_arrays(mol)

            # Append an empty array for this molecule.
            het_data.append([])

            # Collect the non-standard residue info.
            for i in xrange(len(mol.atom_name)):
                # Skip non-HETATM records and HETATM records with no residue info.
                if mol.pdb_record[i] != 'HETATM' or mol.res_name[i] == None:
                    continue

                # If the residue is not already stored initialise a new het_data element.
                # (residue number, residue name, chain ID, number of atoms, atom count array).
                if not het_data[index] or not mol.res_num[i] == het_data[index][-1][0]:
                    het_data[index].append([mol.res_num[i], mol.res_name[i], mol.chain_id[i], 0, []])

                    # Catch missing chain_ids.
                    if het_data[index][-1][2] == None:
                        het_data[index][-1][2] = ''

                # Total atom count.
                het_data[index][-1][3] = het_data[index][-1][3] + 1

                # Find if the atom has already a count entry.
                entry = False
                for j in xrange(len(het_data[index][-1][4])):
                    if mol.element[i] == het_data[index][-1][4][j][0]:
                        entry = True

                # Create a new specific atom count entry.
                if not entry:
                    het_data[index][-1][4].append([mol.element[i], 0])

                # Increment the specific atom count.
                for j in xrange(len(het_data[index][-1][4])):
                    if mol.element[i] == het_data[index][-1][4][j][0]:
                        het_data[index][-1][4][j][1] = het_data[index][-1][4][j][1] + 1

            # Create the collective hetrogen info data structure.
            for i in xrange(len(het_data[index])):
                # Find the entry in the collective structure.
                found = False
                for j in xrange(len(het_data_coll)):
                    # Matching residue numbers.
                    if het_data[index][i][0] == het_data_coll[j][0]:
                        # Change the flag.
                        found = True

                        # The checks.
                        if het_data_coll[j][1] != het_data[index][i][1]:
                            raise RelaxError("The " + repr(het_data[index][i][1]) + " residue name of hetrogen " + repr(het_data[index][i][0]) + " " + het_data[index][i][1] + " of structure " + repr(index) + " does not match the " + repr(het_data_coll[j][1]) + " name of the previous structures.")

                        elif het_data_coll[j][2] != het_data[index][i][2]:
                            raise RelaxError("The hetrogen chain id " + repr(het_data[index][i][2]) + " does not match " + repr(het_data_coll[j][2]) + " of residue " + repr(het_data_coll[j][0]) + " " + het_data_coll[j][1] + " of the previous structures.")

                        elif het_data_coll[j][3] != het_data[index][i][3]:
                            raise RelaxError("The " + repr(het_data[index][i][3]) + " atoms of hetrogen " + repr(het_data_coll[j][0]) + " " + het_data_coll[j][1] + " of structure " + repr(index) + " does not match the " + repr(het_data_coll[j][3]) + " of the previous structures.")

                        elif het_data_coll[j][4] != het_data[index][i][4]:
                            raise RelaxError("The atom counts " + repr(het_data[index][i][4]) +  " for the hetrogen residue " + repr(het_data_coll[j][0]) + " " + het_data_coll[j][1] + " of structure " + repr(index) + " do not match the counts " + repr(het_data_coll[j][4]) + " of the previous structures.")

                # If there is no match, add the new residue to the collective.
                if not found:
                    het_data_coll.append(het_data[index][i])

            # Increment the molecule index.
            index = index + 1


        # The HET records.
        ##################

        # Print out.
        print("HET")

        # Write the HET records.
        for het in het_data_coll:
            file.write("%-6s %3s  %1s%4s%1s  %5s     %-40s\n" % ('HET', het[2], het[1], het[0], '', het[3], ''))


        # The HETNAM records.
        #####################

        # Print out.
        print("HETNAM")

        # Loop over the non-standard residues.
        residues = []
        for het in het_data_coll:
            # Test if the residue HETNAM record as already been written (otherwise store its name).
            if het[1] in residues:
                continue
            else:
                residues.append(het[1])

            # Get the chemical name.
            chemical_name = self.__get_chemical_name(het[1])
            if not chemical_name:
                chemical_name = 'Unknown'

            # Write the HETNAM records.
            file.write("%-6s  %2s %3s %-55s\n" % ('HETNAM', '', het[1], chemical_name))


        # The FORMUL records.
        #####################

        # Print out.
        print("FORMUL")

        # Loop over the non-standard residues and generate and write the chemical formula.
        residues = []
        for het in het_data_coll:
            # Test if the residue HETNAM record as already been written (otherwise store its name).
            if het[1] in residues:
                continue
            else:
                residues.append(het[1])

            # Initialise the chemical formula.
            formula = ''

            # Loop over the atoms.
            for atom_count in het[4]:
                formula = formula + atom_count[0] + repr(atom_count[1])

            # The FORMUL record (chemical formula).
            file.write("%-6s  %2s  %3s %2s%1s%-51s\n" % ('FORMUL', het[0], het[1], '', '', formula))


        ######################
        # Coordinate section #
        ######################

        # Loop over the models.
        for model in self.model_loop(model_num):
            # MODEL record, for multiple models.
            ####################################

            if model_records:
                # Print out.
                print(("\nMODEL %s" % model.num))

                # Write the model record.
                file.write("%-6s    %4i\n" % ('MODEL', model.num))


            # Add the atomic coordinate records (ATOM, HETATM, and TER).
            ############################################################

            # Loop over the molecules.
            for mol in model.mol:
                # Print out.
                print("ATOM, HETATM, TER")

                # Loop over the atomic data.
                atom_record = False
                for i in xrange(len(mol.atom_name)):
                    # Write the ATOM record.
                    if mol.pdb_record[i] in [None, 'ATOM']:
                        atom_record = True

                        # The atom number, if missing.
                        atom_num = mol.atom_num[i]
                        if atom_num == None:
                            atom_num = i + 1

                        # Write out.
                        file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('ATOM', atom_num, self._translate(mol.atom_name[i]), '', self._translate(mol.res_name[i]), self._translate(mol.chain_id[i]), self._translate(mol.res_num[i]), '', self._translate(mol.x[i], 'float'), self._translate(mol.y[i], 'float'), self._translate(mol.z[i], 'float'), 1.0, 0, self._translate(mol.seg_id[i]), self._translate(mol.element[i]), ''))
                        num_atom = num_atom + 1

                # Finish the ATOM section with the TER record.
                if atom_record:
                    file.write("%-6s%5s      %3s %1s%4s%1s\n" % ('TER', num_atom+1, self._translate(mol.res_name[i]), self._translate(mol.chain_id[i]), self._translate(mol.res_num[i]), ''))
                    num_ter = num_ter + 1

                # Loop over the atomic data.
                for i in xrange(len(mol.atom_name)):
                    # Write the HETATM record.
                    if mol.pdb_record[i] == 'HETATM':
                        # The atom number, if missing.
                        atom_num = mol.atom_num[i]
                        if atom_num == None:
                            atom_num = i + 1

                        # Write out.
                        file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('HETATM', atom_num, self._translate(mol.atom_name[i]), '', self._translate(mol.res_name[i]), self._translate(mol.chain_id[i]), self._translate(mol.res_num[i]), '', self._translate(mol.x[i], 'float'), self._translate(mol.y[i], 'float'), self._translate(mol.z[i], 'float'), 1.0, 0, self._translate(mol.seg_id[i]), self._translate(mol.element[i]), ''))
                        num_hetatm = num_hetatm + 1


            # ENDMDL record, for multiple structures.
            ########################################

            if model_records:
                # Print out.
                print("ENDMDL")

                # Write the model record.
                file.write("%-6s\n" % 'ENDMDL')


        # Create the CONECT records.
        ############################

        # Print out.
        print("CONECT")

        # Loop over the molecules of the first model.
        for mol in self.structural_data[0].mol:
            # Loop over the atoms.
            for i in xrange(len(mol.atom_name)):
                # No bonded atoms, hence no CONECT record is required.
                if not len(mol.bonded[i]):
                    continue

                # Initialise some data structures.
                flush = 0
                bonded_index = 0
                bonded = ['', '', '', '']

                # Loop over the bonded atoms.
                for j in xrange(len(mol.bonded[i])):
                    # End of the array, hence create the CONECT record in this iteration.
                    if j == len(mol.bonded[i])-1:
                        flush = True

                    # Only four covalently bonded atoms allowed in one CONECT record.
                    if bonded_index == 3:
                        flush = True

                    # Get the bonded atom index.
                    bonded[bonded_index] = mol.bonded[i][j]

                    # Increment the bonded_index value.
                    bonded_index = bonded_index + 1

                    # Generate the CONECT record and increment the counter.
                    if flush:
                        # Convert the atom indices to atom numbers.
                        for k in range(4):
                            if bonded[k] != '':
                                if mol.atom_num[bonded[k]] != None:
                                    bonded[k] = mol.atom_num[bonded[k]]
                                else:
                                    bonded[k] = bonded[k] + 1

                        # Write the CONECT record.
                        file.write("%-6s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('CONECT', i+1, bonded[0], bonded[1], bonded[2], bonded[3], '', '', '', '', '', ''))

                        # Reset the flush flag, the bonded atom count, and the bonded atom names.
                        flush = False
                        bonded_index = 0
                        bonded = ['', '', '', '']

                        # Increment the CONECT record count.
                        num_conect = num_conect + 1



        # MASTER record.
        ################

        # Print out.
        print("\nMASTER")

        # Write the MASTER record.
        file.write("%-6s    %5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('MASTER', 0, 0, len(het_data_coll), 0, 0, 0, 0, 0, num_atom+num_hetatm, num_ter, num_conect, 0))


        # END.
        ######

        # Print out.
        print("END")

        # Write the END record.
        file.write("END\n")


class MolContainer:
    """The container for the molecular information.

    The structural data object for this class is a container possessing a number of different arrays
    corresponding to different structural information.  These objects include:

        - atom_num:  The atom name.
        - atom_name:  The atom name.
        - bonded:  Each element an array of bonded atom indices.
        - chain_id:  The chain ID.
        - element:  The element symbol.
        - pdb_record:  The optional PDB record name (one of ATOM, HETATM, or TER).
        - res_name:  The residue name.
        - res_num:  The residue number.
        - seg_id:  The segment ID.
        - x:  The x coordinate of the atom.
        - y:  The y coordinate of the atom.
        - z:  The z coordinate of the atom.

    All arrays should be of equal length so that an atom index can retrieve all the corresponding
    data.  Only the atom identification string is compulsory, all other arrays can contain None.
    """


    def __init__(self):
        """Initialise the molecular container."""

        # The atom num (array of int).
        self.atom_num = []

        # The atom name (array of str).
        self.atom_name = []

        # The bonded atom indices (array of arrays of int).
        self.bonded = []

        # The chain ID (array of str).
        self.chain_id = []

        # The element symbol (array of str).
        self.element = []

        # The optional PDB record name (array of str).
        self.pdb_record = []

        # The residue name (array of str).
        self.res_name = []

        # The residue number (array of int).
        self.res_num = []

        # The segment ID (array of int).
        self.seg_id = []

        # The x coordinate (array of float).
        self.x = []

        # The y coordinate (array of float).
        self.y = []

        # The z coordinate (array of float).
        self.z = []


    def __atom_index(self, atom_num):
        """Find the atom index corresponding to the given atom number.

        @param atom_num:        The atom number to find the index of.
        @type atom_num:         int
        @return:                The atom index corresponding to the atom.
        @rtype:                 int
        """

        # Loop over the atoms.
        for j in xrange(len(self.atom_num)):
            # Return the index.
            if self.atom_num[j] == atom_num:
                return j

        # Should not be here, the PDB connect records are incorrect.
        warn(RelaxWarning("The atom number " + repr(atom_num) + " from the CONECT record cannot be found within the ATOM and HETATM records."))


    def __det_pdb_element(self, atom_name):
        """Try to determine the element from the PDB atom name.

        @param atom_name:   The PDB atom name.
        @type atom_name:    str
        @return:            The element name, or None if unsuccessful.
        @rtype:             str or None
        """

        # Strip away the "'" character (for RNA, etc.).
        element = strip(atom_name, "'")

        # Strip away atom numbering, from the front and end.
        element = strip(element, digits)

        # Amino acid atom translation table (note, numbers have been stripped already!).
        table = {'C': ['CA', 'CB', 'CG', 'CD', 'CE', 'CH', 'CZ'],
                 'N': ['ND', 'NE', 'NH', 'NZ'],
                 'H': ['HA', 'HB', 'HG', 'HD', 'HE', 'HH', 'HT', 'HZ'],
                 'O': ['OG', 'OD', 'OE', 'OH', 'OT'],
                 'S': ['SD', 'SG']
        }

        # Translate amino acids.
        for key in list(table.keys()):
            if element in table[key]:
                element = key
                break

        # Allowed element list.
        elements = ['H', 'C', 'N', 'O', 'F', 'P', 'S']

        # Return the element, if in the list.
        if element in elements:
            return element

        # Else, throw a warning.
        warn(RelaxWarning("Cannot determine the element associated with atom '%s'." % atom_name))


    def __parse_pdb_record(self, record):
        """Parse the PDB record string and return an array of the corresponding atomic information.

        The format of the ATOM and HETATM records is::
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


        The format of the TER record is::
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


        The format of the CONECT record is::
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


        @param record:  The single line PDB record.
        @type record:   str
        @return:        The list of atomic information, each element corresponding to the PDB fields
                        as defined in "Protein Data Bank Contents Guide: Atomic Coordinate Entry
                        Format Description" version 2.1 (draft), October 25, 1996.
        @rtype:         list of str
        """

        # Initialise.
        fields = []

        # ATOM and HETATM records.
        if search('^ATOM', record) or search('^HETATM', record):
            # Split up the record.
            fields.append(record[0:6])
            fields.append(record[6:11])
            fields.append(record[12:16])
            fields.append(record[16])
            fields.append(record[17:20])
            fields.append(record[21])
            fields.append(record[22:26])
            fields.append(record[26])
            fields.append(record[30:38])
            fields.append(record[38:46])
            fields.append(record[46:54])
            fields.append(record[54:60])
            fields.append(record[60:66])
            fields.append(record[72:76])
            fields.append(record[76:78])
            fields.append(record[78:80])

            # Loop over the fields.
            for i in xrange(len(fields)):
                # Strip all whitespace.
                fields[i] = strip(fields[i])

                # Replace nothingness with None.
                if fields[i] == '':
                    fields[i] = None

            # Convert strings to numbers.
            if fields[1]:
                fields[1] = int(fields[1])
            if fields[6]:
                fields[6] = int(fields[6])
            if fields[8]:
                fields[8] = float(fields[8])
            if fields[9]:
                fields[9] = float(fields[9])
            if fields[10]:
                fields[10] = float(fields[10])
            if fields[11]:
                fields[11] = float(fields[11])
            if fields[12]:
                fields[12] = float(fields[12])

        # CONECT records.
        if search('^CONECT', record):
            # Split up the record.
            fields.append(record[0:6])
            fields.append(record[6:11])
            fields.append(record[11:16])
            fields.append(record[16:21])
            fields.append(record[21:26])
            fields.append(record[26:31])

            # Loop over the fields.
            for i in xrange(len(fields)):
                # Strip all whitespace.
                fields[i] = strip(fields[i])

                # Replace nothingness with None.
                if fields[i] == '':
                    fields[i] = None

            # Convert strings to numbers.
            if fields[1]:
                fields[1] = int(fields[1])
            if fields[2]:
                fields[2] = int(fields[2])
            if fields[3]:
                fields[3] = int(fields[3])
            if fields[4]:
                fields[4] = int(fields[4])
            if fields[5]:
                fields[5] = int(fields[5])

        # Return the atomic info.
        return fields


    def __parse_xyz_record(self, record):
        """Parse the XYZ record string and return an array of the corresponding atomic information.

        The format of the XYZ records is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1      | String       | element      |                                                |
         |  2      | Real         | x            | Orthogonal coordinates for X in Angstroms      |
         |  3      | Real         | y            | Orthogonal coordinates for Y in Angstroms      |
         |  4      | Real         | z            | Orthogonal coordinates for Z in Angstroms      |
         |_________|______________|______________|________________________________________________|


        @param record:  The single line PDB record.
        @type record:   str
        @return:        The list of atomic information
        @rtype:         list of str
        """

        # Initialise.
        fields = []
        word=split(record)

        # ATOM and HETATM records.
        if len(word)==4:
            # Split up the record.
            fields.append(word[0])
            fields.append(word[1])
            fields.append(word[2])
            fields.append(word[3])

            # Loop over the fields.
            for i in xrange(len(fields)):
                # Strip all whitespace.
                fields[i] = strip(fields[i])

                # Replace nothingness with None.
                if fields[i] == '':
                    fields[i] = None

            # Convert strings to numbers.
            if fields[1]:
                fields[1] = float(fields[1])
            if fields[2]:
                fields[2] = float(fields[2])
            if fields[3]:
                fields[3] = float(fields[3])

        # Return the atomic info.
        return fields


    def atom_add(self, atom_name=None, res_name=None, res_num=None, pos=[None, None, None], element=None, atom_num=None, chain_id=None, segment_id=None, pdb_record=None):
        """Method for adding an atom to the structural data object.

        This method will create the key-value pair for the given atom.


        @keyword atom_name:     The atom name, e.g. 'H1'.
        @type atom_name:        str or None
        @keyword res_name:      The residue name.
        @type res_name:         str or None
        @keyword res_num:       The residue number.
        @type res_num:          int or None
        @keyword pos:           The position vector of coordinates.
        @type pos:              list (length = 3)
        @keyword element:       The element symbol.
        @type element:          str or None
        @keyword atom_num:      The atom number.
        @type atom_num:         int or None
        @keyword chain_id:      The chain identifier.
        @type chain_id:         str or None
        @keyword segment_id:    The segment identifier.
        @type segment_id:       str or None
        @keyword pdb_record:    The optional PDB record name, e.g. 'ATOM' or 'HETATM'.
        @type pdb_record:       str or None
        """

        # Append to all the arrays.
        self.atom_num.append(atom_num)
        self.atom_name.append(atom_name)
        self.bonded.append([])
        self.chain_id.append(chain_id)
        self.element.append(element)
        self.pdb_record.append(pdb_record)
        self.res_name.append(res_name)
        self.res_num.append(res_num)
        self.seg_id.append(segment_id)
        self.x.append(pos[0])
        self.y.append(pos[1])
        self.z.append(pos[2])


    def atom_connect(self, index1=None, index2=None):
        """Method for connecting two atoms within the data structure object.

        This method will append index2 to the array at bonded[index1] and vice versa.


        @keyword index1:        The index of the first atom.
        @type index1:           int
        @keyword index2:        The index of the second atom.
        @type index2:           int
        """

        # Update the bonded array structure, if necessary.
        if index2 not in self.bonded[index1]:
            self.bonded[index1].append(index2)
        if index1 not in self.bonded[index2]:
            self.bonded[index2].append(index1)


    def fill_object_from_pdb(self, records):
        """Method for generating a complete Structure_container object from the given PDB records.

        @param records:         A list of structural PDB records.
        @type records:          list of str
        """

        # Loop over the records.
        for record in records:
            # Parse the record.
            record = self.__parse_pdb_record(record)

            # Nothing to do.
            if not record:
                continue

            # Add the atom.
            if record[0] == 'ATOM' or record[0] == 'HETATM':
                # Attempt at determining the element, if missing.
                element = record[14]
                if not element:
                    element = self.__det_pdb_element(record[2])

                # Add.
                self.atom_add(pdb_record=record[0], atom_num=record[1], atom_name=record[2], res_name=record[4], chain_id=record[5], res_num=record[6], pos=[record[8], record[9], record[10]], segment_id=record[13], element=element)

            # Connect atoms.
            if record[0] == 'CONECT':
                # Loop over the atoms of the record.
                for i in xrange(len(record)-2):
                    # Skip if there is no record.
                    if record[i+2] == None:
                        continue

                    # Make the connection.
                    self.atom_connect(index1=self.__atom_index(record[1]), index2=self.__atom_index(record[i+2]))


    def fill_object_from_xyz(self, records):
        """Method for generating a complete Structure_container object from the given xyz records.

        @param records:         A list of structural xyz records.
        @type records:          list of str
        """

        # initialisation for atom number
        atom_number = 1

        # Loop over the records.
        for record in records:
            # Parse the record.
            record = self.__parse_xyz_record(record)

            # Nothing to do.
            if not record:
                continue

            # Add the atom.
            if len(record) == 4:
                # Attempt at determining the element, if missing.
                element = record[0]
                if not element:
                    element = self.__det_pdb_element(record[2])

                # Add.
                self.atom_add(atom_num=atom_number, pos=[record[1], record[2], record[3]], element=element)

                # Increment of atom number
                atom_number = atom_number + 1


    def from_xml(self, mol_node):
        """Recreate the MolContainer from the XML molecule node.

        @param mol_node:    The molecule XML node.
        @type mol_node:     xml.dom.minicompat.NodeList instance
        """

        # Recreate the current molecule container.
        xml_to_object(mol_node, self)


    def is_empty(self):
        """Check if the container is empty."""

        # Set attributes.
        if hasattr(self, 'mol_name'): return False
        if hasattr(self, 'file_name'): return False
        if hasattr(self, 'file_path'): return False
        if hasattr(self, 'file_mol_num'): return False
        if hasattr(self, 'file_model'): return False

        # Internal data structures.
        if not self.atom_num == []: return False
        if not self.atom_name == []: return False
        if not self.bonded == []: return False
        if not self.chain_id == []: return False
        if not self.element == []: return False
        if not self.pdb_record == []: return False
        if not self.res_name == []: return False
        if not self.res_num == []: return False
        if not self.seg_id == []: return False
        if not self.x == []: return False
        if not self.y == []: return False
        if not self.z == []: return False

        # Ok, now this thing must be empty.
        return True


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
        fill_object_contents(doc, mol_element, object=self, blacklist=list(self.__class__.__dict__.keys()))
