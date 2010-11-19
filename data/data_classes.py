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
from numpy import ndarray
from types import ListType

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

            # Get the object.
            obj = getattr(self, name)

            # Numpy matrices.
            if isinstance(obj, ndarray) and  isinstance(obj[0], ndarray):
                spacer = '\n'
            else:
                spacer = ''

            # Generate the text.
            text = text + "%-25s%s%-100s\n" % (name, spacer, repr(obj))

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

        The variables self.element_name and self.element_desc must exist.


        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the container element to.
        @type element:  XML element object
        """

        # Create the container element and add it to the higher level element.
        container_element = doc.createElement(self.element_name)
        element.appendChild(container_element)

        # Set the container attributes.
        container_element.setAttribute('desc', self.element_desc)

        # Blacklist.
        blacklist = ['element_name', 'element_desc'] + list(Element.__dict__.keys()) + list(self.__class__.__dict__.keys())
        if hasattr(self, 'blacklist'):
            blacklist = blacklist + self.blacklist + ['blacklist']

        # Add all simple python objects within.
        fill_object_contents(doc, container_element, object=self, blacklist=blacklist)

        # Run any object to_xml() methods.
        for name in dir(self):
            # Skip certain objects.
            if search("^_", name):
                continue

            # Get the object.
            obj = getattr(self, name)

            # Test for and run to_xml().
            if hasattr(obj, 'to_xml'):
                obj.to_xml(doc, container_element)



# Empty data container.
#######################

class ContainerList(ListType):
    """List type data container for basic Element data containers.

    The elements of this list should be Element instances.
    """

    def __repr__(self):
        """Replacement function for displaying an instance of this class."""

        text = "Container list.\n\n"
        text = text + "%-8s%-20s\n" % ("Index", "Name")
        for i in xrange(len(self)):
            text = text + "%-8i%-20s\n" % (i, self[i].element_name)
        return text


    def add_item(self):
        """Function for appending a new Element instance to the list."""

        self.append(Element())


    def from_xml(self, container_list_super_node):
        """Recreate the container list data structure from the XML container list node.

        @param container_list_super_node:     The container list XML nodes.
        @type container_list_super_node:      xml.dom.minicompat.Element instance
        """

        # Recreate all the container list data structures.
        xml_to_object(container_list_super_node, self, blacklist=[self.container_name])

        # Get the individual containers.
        container_list_nodes = container_list_super_node.getElementsByTagName(self.container_name)

        # Loop over the child nodes.
        for container_node in container_nodes:
            # Add the container list data container.
            self.add_item(container_node.getAttribute('name'))

            # Recreate all the other data structures.
            xml_to_object(container_node, self[-1])


    def to_xml(self, doc, element):
        """Create an XML element for the container list.

        The variables self.container_name and self.container_desc must exist.


        @param doc:     The XML document object.
        @type doc:      xml.dom.minidom.Document instance
        @param element: The element to add the container list XML element to.
        @type element:  XML element object
        """

        # Create the container list element and add it to the higher level element.
        container_list_element = doc.createElement(self.container_name)
        element.appendChild(container_list_element)

        # Set the container list attributes.
        container_list_element.setAttribute('desc', self.container_desc)

        # Blacklist.
        blacklist = ['container_name', 'container_desc'] + list(ListType.__dict__.keys()) + list(ContainerList.__dict__.keys()) + list(self.__class__.__dict__.keys())
        if hasattr(self, 'blacklist'):
            blacklist = blacklist + self.blacklist + ['blacklist']

        # Add all simple python objects.
        fill_object_contents(doc, container_list_element, object=self, blacklist=blacklist)

        # Loop over the elements.
        for i in xrange(len(self)):
            # Add the element.
            self[i].to_xml(doc, container_list_element)
