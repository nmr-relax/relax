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


    def from_xml(self, mol_nodes, id=None, file_version=1):
        """Recreate a molecule list data structure from the XML molecule nodes.

        @param mol_nodes:       The molecule XML nodes.
        @type mol_nodes:        xml.dom.minicompat.NodeList instance
        @keyword id:            The specific structural object ID string.  This can be 'scientific', 'internal', etc.
        @type id:               str
        @keyword file_version:  The relax XML version of the XML file.
        @type file_version:     int
        """

        # Test if empty.
        if not self.is_empty():
            raise RelaxFromXMLNotEmptyError(self.__class__.__name__)

        # Loop over the molecules.
        for mol_node in mol_nodes:
            # Some imports (here to break circular import issues).
            if id == 'internal':
                from pipe_control.structure.internal import MolContainer
            elif id == 'scientific':
                from pipe_control.structure.scientific import MolContainer

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
