###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""The API for accessing, creating, and modifying structural information.

The full API is documented within this base class object.  Each available API call is given as a
prototype method stub (or functional method) with all arguments, raised errors, and return values
documented.
"""

# relax module import.
from relax_errors import RelaxImplementError


class Base_struct_API:
    """The structural object base class.

    All API methods are prototyped here as stub methods.
    """

    # Identification string.
    id = 'API'


    def __init__(self):
        """Initialise the structural object."""

        # The parser specific data object.
        self.structural_data = []


    def atom_add(self, pdb_record=None, atom_num=None, atom_name=None, res_name=None, chain_id=None, res_num=None, pos=[None, None, None], segment_id=None, element=None, model=None):
        """Prototype method stub for adding an atom to the structural data object.

        This method will create the key-value pair for the given atom.


        @keyword pdb_record:    The optional PDB record name, e.g. 'ATOM', 'HETATM', or 'TER'.
        @type pdb_record:       str or None
        @keyword atom_num:      The atom number.
        @type atom_num:         int or None
        @keyword atom_name:     The atom name, e.g. 'H1'.
        @type atom_name:        str or None
        @keyword res_name:      The residue name.
        @type res_name:         str or None
        @keyword chain_id:      The chain identifier.
        @type chain_id:         str or None
        @keyword res_num:       The residue number.
        @type res_num:          int or None
        @keyword pos:           The position vector of coordinates.
        @type pos:              list (length = 3)
        @keyword segment_id:    The segment identifier.
        @type segment_id:       str or None
        @keyword element:       The element symbol.
        @type element:          str or None
        @keyword model:         The model to add the atom to.  If not supplied and multiple models
                                exist, then the atom will be added to all models.
        @type model:            None or int
        """

        # Raise the error.
        raise RelaxImplementError


    def atom_connect(self, index1=None, index2=None, model=None):
        """Prototype method stub for connecting two atoms within the data structure object.

        This method should connect the atoms corresponding to the two indecies.


        @keyword index1:    The index of the first atom.
        @type index1:       int
        @keyword index2:    The index of the second atom.
        @type index2:       int
        @keyword model:     The model to add the atom to.  If not supplied and multiple models
                            exist, then the atom will be added to all models.
        @type model:        None or int
        """

        # Raise the error.
        raise RelaxImplementError


    def atom_loop(self, atom_id=None, model_num_flag=False, mol_name_flag=False, res_num_flag=False, res_name_flag=False, atom_num_flag=False, atom_name_flag=False, element_flag=False, pos_flag=False):
        """Prototype generator method stub for looping over all atoms in the structural data object.

        This method should be designed as a generator (http://www.python.org/dev/peps/pep-0255/).
        It should loop over all atoms of the system yielding the following atomic information, if
        the corresponding flag is True, in tuple form:

            1.  Model number.
            2.  Molecule name.
            3.  Residue number.
            4.  Residue name.
            5.  Atom number.
            6.  Atom name.
            7.  The element name (its atomic symbol and optionally the isotope, e.g. 'N', 'Mg',
                '17O', '13C', etc).
            8.  The position of the atom in Euclidean space.


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

        # Raise the error.
        raise RelaxImplementError


    def attached_atom(self, atom_id=None, attached_atom=None, model=None):
        """Prototype method stub for finding the atom 'attached_atom' bonded to the atom 'atom_id'.

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

        # Raise the error.
        raise RelaxImplementError


    def bond_vectors(self, atom_id=None, attached_atom=None, model=None):
        """Prototype method stub for finding the bond vectors between 'attached_atom' and 'atom_id'.

        @keyword atom_id:       The molecule, residue, and atom identifier string.  This must
                                correspond to a single atom in the system.
        @type atom_id:          str
        @keyword attached_atom: The name of the bonded atom.
        @type attached_atom:    str
        @keyword model:         The model to return the vectors information from.  If not
                                supplied and multiple models exist, then the returned data will
                                contain the vectors for all models.
        @type model:            None or int
        @return:                The list of bond vectors for each model.
        @rtype:                 list of numpy arrays
        """

        # Raise the error.
        raise RelaxImplementError


    def load_pdb(self, file_path, model=None, verbosity=False):
        """Prototype method stub for loading structures from a PDB file.

        This inherited prototype method is a stub which, if the functionality is desired, should be
        overwritten by the derived class.


        @param file_path:   The full path of the PDB file.
        @type file_path:    str
        @param model:       The structural model to use.
        @type model:        int
        @keyword verbosity: A flag which if True will cause messages to be printed.
        @type verbosity:    bool
        """

        # Raise the error.
        raise RelaxImplementError


    def num_models(self):
        """Method for returning the number of loaded models (i.e. number of NMR models, etc.).

        @return:    The number of models which have been loaded.
        @rtype:     int
        """

        return len(self.structural_data)


    def terminate(self, model=None):
        """Prototype method stub for terminating the structural chain.

        @keyword model:     The model to add the atom to.  If not supplied and multiple models
                            exist, then the atom will be added to all models.
        @type model:        None or int
        """

        # Raise the error.
        raise RelaxImplementError


    def write_pdb(self, file):
        """Prototype method stub for the creation of a PDB file from the structural data.

        The PDB records
        ===============

        The following information about the PDB records has been taken from the "Protein Data Bank
        Contents Guide: Atomic Coordinate Entry Format Description" version 2.1 (draft),
        October 25, 1996.

        HET record
        ----------

        The HET record describes non-standard residues.  The format is of the record is::
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
        the record is::
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

        The chemical formula for non-standard groups. The format is of the record is::
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
        The format is of the record is::
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
        groups.  The format is of the record is::
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

        I{"The TER record has the same residue name, chain identifier, sequence number and insertion
        code as the terminal residue. The serial number of the TER record is one number greater than
        the serial number of the ATOM/HETATM preceding the TER."}

        The format is of the record is::
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
        bonds.  The format is of the record is::
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

        The control record for bookkeeping.  The format is of the record is::
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

        The end of the PDB file.  The format is of the record is::
         __________________________________________________________________________________________
         |         |              |              |                                                |
         | Columns | Data type    | Field        | Definition                                     |
         |_________|______________|______________|________________________________________________|
         |         |              |              |                                                |
         |  1 -  6 | Record name  | "END   "     |                                                |
         |_________|______________|______________|________________________________________________|


        @param file:        The PDB file object.  This object must be writable.
        @type file:         file object
        """

        # Raise the error.
        raise RelaxImplementError
