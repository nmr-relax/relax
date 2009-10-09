###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2008 Edward d'Auvergne                        #
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

# Python module imports.
from re import search

# relax module imports.
from relax_xml import fill_object_contents, xml_to_object


# Empty data container.
#######################

class Element(object):
    """Empty data container."""

    def __repr__(self):
        # Header.
        text = "%-25s%-100s\n\n" % ("Data structure", "Value")

        # Data structures.
        for name in dir(self):
            # Skip Element and derived class methods.
            if name in list(Element.__dict__.keys()) or name in list(self.__class__.__dict__.keys()):
                continue

            # Skip special objects.
            if search("^_", name):
                continue

            # Generate the text.
            text = text + "%-25s%-100s\n" % (name, repr(getattr(self, name)))

        # Return the lot.
        return text


    def from_xml(self, exp_info_node):
        """Recreate the container data structure from the XML container node.

        @param exp_info_node:   The container XML node.
        @type exp_info_node:    xml.dom.minicompat.Element instance
        """

        # Recreate all the data structures.
        xml_to_object(exp_info_node, self)


    def is_empty(self):
        """Method for testing if the Element container is empty.

        @return:    True if the Element container is empty, False otherwise.
        @rtype:     bool
        """

        # An object has been added to the container.
        for name in dir(self):
            # Skip Element and derived class methods.
            if name in list(Element.__dict__.keys()) or name in list(self.__class__.__dict__.keys()):
                continue

            # Skip special objects.
            if search("^__", name):
                continue

            # An object has been added.
            return False

        # The Element container is empty.
        return True


    def to_xml(self, doc, element):
        """Create an XML element for the container.

        The variables self.name and self.desc must exist.


        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the container element to.
        @type element:  XML element object
        """

        # Create the container element and add it to the higher level element.
        tensor_element = doc.createElement(self.name)
        element.appendChild(tensor_element)

        # Set the container attributes.
        tensor_element.setAttribute('desc', self.desc)

        # Add all simple python objects within the PipeContainer to the pipe element.
        fill_object_contents(doc, tensor_element, object=self, blacklist=['type'] + list(self.__class__.__dict__.keys()))
