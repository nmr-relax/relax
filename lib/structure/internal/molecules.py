###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
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
"""The objects representing molecules in the internal structural object."""

# relax module import.
from lib.errors import RelaxError, RelaxFromXMLNotEmptyError


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


    def _atom_index(self, atom_num):
        """Find the atom index corresponding to the given atom number.

        @param atom_num:        The atom number to find the index of.
        @type atom_num:         int
        @return:                The atom index corresponding to the atom.
        @rtype:                 int
        """

        # Loop over the atoms.
        for j in range(len(self.atom_num)):
            # Return the index.
            if self.atom_num[j] == atom_num:
                return j

        # Should not be here, the PDB connect records are incorrect.
        warn(RelaxWarning("The atom number " + repr(atom_num) + " from the CONECT record cannot be found within the ATOM and HETATM records."))


    def _det_pdb_element(self, atom_name):
        """Try to determine the element from the PDB atom name.

        @param atom_name:   The PDB atom name.
        @type atom_name:    str
        @return:            The element name, or None if unsuccessful.
        @rtype:             str or None
        """

        # Strip away the "'" character (for RNA, etc.).
        element = atom_name.strip("'")

        # Strip away atom numbering, from the front and end.
        element = element.strip(digits)

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


    def _parse_xyz_record(self, record):
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
        word = record.split()

        # ATOM and HETATM records.
        if len(word)==4:
            # Split up the record.
            fields.append(word[0])
            fields.append(word[1])
            fields.append(word[2])
            fields.append(word[3])

            # Loop over the fields.
            for i in range(len(fields)):
                # Strip all whitespace.
                fields[i] = fields[i].strip()

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
        @return:                The index of the added atom.
        @rtype:                 int
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

        # Return the index.
        return len(self.atom_num) - 1


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


    def fill_object_from_pdb(self, records, alt_loc_select=None):
        """Method for generating a complete Structure_container object from the given PDB records.

        @param records:             A list of structural PDB records.
        @type records:              list of str
        @keyword alt_loc_select:    The PDB ATOM record 'Alternate location indicator' field value to select which coordinates to use.
        @type alt_loc_select:       str or None
        """

        # Loop over the records.
        for record in records:
            # Nothing to do.
            if not record or record == '\n':
                continue

            # Add the atom.
            if record[:4] == 'ATOM' or record[:6] == 'HETATM':
                # Parse the record.
                if record[:4] == 'ATOM':
                    record_type, serial, name, alt_loc, res_name, chain_id, res_seq, icode, x, y, z, occupancy, temp_factor, element, charge = pdb_read.atom(record)
                if record[:6] == 'HETATM':
                    record_type, serial, name, alt_loc, res_name, chain_id, res_seq, icode, x, y, z, occupancy, temp_factor, element, charge = pdb_read.hetatm(record)

                # Handle the alternate locations.
                if alt_loc != None:
                    # Don't know what to do.
                    if alt_loc_select == None:
                        raise RelaxError("Multiple alternate location indicators are present in the PDB file, but the desired coordinate set has not been specified.")

                    # Skip non-matching locations.
                    if alt_loc != alt_loc_select:
                        continue

                # Attempt at determining the element, if missing.
                if not element:
                    element = self._det_pdb_element(name)

                # Add.
                self.atom_add(pdb_record=record_type, atom_num=serial, atom_name=name, res_name=res_name, chain_id=chain_id, res_num=res_seq, pos=[x, y, z], element=element)

            # Connect atoms.
            if record[:6] == 'CONECT':
                # Parse the record.
                record_type, serial, bonded1, bonded2, bonded3, bonded4 = pdb_read.conect(record)

                # Loop over the atoms of the record.
                for bonded in [bonded1, bonded2, bonded3, bonded4]:
                    # Skip if there is no record.
                    if not bonded:
                        continue

                    # Skip broken CONECT records (for when the record points to a non-existent atom).
                    if self._atom_index(serial) == None or self._atom_index(bonded) == None:
                        continue

                    # Make the connection.
                    self.atom_connect(index1=self._atom_index(serial), index2=self._atom_index(bonded))


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
            record = self._parse_xyz_record(record)

            # Nothing to do.
            if not record:
                continue

            # Add the atom.
            if len(record) == 4:
                # Add.
                self.atom_add(atom_name=record[0], atom_num=atom_number, pos=[record[1], record[2], record[3]], element=record[0])

                # Increment of atom number
                atom_number = atom_number + 1


    def from_xml(self, mol_node, file_version=1):
        """Recreate the MolContainer from the XML molecule node.

        @param mol_node:        The molecule XML node.
        @type mol_node:         xml.dom.minicompat.NodeList instance
        @keyword file_version:  The relax XML version of the XML file.
        @type file_version:     int
        """

        # Recreate the current molecule container.
        xml_to_object(mol_node, self, file_version=file_version)


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


    def last_residue(self):
        """Return the number of the last residue.

        @return:    The last residue number.
        @rtype:     int
        """

        # Return the number.
        return self.res_num[-1]


    def merge(self, mol_cont=None):
        """Merge the contents of the given molecule container into here.

        @keyword mol_cont:      The data structure for the molecule to merge.
        @type mol_cont:         MolContainer instance
        """

        # The current index.
        curr_index = len(self.atom_num)

        # Loop over all data.
        for i in range(len(mol_cont.atom_num)):
            # Add the atom.
            self.atom_add(atom_num=curr_index+i+1, atom_name=mol_cont.atom_name[i], res_name=mol_cont.res_name[i], res_num=mol_cont.res_num[i], pos=[mol_cont.x[i], mol_cont.y[i], mol_cont.z[i]], element=mol_cont.element[i], chain_id=mol_cont.chain_id[i], pdb_record=mol_cont.pdb_record[i])

            # Connect the atoms.
            for j in range(len(mol_cont.bonded[i])):
                self.atom_connect(index1=i+curr_index+1, index2=mol_cont.bonded[i][j]+curr_index+1)


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



class MolList(list):
    """List type data container for holding the different molecules of one model."""

    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        text = "Molecules.\n\n"
        text = text + "%-8s%-8s" % ("Index", "Name") + "\n"
        for i in range(len(self)):
            text = text + "%-8i%-8s" % (i, self[i].mol_name) + "\n"
        return text


    def add_item(self, mol_name=None, mol_cont=None):
        """Append the given MolContainer instance to the MolList.

        @keyword mol_name:      The molecule number.
        @type mol_name:         int
        @keyword mol_cont:      The data structure for the molecule.
        @type mol_cont:         MolContainer instance
        @return:                The new molecule container.
        @rtype:                 MolContainer instance
        """

        # If no molecule data exists, replace the empty first molecule with this molecule (just a renaming).
        if len(self) and self.is_empty():
            self[0].mol_name = mol_name

        # Otherwise append an empty MolContainer.
        else:
            # Test if the molecule already exists.
            for i in range(len(self)):
                if self[i].mol_name == mol_name:
                    raise RelaxError("The molecule '%s' already exists." % mol_name)

            # Append an empty MolContainer.
            self.append(mol_cont)

            # Set the name.
            self[-1].mol_name = mol_name

        # Return the container.
        return self[-1]


    def is_empty(self):
        """Method for testing if this MolList object is empty.

        @return:    True if this list only has one MolContainer and the molecule name has not
                    been set, False otherwise.
        @rtype:     bool
        """

        # No MolContainers.
        if len(self) == 0:
            return True

        # There is only one MolContainer and it is empty.
        if len(self) == 1 and hasattr(self[0], 'is_empty') and self[0].is_empty():
            return True

        # Otherwise.
        return False


    def from_xml(self, mol_nodes, file_version=1):
        """Recreate a molecule list data structure from the XML molecule nodes.

        @param mol_nodes:       The molecule XML nodes.
        @type mol_nodes:        xml.dom.minicompat.NodeList instance
        @keyword file_version:  The relax XML version of the XML file.
        @type file_version:     int
        """

        # Test if empty.
        if not self.is_empty():
            raise RelaxFromXMLNotEmptyError(self.__class__.__name__)

        # Loop over the molecules.
        for mol_node in mol_nodes:
            # Initialise a MolContainer instance.
            mol_cont = MolContainer()

            # Get the molecule name.
            name = mol_node.getAttribute('name')
            if name == 'None':
                name = None

            # Add the molecule to the MolList structure.
            self.add_item(mol_name=name, mol_cont=mol_cont)

            # Execute the specific MolContainer from_xml() method.
            self[-1].from_xml(mol_node, file_version=file_version)


    def merge_item(self, mol_name=None, mol_cont=None):
        """Mege the given MolContainer instance into a pre-existing molecule container.

        @keyword mol_name:      The molecule number.
        @type mol_name:         int
        @keyword mol_cont:      The data structure for the molecule.
        @type mol_cont:         MolContainer instance
        @return:                The new molecule container.
        @rtype:                 MolContainer instance
        """

        # Find the molecule to merge.
        index = None
        for i in range(len(self)):
            if self[i].mol_name == mol_name:
                index = i
                break

        # No molecule found.
        if index == None:
            raise RelaxError("The molecule '%s' to merge with cannot be found." % mol_name)

        # Merge the molecules.
        self[index].merge(mol_cont)

        # Return the container.
        return self[index]


    def to_xml(self, doc, element):
        """Create XML elements for each molecule.

        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the molecule XML elements to.
        @type element:  XML element object
        """

        # Loop over the molecules.
        for i in range(len(self)):
            # Add the molecule data.
            self[i].to_xml(doc, element)
