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


# Python module imports.
from math import sqrt
from numpy import dot, float64, zeros
from warnings import warn

# Scientific Python import.
module_avail = True
try:
    import Scientific.IO.PDB
except ImportError:
    module_avail = False

# relax module imports.
from api_base import Base_struct_API
from data import Data as relax_data_store
from generic_fns.selection import parse_token, tokenise, wildcard_match
from relax_errors import RelaxNoPdbChainError, RelaxNoResError, RelaxPdbLoadError
from relax_warnings import RelaxNoAtomWarning, RelaxZeroVectorWarning


class Scientific_data(Base_struct_API):
    """The Scientific Python specific data object."""

    # Identification string.
    id = 'scientific'


    def __molecule_loop(self, struct, molecules):
        """Generator function for looping over all molecules in the Scientific PDB data objects.

        @param struct:      The individual structure object, the highest level Scientific Python PDB
                            object.
        @type struct:       Scientific Python PDB object
        @param molecules:   A list of molecule names.  If non-empty, only molecules found in this
                            list will be returned.
        @type molecules:    list of str
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
                if molecules and not wildcard_match(mol_name, molecules):
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
                if molecules and not wildcard_match(mol_name, molecules):
                    continue

                # Yield the molecule and its name.
                yield chain, mol_name, 'nucleic acid'

        # Other molecules.
        if struct.molecules:
            for key in struct.molecules:
                # Yield the molecule and its name.
                yield struct.molecules[key], key, 'other'


    def __residue_loop(self, mol, mol_type, residues):
        """Generator function for looping over all residues in the Scientific PDB data objects.

        @param mol:         The individual residue Scientific Python PDB data object.
        @type mol:          Scientific Python PDB object
        @param residues:    A list of residue names.  If non-empty, only residues found in this list
                            will be returned.
        @type residues:     list of str
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
                if residues and not (wildcard_match(res_name, residues) or res_num in residues):
                    continue

                # Yield the residue info.
                yield res, res_num, res_name

        # Other molecules.
        else:
            for res in mol:
                # Skip non-matching residues.
                if residues and not (wildcard_match(res.name, residues) or res.number in residues):
                    continue

                # Yield the residue info.
                yield res, res.number, res.name


    def atom_loop(self, atom_id=None, model_num_flag=False, mol_name_flag=False, res_num_flag=False, res_name_flag=False, atom_num_flag=False, atom_name_flag=False, element_flag=False, pos_flag=False):
        """Generator function for looping over all atoms in the Scientific Python data objects.

        @keyword atom_id:           The molecule, residue, and atom identifier string.  Only atoms
                                    matching this selection will be yielded.
        @type atom_id:              str
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
        @return:                    A tuple of atomic information, as described in the docstring.
        @rtype:                     tuple consisting of optional molecule name (str), residue number
                                    (int), residue name (str), atom number (int), atom name(str),
                                    element name (str), and atomic position (array of len 3).
        """

        # Split up the selection string.
        mol_token, res_token, atom_token = tokenise(atom_id)

        # Parse the tokens.
        molecules = parse_token(mol_token)
        residues = parse_token(res_token)
        atoms = parse_token(atom_token)

        # Loop over the models.
        for struct in self.structural_data:
            # Loop over each individual molecule.
            for mol, mol_name, mol_type in self.__molecule_loop(struct, molecules):
                # Loop over the residues of the protein in the PDB file.
                for res, res_num, res_name in self.__residue_loop(mol, mol_type, residues):
                    # Loop over the atoms of the residue.
                    for atom in res:
                        # Atom number, name, and position.
                        atom_num = atom.properties['serial_number']
                        atom_name = atom.name
                        element = atom.properties['element']
                        pos = atom.position.array

                        # Skip non-matching atoms.
                        if atom_token and not (wildcard_match(atom_name, atoms) or atom_num in atoms):
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


    def load_structures(self, file_path, model, verbosity=False):
        """Function for loading the structures from the PDB file.

        @param file_path:   The full path of the file.
        @type file_path:    str
        @param model:       The PDB model to use.
        @type model:        int
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
        for data_pipe in relax_data_store:
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


    def xh_vector(self, spin, structure=None, unit=True):
        """Function for calculating/extracting the XH vector from the loaded structure.

        @param spin:        The spin system data container.
        @type spin:         SpinContainer instance
        @keyword structure: The structure number to get the XH vector from.  If set to None and
                            multiple structures exist, then the XH vector will be averaged across
                            all structures.
        @type structure:    int
        @keyword unit:      A flag which if set will cause the function to return the unit XH vector
                            rather than the full vector.
        @type unit:         bool
        @return:            The XH vector (or unit vector if the unit flag is set).
        @rtype:             list or None
        """

        # Initialise.
        vector_array = []
        ave_vector = zeros(3, float64)

        # Loop over the structures.
        for i in xrange(self.num_str()):
            # The vectors from a specific structure.
            if structure != None and structure != i:
                continue

            # Reassign the first peptide or nucleotide chain of the first structure.
            if self.structural_data[i].peptide_chains:
                pdb_residues = self.structural_data[i].peptide_chains[0].residues
            elif self.structural_data[i].nucleotide_chains:
                pdb_residues = self.structural_data[i].nucleotide_chains[0].residues
            else:
                raise RelaxNoPdbChainError

            # Find the corresponding residue in the PDB.
            pdb_res = None
            for k in xrange(len(pdb_residues)):
                if spin.num == pdb_residues[k].number:
                    pdb_res = pdb_residues[k]
                    break
            if pdb_res == None:
                raise RelaxNoResError, spin.num

            # Test if the proton atom exists for residue i.
            if not pdb_res.atoms.has_key(spin.proton):
                warn(RelaxNoAtomWarning(spin.proton, spin.num))

            # Test if the heteronucleus atom exists for residue i.
            elif not pdb_res.atoms.has_key(spin.heteronuc):
                warn(RelaxNoAtomWarning(spin.heteronuc, spin.num))

            # Calculate the vector.
            else:
                # Get the proton position.
                posH = pdb_res.atoms[spin.proton].position.array

                # Get the heteronucleus position.
                posX = pdb_res.atoms[spin.heteronuc].position.array

                # Calculate the XH bond vector.
                vector = posH - posX

                # Unit vector.
                if unit:
                    # Normalisation factor.
                    norm_factor = sqrt(dot(vector, vector))

                    # Test for zero length.
                    if norm_factor == 0.0:
                        warn(RelaxZeroVectorWarning(spin.num))

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
