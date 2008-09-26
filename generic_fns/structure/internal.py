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
"""Module containing the internal relax structural object."""

# Python module imports.
from numpy import array, float64, linalg, zeros
from os import path
from re import search
from string import split, strip, upper
from warnings import warn

# relax module imports.
from api_base import Base_struct_API
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import relax_re
from generic_fns.mol_res_spin import Selection
from relax_errors import RelaxError
from relax_io import open_read_file
from relax_warnings import RelaxWarning



class Internal(Base_struct_API):
    """The internal relax structural data object.

    The structural data object for this class is a container possessing a number of different arrays
    corresponding to different structural information.  These objects are described in the
    structural container docstring.
    """

    # Identification string.
    id = 'internal'


    def __atom_index(self, atom_num, struct_index):
        """Find the atom index corresponding to the given atom number.

        @param atom_num:        The atom number to find the index of.
        @type atom_num:         int
        @param struct_index:    The index of the structural container to extract the atom index
                                from.
        @type struct_index:     int
        @return:                The atom index corresponding to the atom.
        @rtype:                 int
        """

        # Loop over the atoms.
        for i in xrange(len(self.structural_data[struct_index].atom_num)):
            # Return the index.
            if self.structural_data[struct_index].atom_num[i] == atom_num:
                return i

        # Should not be here, the PDB connect records are incorrect.
        warn(RelaxWarning("The atom number " + `atom_num` + " from the CONECT record cannot be found within the ATOM and HETATM records."))


    def __bonded_atom(self, attached_atom, index, struct_index):
        """Find the atom named attached_atom directly bonded to the atom located at the index.

        @param attached_atom:   The name of the attached atom to return.
        @type attached_atom:    str
        @param index:           The index of the atom which the attached atom is attached to. 
        @type index:            int
        @param struct_index:    The index of the structure.
        @type struct_index:     int
        @return:                A tuple of information about the bonded atom.
        @rtype:                 tuple consisting of the atom number (int), atom name (str), element
                                name (str), and atomic position (Numeric array of len 3)
        """

        # Init.
        bonded_found = False
        struct = self.structural_data[struct_index]

        # No bonded atoms, so go find everything within 1.2 Angstroms and say they are bonded.
        if not struct.bonded[index]:
            self.__find_bonded_atoms(index, struct_index)

        # Loop over the bonded atoms.
        matching_list = []
        for bonded_index in struct.bonded[index]:
            if relax_re.search(struct.atom_name[bonded_index], attached_atom):
                matching_list.append(bonded_index)
        num_attached = len(matching_list)

        # Problem.
        if num_attached > 1:
            # Get the atom names.
            matching_names = []
            for i in matching_list:
                matching_names.append(struct.atom_name[i])

            # Return nothing but a warning.
            return None, None, None, None, None, 'More than one attached atom found: ' + `matching_names`

        # No attached atoms.
        if num_attached == 0:
            return None, None, None, None, None, "No attached atom could be found"

        # The bonded atom info.
        index = matching_list[0]
        bonded_num = struct.atom_num[index]
        bonded_name = struct.atom_name[index]
        element = struct.element[index]
        pos = [struct.x[index], struct.y[index], struct.z[index]]
        attached_name = struct.atom_name[index]

        # Return the information.
        return bonded_num, bonded_name, element, pos, attached_name, None


    def __fill_object_from_pdb(self, records, struct_index):
        """Method for generating a complete Structure_container object from the given PDB records.

        @param records:         A list of structural PDB records.
        @type records:          list of str
        @param struct_index:    The index of the structural container to add the data to.
        @type struct_index:     int
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
                self.atom_add(pdb_record=record[0], atom_num=record[1], atom_name=record[2], res_name=record[4], chain_id=record[5], res_num=record[6], pos=[record[8], record[9], record[10]], segment_id=record[13], element=record[14], struct_index=struct_index)

            # Connect atoms.
            if record[0] == 'CONECT':
                # Loop over the atoms of the record.
                for i in xrange(len(record)-2):
                    # Skip if there is no record.
                    if record[i+2] == None:
                        continue

                    # Make the connection.
                    self.atom_connect(index1=self.__atom_index(record[1], struct_index), index2=self.__atom_index(record[i+2], struct_index), struct_index=struct_index)


    def __find_bonded_atoms(self, index, struct_index, radius=1.2):
        """Find all atoms within a sphere and say that they are attached to the central atom.

        The found atoms will be added to the 'bonded' data structure.


        @param index:           The index of the central atom.
        @type index:            int
        @param struct_index:    The index of the structure.
        @type struct_index:     int
        """

        # Init.
        struct = self.structural_data[struct_index]

        # Central atom info.
        centre = array([struct.x[index], struct.y[index], struct.z[index]], float64)

        # Atom loop.
        for i in xrange(len(struct.atom_num)):
            # The atom's position.
            pos = array([struct.x[i], struct.y[i], struct.z[i]], float64)

            # The distance from the centre.
            dist = linalg.norm(centre-pos)

            # Connect the atoms if within the radius value.
            if dist < radius:
                self.atom_connect(index, i)


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

        @param res: The residue ID.
        @type res:  str
        @return:    The chemical name.
        @rtype:     str or None
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


    def __parse_models(self, file_path):
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
                    raise RelaxError, "The MODEL record " + `lines[i]` + " is corrupt, cannot read the PDB file."

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


    def __validate_data_arrays(self, struct):
        """Check the validity of the data arrays in the given structure object.

        @param struct:  The structural object.
        @type struct:   Structure_container instance
        """

        # The number of atoms.
        num = len(struct.atom_name)

        # Check the other lengths.
        if len(struct.bonded) != num and len(struct.chain_id) != num and len(struct.element) != num and len(struct.pdb_record) != num and len(struct.res_name) != num and len(struct.res_num) != num and len(struct.seg_id) != num and len(struct.x) != num and len(struct.y) != num and len(struct.z) != num:
            raise RelaxError, "The structural data is invalid."


    def atom_add(self, pdb_record=None, atom_num=None, atom_name=None, res_name=None, chain_id=None, res_num=None, pos=[None, None, None], segment_id=None, element=None, struct_index=None):
        """Method for adding an atom to the structural data object.

        This method will create the key-value pair for the given atom.


        @keyword pdb_record:    The optional PDB record name, e.g. 'ATOM' or 'HETATM'.
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
        @keyword struct_index:  The index of the structure to add the atom to.  If not supplied and
                                multiple structures or models are loaded, then the atom will be
                                added to all structures.
        @type struct_index:     None or int
        """


        # Loop over the structures.
        for i in xrange(len(self.structural_data)):
            # Skip non-matching structures.
            if struct_index != None and struct_index != i:
                continue

            # Append to all the arrays.
            self.structural_data[i].atom_num.append(atom_num)
            self.structural_data[i].atom_name.append(atom_name)
            self.structural_data[i].bonded.append([])
            self.structural_data[i].chain_id.append(chain_id)
            self.structural_data[i].element.append(element)
            self.structural_data[i].pdb_record.append(pdb_record)
            self.structural_data[i].res_name.append(res_name)
            self.structural_data[i].res_num.append(res_num)
            self.structural_data[i].seg_id.append(segment_id)
            self.structural_data[i].x.append(pos[0])
            self.structural_data[i].y.append(pos[1])
            self.structural_data[i].z.append(pos[2])


    def atom_connect(self, index1=None, index2=None, struct_index=None):
        """Method for connecting two atoms within the data structure object.

        This method will append index2 to the array at bonded[index1] and vice versa.


        @keyword index1:        The index of the first atom.
        @type index1:           int
        @keyword index2:        The index of the second atom.
        @type index2:           int
        @keyword struct_index:  The index of the structure to connect the atoms of.  If not supplied
                                and multiple structures or models are loaded, then the atoms will be
                                connected within all structures.
        @type struct_index:     None or int
        """

        # Loop over the structures.
        for i in xrange(len(self.structural_data)):
            # Skip non-matching structures.
            if struct_index != None and struct_index != i:
                continue

            # Update the bonded array structure, if necessary.
            if index2 not in self.structural_data[i].bonded[index1]:
                self.structural_data[i].bonded[index1].append(index2)
            if index1 not in self.structural_data[i].bonded[index2]:
                self.structural_data[i].bonded[index2].append(index1)


    def atom_loop(self, atom_id=None, str_id=None, model_num_flag=False, mol_name_flag=False, res_num_flag=False, res_name_flag=False, atom_num_flag=False, atom_name_flag=False, element_flag=False, pos_flag=False, ave=False):
        """Generator function for looping over all atoms in the internal relax structural object.

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
        @keyword ave:               A flag which if True will result in this method returning the
                                    average atom properties across all loaded structures.
        @type ave:                  bool
        @return:                    A tuple of atomic information, as described in the docstring.
        @rtype:                     tuple consisting of optional molecule name (str), residue number
                                    (int), residue name (str), atom number (int), atom name(str),
                                    element name (str), and atomic position (array of len 3).
        """

        # Generate the selection object.
        sel_obj = Selection(atom_id)

        # Average properties mode.
        if ave:
            # Loop over all atoms.
            for i in xrange(len(self.structural_data[0].atom_name)):
                # Skip non-matching atoms.
                if sel_obj and not sel_obj.contains_spin(self.structural_data[0].atom_num[i], self.structural_data[0].atom_name[i], self.structural_data[0].res_num[i], self.structural_data[0].res_name[i]):
                    continue

                # Initialise.
                model = None
                mol_name = None
                res_num = self.structural_data[0].res_num[i]
                res_name = self.structural_data[0].res_name[i]
                atom_num = self.structural_data[0].atom_num[i]
                atom_name = self.structural_data[0].atom_name[i]
                element = self.structural_data[0].element[i]
                pos = zeros(3, float64)

                # Loop over the structures.
                for struct in self.structural_data:
                    # Some sanity checks.
                    if struct.atom_num[i] != atom_num:
                        raise RelaxError, "The loaded structures do not contain the same atoms.  The average structural properties can not be calculated."

                    # Sum the atom positions.
                    pos = pos + array([struct.x[i], struct.y[i], struct.z[i]], float64)

                # Average the position array.
                pos = pos / len(self.structural_data)

                # Build the tuple to be yielded.
                atomic_tuple = ()
                if model_num_flag:
                    atomic_tuple = atomic_tuple + (model,)
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

        # Individual structure mode.
        else:
            # Loop over the models.
            for c in xrange(len(self.structural_data)):
                # Explicit structure identifier.
                if type(str_id) == int:
                    if str_id != c:
                        continue

                # Alias the structural data.
                struct = self.structural_data[c]

                # Loop over all atoms.
                for i in xrange(len(struct.atom_name)):
                    # Skip non-matching atoms.
                    if sel_obj and not sel_obj.contains_spin(struct.atom_num[i], struct.atom_name[i], struct.res_num[i], struct.res_name[i]):
                        continue

                    # Build the tuple to be yielded.
                    atomic_tuple = ()
                    if model_num_flag:
                        atomic_tuple = atomic_tuple + (struct.model,)
                    if mol_name_flag:
                        atomic_tuple = atomic_tuple + (None,)
                    if res_num_flag:
                        atomic_tuple = atomic_tuple + (struct.res_num[i],)
                    if res_name_flag:
                        atomic_tuple = atomic_tuple + (struct.res_name[i],)
                    if atom_num_flag:
                        atomic_tuple = atomic_tuple + (struct.atom_num[i],)
                    if atom_name_flag:
                        atomic_tuple = atomic_tuple + (struct.atom_name[i],)
                    if element_flag:
                        atomic_tuple = atomic_tuple + (struct.element[i],)
                    if pos_flag:
                        atomic_tuple = atomic_tuple + (array([struct.x[i], struct.y[i], struct.z[i]], float64),)

                    # Yield the information.
                    yield atomic_tuple


    def bond_vectors(self, atom_id=None, attached_atom=None, struct_index=None, return_name=False, return_warnings=False):
        """Find the bond vector between the atoms of 'attached_atom' and 'atom_id'.

        @keyword atom_id:           The molecule, residue, and atom identifier string.  This must
                                    correspond to a single atom in the system.
        @type atom_id:              str
        @keyword attached_atom:     The name of the bonded atom.
        @type attached_atom:        str
        @keyword struct_index:      The index of the structure to return the vectors from.  If not
                                    supplied and multiple structures/models exist, then vectors from
                                    all structures will be returned.
        @type struct_index:         None or int
        @keyword return_name:       A flag which if True will cause the name of the attached atom to
                                    be returned together with the bond vectors.
        @type return_name:          bool
        @keyword return_warnings:   A flag which if True will cause warning messages to be returned.
        @type return_warnings:      bool
        @return:                    The list of bond vectors for each structure.
        @rtype:                     list of numpy arrays (or a tuple if return_name or
                                    return_warnings are set)
        """

        # Generate the selection object, using upper case to avoid PDB file issues.
        sel_obj = Selection(upper(atom_id))

        # Initialise some objects.
        vectors = []
        attached_name = None
        warnings = None

        # Loop over the structures.
        for i in xrange(len(self.structural_data)):
            # Single structure.
            if struct_index and struct_index != i:
                continue

            # Alias.
            struct = self.structural_data[i]

            # Init.
            atom_found = False

            # Loop over all atoms.
            for j in xrange(len(struct.atom_name)):
                # Skip non-matching atoms.
                if sel_obj and not sel_obj.contains_spin(struct.atom_num[j], struct.atom_name[j], struct.res_num[j], struct.res_name[j]):
                    continue

                # More than one matching atom!
                if atom_found:
                    raise RelaxError, "The atom_id argument " + `atom_id` + " must correspond to a single atom."

                # The atom has been found, so store some info.
                atom_found = True
                index = j

            # Found the atom.
            if atom_found:
                # Get the atom bonded to this structure/molecule/residue/atom.
                bonded_num, bonded_name, element, pos, attached_name, warnings = self.__bonded_atom(attached_atom, index, i)

                # No bonded atom.
                if (bonded_num, bonded_name, element) == (None, None, None):
                    continue

                # The bond vector.
                vector = array(pos, float64) - array([struct.x[index], struct.y[index], struct.z[index]], float64)

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


    def load_pdb(self, file_path, model=None, verbosity=False):
        """Method for loading structures from a PDB file.

        @param file_path:   The full path of the PDB file.
        @type file_path:    str
        @param model:       The structural model to use.
        @type model:        int
        @keyword verbosity: A flag which if True will cause messages to be printed.
        @type verbosity:    bool
        """

        # Initial print out.
        if verbosity:
            print "Internal relax PDB parser.\n"

        # Set the file name and path.
        expanded = path.split(file_path)
        self.path.append(expanded[0])
        self.file.append(expanded[1])

        # Store the model number.
        self.model = model

        # Use pointers (references) if the PDB data exists in another pipe.
        for data_pipe in ds:
            if hasattr(data_pipe, 'structure'):
                # Loop over the structures.
                for i in xrange(len(data_pipe.structure)):
                    if data_pipe.structure.file[i] == expanded[1] and data_pipe.structure[i].model == model and data_pipe.structure.id == 'internal':
                        # Make a pointer to the data.
                        self.structural_data = data_pipe.structure.structural_data[i]

                        # Print out.
                        if verbosity:
                            print "Using the structures from the data pipe " + `data_pipe.pipe_name` + "."
                            for i in xrange(len(self.structural_data)):
                                print self.structural_data[i]

                        # Exit this function.
                        return

        # Print out.
        if verbosity:
            if type(model) == int:
                print "Loading structure " + `model` + " from the PDB file."
            else:
                print "Loading all structures from the PDB file."

        # Loop over all models in the PDB file.
        for model_num, records in self.__parse_models(file_path):
            # Only load the desired model.
            if model != None and model != model_num:
                continue

            # Initialise and fill the structural data object.
            self.structural_data.append(Structure_container())
            self.structural_data[-1].model = model_num
            self.__fill_object_from_pdb(records, len(self.structural_data)-1)


    def write_pdb(self, file, struct_index=None):
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
        @param struct_index:    The index of the structural container to write.  If None, all
                                structures will be written.
        @type struct_index:     int
        """

        # Initialise record counts.
        num_hetatm = 0
        num_atom = 0
        num_ter = 0
        num_conect = 0

        # Print out.
        print "\nCreating the PDB records\n"

        # Write some initial remarks.
        print "REMARK"
        file.write("REMARK   4 THIS FILE COMPLIES WITH FORMAT V. 3.1, 1-AUG-2007\n")
        file.write("REMARK  40 CREATED BY RELAX (HTTP://NMR-RELAX.COM)\n")
        num_remark = 2


        ####################
        # Hetrogen section #
        ####################

        # Initialise the hetrogen info array.
        het_data = []
        het_data_coll = []

        # Loop over the structures.
        for index in xrange(len(self.structural_data)):
            # Skip non-matching structures.
            if struct_index != None and struct_index != index:
                continue

            # Alias the structure container.
            struct = self.structural_data[index]

            # Check the validity of the data.
            self.__validate_data_arrays(struct)

            # Append an empty array for this structure.
            het_data.append([])

            # Collect the non-standard residue info.
            for i in xrange(len(struct.atom_name)):
                # Skip non-HETATM records and HETATM records with no residue info.
                if struct.pdb_record[i] != 'HETATM' or struct.res_name[i] == None:
                    continue

                # If the residue is not already stored initialise a new het_data element.
                # (residue number, residue name, chain ID, number of atoms, atom count array).
                if not het_data[index] or not struct.res_num[i] == het_data[index][-1][0]:
                    het_data[index].append([struct.res_num[i], struct.res_name[i], struct.chain_id[i], 0, []])

                    # Catch missing chain_ids.
                    if het_data[index][-1][2] == None:
                        het_data[index][-1][2] = ''

                # Total atom count.
                het_data[index][-1][3] = het_data[index][-1][3] + 1

                # Find if the atom has already a count entry.
                entry = False
                for j in xrange(len(het_data[index][-1][4])): 
                    if struct.element[i] == het_data[index][-1][4][j][0]:
                        entry = True

                # Create a new specific atom count entry.
                if not entry:
                    het_data[index][-1][4].append([struct.element[i], 0])

                # Increment the specific atom count.
                for j in xrange(len(het_data[index][-1][4])): 
                    if struct.element[i] == het_data[index][-1][4][j][0]:
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
                        if het_data_coll[i][1] != het_data[index][i][1]:
                            raise RelaxError, "The " + `het_data[index][i][1]` + " residue name of hetrogen " + `het_data[index][i][0]` + " " + het_data[index][i][1] + " of structure " + `index` + " does not match the " + `het_data_coll[j][1]` + " name of the previous structures."

                        elif het_data_coll[i][2] != het_data[index][i][2]:
                            raise RelaxError, "The hetrogen chain id " + `het_data[index][i][2]` + " does not match " + `het_data_coll[j][2]` + " of residue " + `het_data_coll[j][0]` + " " + het_data_coll[j][1] + " of the previous structures."

                        elif het_data_coll[i][3] != het_data[index][i][3]:
                            raise RelaxError, "The " + `het_data[index][i][3]` + " atoms of hetrogen " + `het_data_coll[j][0]` + " " + het_data_coll[j][1] + " of structure " + `index` + " does not match the " + `het_data_coll[j][3]` + " of the previous structures."

                        elif het_data_coll[i][4] != het_data[index][i][4]:
                            raise RelaxError, "The atom counts " + `het_data[index][i][4]` +  " for the hetrogen residue " + `het_data_coll[j][0]` + " " + het_data_coll[j][1] + " of structure " + `index` + " do not match the counts " + `het_data_coll[j][4]` + " of the previous structures."

                # If there is no match, add the new residue to the collective.
                if not found:
                    het_data_coll.append(het_data[index][i])


        # The HET records.
        ##################

        # Print out.
        print "HET"

        # Write the HET records.
        for het in het_data_coll:
            file.write("%-6s %3s  %1s%4s%1s  %5s     %-40s\n" % ('HET', het[2], het[1], het[0], '', het[3], ''))


        # The HETNAM records.
        #####################

        # Print out.
        print "HETNAM"

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
        print "FORMUL"

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
                formula = formula + atom_count[0] + `atom_count[1]`

            # The FORMUL record (chemical formula).
            file.write("%-6s  %2s  %3s %2s%1s%-51s\n" % ('FORMUL', het[0], het[1], '', '', formula))


        ######################
        # Coordinate section #
        ######################

        # Loop over the structures.
        for index in xrange(len(self.structural_data)):
            # Skip non-matching structures.
            if struct_index != None and struct_index != index:
                continue

            # Alias the structure container.
            struct = self.structural_data[index]


            # MODEL record, for multiple structures.
            ########################################

            if not struct_index and len(self.structural_data) > 1:
                # Print out.
                print "\nMODEL " + `index+1`

                # Write the model record.
                file.write("%-6s    %4i\n" % ('MODEL', index+1))


            # Add the atomic coordinate records (ATOM, HETATM, and TER).
            ############################################################

            # Print out.
            print "ATOM, HETATM, TER"

            # Loop over the atomic data.
            for i in xrange(len(struct.atom_name)):
                # Aliases.
                atom_num = struct.atom_num[i]
                atom_name = struct.atom_name[i]
                res_name = struct.res_name[i]
                chain_id = struct.chain_id[i]
                res_num = struct.res_num[i]
                x = struct.x[i]
                y = struct.y[i]
                z = struct.z[i]
                seg_id = struct.seg_id[i]
                element = struct.element[i]

                # Replace None with ''.
                if atom_name == None:
                    atom_name = ''
                if res_name == None:
                    res_name = ''
                if chain_id == None:
                    chain_id = ''
                if res_num == None:
                    res_num = ''
                if x == None:
                    x = ''
                if y == None:
                    y = ''
                if z == None:
                    z = ''
                if seg_id == None:
                    seg_id = ''
                if element == None:
                    element = ''

                # Write the ATOM record.
                if struct.pdb_record[i] == 'ATOM':
                    file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('ATOM', atom_num, atom_name, '', res_name, chain_id, res_num, '', x, y, z, 1.0, 0, seg_id, element, ''))
                    num_atom = num_atom + 1

                # Write the HETATM record.
                if struct.pdb_record[i] == 'HETATM':
                    file.write("%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s\n" % ('HETATM', atom_num, atom_name, '', res_name, chain_id, res_num, '', x, y, z, 1.0, 0, seg_id, element, ''))
                    num_hetatm = num_hetatm + 1

            # Finish off with the TER record.
            file.write("%-6s%5s      %3s %1s%4s%1s\n" % ('TER', atom_num+1, res_name, chain_id, res_num, ''))
            num_ter = num_ter + 1


            # ENDMDL record, for multiple structures.
            ########################################

            if not struct_index and len(self.structural_data) > 1:
                # Print out.
                print "ENDMDL"

                # Write the model record.
                file.write("%-6s\n" % 'ENDMDL')


            # Create the CONECT records.
            ############################

            # Print out.
            print "CONECT"

            for i in xrange(len(struct.atom_name)):
                # No bonded atoms, hence no CONECT record is required.
                if not len(struct.bonded[i]):
                    continue

                # Initialise some data structures.
                flush = 0
                bonded_index = 0
                bonded = ['', '', '', '']

                # Loop over the bonded atoms.
                for j in xrange(len(struct.bonded[i])):
                    # End of the array, hence create the CONECT record in this iteration.
                    if j == len(struct.bonded[i])-1:
                        flush = True

                    # Only four covalently bonded atoms allowed in one CONECT record.
                    if bonded_index == 3:
                        flush = True

                    # Get the bonded atom index.
                    bonded[bonded_index] = struct.bonded[i][j]

                    # Increment the bonded_index value.
                    bonded_index = bonded_index + 1

                    # Generate the CONECT record and increment the counter.
                    if flush:
                        # Convert the atom indices to atom numbers.
                        for k in range(4):
                            if bonded[k] != '':
                                bonded[k] = struct.atom_num[bonded[k]]

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
        print "\nMASTER"

        # Write the MASTER record.
        file.write("%-6s    %5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n" % ('MASTER', 0, 0, len(het_data_coll), 0, 0, 0, 0, 0, num_atom+num_hetatm, num_ter, num_conect, 0))


        # END.
        ######

        # Print out.
        print "END"

        # Write the END record.
        file.write("END\n")


class Structure_container:
    """The container for the structural information.

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
        """Initialise all the arrays."""

        # The model.
        self.model = None

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
