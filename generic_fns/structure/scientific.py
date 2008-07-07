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

# Module docstring.
"""Module containing the Scientific Python PDB specific structural object class."""

# Dependency check module.
import dep_check

# Python module imports.
from math import sqrt
from numpy import array, dot, float64, zeros
if dep_check.scientific_pdb_module:
    import Scientific.IO.PDB
from warnings import warn

# relax module imports.
from api_base import Base_struct_API
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import Selection, parse_token, tokenise
from relax_errors import RelaxError, RelaxNoPdbChainError, RelaxNoResError, RelaxPdbLoadError
from relax_warnings import RelaxNoAtomWarning, RelaxZeroVectorWarning


class Scientific_data(Base_struct_API):
    """The Scientific Python specific data object."""

    # Identification string.
    id = 'scientific'

    def __init__(self):
        """Initialise the class."""

        # Test for the PDB parser availability.
        if not dep_check.scientific_pdb_module:
            raise RelaxError, "The Scientific python PDB module Scientific.IO.PDB could not be imported."

        # The parser specific data object.
        self.structural_data = []


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

        # The attached atom is in the residue.
        if attached_atom in res.atoms:
            # The bonded atom object.
            bonded = res[attached_atom]

            # The bonded atom info.
            bonded_num = bonded.properties['serial_number']
            bonded_name = bonded.name
            element = bonded.properties['element']
            pos = bonded.position.array

            # The bonded atom has been found.
            bonded_found = True

        # Return the information.
        if bonded_found:
            return bonded_num, bonded_name, element, pos
        else:
            return None, None, None, None


    def __molecule_loop(self, struct, sel_obj=None):
        """Generator function for looping over molecules in the Scientific PDB data objects.

        @param struct:      The individual structure object, the highest level Scientific Python PDB
                            object.
        @type struct:       Scientific Python PDB object
        @keyword sel_obj:   The selection object.
        @type sel_obj:      instance of generic_fns.mol_res_spin.Selection
        @return:            A tuple of the Scientific Python PDB object representing a single
                            molecule, the molecule name, and molecule type.
        @rtype:             (Scientific Python PDB object, str, str)
        """

        # Protein.
        if struct.peptide_chains:
            for chain in struct.peptide_chains:
                # The molecule name.
                if hasattr(chain, 'chain_id') and chain.chain_id:
                    mol_name = chain.chain_id
                elif hasattr(chain, 'segment_id') and chain.segment_id:
                    mol_name = chain.segment_id
                else:
                    mol_name = None

                # Skip non-matching molecules.
                if sel_obj and not sel_obj.contains_mol(mol_name):
                    continue

                # Yield the molecule and its name.
                yield chain, mol_name, 'protein'

        # RNA/DNA.
        if struct.nucleotide_chains:
            for chain in struct.nucleotide_chains:
                # The molecule name.
                if hasattr(chain, 'chain_id') and chain.chain_id:
                    mol_name = chain.chain_id
                elif hasattr(chain, 'segment_id') and chain.segment_id:
                    mol_name = chain.segment_id
                else:
                    mol_name = None

                # Skip non-matching molecules.
                if sel_obj and not sel_obj.contains_mol(mol_name):
                    continue

                # Yield the molecule and its name.
                yield chain, mol_name, 'nucleic acid'

        # Other molecules.
        if struct.molecules:
            for key in struct.molecules:
                # Yield the molecule and its name.
                yield struct.molecules[key], key, 'other'


    def __residue_loop(self, mol, mol_name, mol_type, sel_obj=None):
        """Generator function for looping over all residues in the Scientific PDB data objects.

        @param mol:         The individual molecule Scientific Python PDB data object.
        @type mol:          Scientific Python PDB object
        @param mol_name:    The name of the molecule.
        @type mol_name:     str or None
        @param mol_type:    The type of the molecule.  This can be one of 'protein', 'nucleic acid',
                            or 'other'.
        @type mol_type:     str
        @keyword sel_obj:   The selection object.
        @type sel_obj:      instance of generic_fns.mol_res_spin.Selection
        @return:            A tuple of the Scientific Python PDB object representing a single
                            residue, the residue number, and residue name.
        @rtype:             (Scientific Python PDB object, str, str)
        """

        # Proteins, RNA, and DNA.
        if mol_type != 'other':
            # Loop over the residues of the protein in the PDB file.
            for res in mol.residues:
                # Residue number and name.
                if mol_type == 'nucleic acid':
                    res_name = res.name[-1]
                else:
                    res_name = res.name
                res_num = res.number

                # Skip non-matching residues.
                if sel_obj and not sel_obj.contains_res(res_num, res_name, mol_name):
                    continue

                # Yield the residue info.
                yield res, res_num, res_name

        # Other molecules.
        else:
            for res in mol:
                # Skip non-matching residues.
                if sel_obj and not sel_obj.contains_res(res.number, res.name, mol_name):
                    continue

                # Yield the residue info.
                yield res, res.number, res.name


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
        @return:                    A tuple of atomic information, as described in the docstring.
        @rtype:                     tuple consisting of optional molecule name (str), residue number
                                    (int), residue name (str), atom number (int), atom name(str),
                                    element name (str), and atomic position (array of len 3).
        """

        # Generate the selection object.
        sel_obj = Selection(atom_id)

        # Loop over the models.
        for struct in self.structural_data:
            # Loop over each individual molecule.
            for mol, mol_name, mol_type in self.__molecule_loop(struct, sel_obj):
                # Loop over the residues of the protein in the PDB file.
                for res, res_num, res_name in self.__residue_loop(mol, mol_name, mol_type, sel_obj):
                    # Loop over the atoms of the residue.
                    for atom in res:
                        # Atom number, name, and position.
                        atom_num = atom.properties['serial_number']
                        atom_name = atom.name
                        element = atom.properties['element']
                        pos = atom.position.array

                        # Skip non-matching atoms.
                        if sel_obj and not sel_obj.contains_spin(atom_num, atom_name, res_num, res_name, mol_name):
                            continue

                        # Build the tuple to be yielded.
                        atomic_tuple = ()
                        if model_num_flag:
                            atomic_tuple = atomic_tuple + (struct.model,)
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
        for struct in self.structural_data:
            # Init.
            atom_found = False

            # Skip non-matching models.
            if model != None and model != struct.model:
                continue

            # Loop over each individual molecule.
            for mol, mol_name, mol_type in self.__molecule_loop(struct, sel_obj):
                # Loop over the residues of the protein in the PDB file.
                for res, res_num, res_name in self.__residue_loop(mol, mol_type, sel_obj):
                    # Loop over the atoms of the residue.
                    for atom in res:
                        # Atom number, name, and position.
                        atom_num = atom.properties['serial_number']
                        atom_name = atom.name

                        # Skip non-matching atoms.
                        if sel_obj and not sel_obj.contains_spin(atom_num, atom_name, res_num, res_name, mol_name):
                            continue

                        # More than one matching atom!
                        if atom_found:
                            raise RelaxError, "The atom_id argument " + `atom_id` + " must correspond to a single atom."

                        # The atom has been found, so store some info.
                        atom_found = True
                        atom_num_match = atom_num
                        atom_name_match = atom_name
                        mol_type_match = mol_type
                        res_match = res

            # Found the atom.
            if atom_found:
                # Find the atom bonded to this model/molecule/residue/atom.
                bonded_num, bonded_name, element, pos = self.__find_bonded_atom(attached_atom, mol_type_match, res_match)

                # Append the position to the position array (converting from a Numeric array to a numpy array).
                pos_array.append(array(pos, float64))

        # Return the atom info.
        return bonded_num, bonded_name, element, pos_array


    def bond_vectors(self, atom_id=None, attached_atom=None, struct_index=None):
        """Find the bond vectors between the atoms of 'attached_atom' and 'atom_id'.

        @keyword atom_id:       The molecule, residue, and atom identifier string.  This must
                                correspond to a single atom in the system.
        @type atom_id:          str
        @keyword attached_atom: The name of the bonded atom.
        @type attached_atom:    str
        @keyword struct_index:  The index of the structure to return the vectors from.  If not
                                supplied and multiple structures/models exist, then vectors from all
                                structures will be returned.
        @type struct_index:     None or int
        @type struct_index:     None or int.
        @return:                The list of bond vectors for each structure.
        @rtype:                 list of numpy arrays
        """

        # Generate the selection object.
        sel_obj = Selection(atom_id)

        # Initialise some objects.
        vectors = []

        # Loop over the structures.
        for i in xrange(len(self.structural_data)):
            # Single structure.
            if struct_index and struct_index != i:
                continue

            # Init.
            atom_found = False

            # Loop over each individual molecule.
            for mol, mol_name, mol_type in self.__molecule_loop(self.structural_data[i], sel_obj):
                # Loop over the residues of the protein in the PDB file.
                for res, res_num, res_name in self.__residue_loop(mol, mol_name, mol_type, sel_obj):
                    # Loop over the atoms of the residue.
                    for atom in res:
                        # Atom number, name, and position.
                        atom_num = atom.properties['serial_number']
                        atom_name = atom.name

                        # Skip non-matching atoms.
                        if sel_obj and not sel_obj.contains_spin(atom_num, atom_name, res_num, res_name, mol_name):
                            continue

                        # More than one matching atom!
                        if atom_found:
                            raise RelaxError, "The atom_id argument " + `atom_id` + " must correspond to a single atom."

                        # The atom has been found, so store some info.
                        atom_found = True
                        pos_match = atom.position.array
                        mol_type_match = mol_type
                        res_match = res

            # Found the atom.
            if atom_found:
                # Find the atom bonded to this structure/molecule/residue/atom.
                bonded_num, bonded_name, element, pos = self.__find_bonded_atom(attached_atom, mol_type_match, res_match)

                # No bonded atom.
                if (bonded_num, bonded_name, element) == (None, None, None):
                    continue

                # The bond vector.
                vector = pos - pos_match

                # Append the vector to the vectors array (converting from a Numeric array to a numpy array).
                vectors.append(array(vector, float64))

        # Return the bond vectors.
        return vectors


    def load_pdb(self, file_path, model=None, verbosity=False):
        """Function for loading the structures from the PDB file.

        @param file_path:   The full path of the file.
        @type file_path:    str
        @param model:       The PDB model to use.
        @type model:        None or int
        @keyword verbosity: A flag which if True will cause messages to be printed.
        @type verbosity:    bool
        """

        # Initial print out.
        if verbosity:
            print "Scientific Python PDB parser.\n"

        # Store the file name (with full path).
        self.file_name = file_path

        # Store the model number.
        self.model = model

        # Use pointers (references) if the PDB data exists in another run.
        for data_pipe in ds:
            if hasattr(data_pipe, 'structure') and data_pipe.structure.file_name == file_path and data_pipe.structure.model == model:
                # Make a pointer to the data.
                self.structural_data = data_pipe.structure.structural_data

                # Print out.
                if verbosity:
                    print "Using the structures from the data pipe " + `data_pipe.pipe_name` + "."
                    for i in xrange(len(self.structural_data)):
                        print self.structural_data[i]

                # Exit this function.
                return

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

            # Place the structure in 'self.structural_data'.
            self.structural_data.append(str)


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

                # Place the structure in 'self.structural_data'.
                self.structural_data.append(str)

                # Increment i.
                i = i + 1
